from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException

from . import banco, cripto
from .modelos import AtualizaSegredo, NovoCofre, NovoSegredo

app = FastAPI(
    title="Cofre de Senhas",
    description="API didática de cofre corporativo com PBKDF2 e AES-256-GCM.",
    version="1.0.0",
)


def obter_cofre_ou_404(cofre_id: str):
    cofre = banco.buscar_cofre(cofre_id)
    if not cofre:
        raise HTTPException(status_code=404, detail="cofre não encontrado")
    return cofre


def autenticar_cofre(cofre: dict, senha_mestra: str) -> bytes:
    chave = cripto.derivar_chave(
        senha_mestra,
        cripto.de_b64(cofre["kdf_sal"]),
        int(cofre["kdf_iteracoes"]),
    )
    correta = cripto.senha_mestra_correta(
        chave,
        cofre["verificador_nonce"],
        cofre["verificador_criptograma"],
        cofre["verificador_etiqueta"],
        cofre["id"],
    )
    if not correta:
        raise HTTPException(status_code=401, detail="senha-mestra incorreta")
    return chave


@app.post("/cofres", status_code=201)
def criar_cofre(dados: NovoCofre):
    cofre_id = str(uuid4())
    sal = cripto.gerar_sal()
    chave = cripto.derivar_chave(
        dados.senha_mestra,
        sal,
        cripto.ITERACOES_PADRAO,
    )
    nonce, criptograma, etiqueta = cripto.criar_verificador(chave, cofre_id)

    banco.inserir_cofre(
        {
            "id": cofre_id,
            "nome": dados.nome,
            "kdf_sal": cripto.para_b64(sal),
            "kdf_iteracoes": cripto.ITERACOES_PADRAO,
            "verificador_nonce": nonce,
            "verificador_criptograma": criptograma,
            "verificador_etiqueta": etiqueta,
        }
    )
    return {"id": cofre_id}


@app.post("/cofres/{cofre_id}/abrir")
def abrir_cofre(
    cofre_id: str,
    x_senha_mestra: str = Header(...),
):
    cofre = obter_cofre_ou_404(cofre_id)
    autenticar_cofre(cofre, x_senha_mestra)
    return {"mensagem": "cofre aberto"}


@app.post("/cofres/{cofre_id}/segredos", status_code=201)
def criar_segredo(
    cofre_id: str,
    dados: NovoSegredo,
    x_senha_mestra: str = Header(...),
):
    cofre = obter_cofre_ou_404(cofre_id)
    chave = autenticar_cofre(cofre, x_senha_mestra)

    segredo_id = str(uuid4())
    aad = cripto.montar_aad(cofre_id, segredo_id)
    nonce, criptograma, etiqueta = cripto.cifrar(chave, dados.senha, aad)

    banco.inserir_segredo(
        {
            "id": segredo_id,
            "cofre_id": cofre_id,
            "titulo": dados.titulo,
            "usuario": dados.usuario,
            "url": dados.url,
            "nonce": nonce,
            "criptograma": criptograma,
            "etiqueta": etiqueta,
        }
    )
    return {"id": segredo_id}


@app.get("/cofres/{cofre_id}/segredos")
def listar_segredos(
    cofre_id: str,
    x_senha_mestra: str = Header(...),
):
    cofre = obter_cofre_ou_404(cofre_id)
    autenticar_cofre(cofre, x_senha_mestra)
    return banco.listar_segredos(cofre_id)


@app.get("/cofres/{cofre_id}/segredos/{segredo_id}")
def ler_segredo(
    cofre_id: str,
    segredo_id: str,
    x_senha_mestra: str = Header(...),
):
    cofre = obter_cofre_ou_404(cofre_id)
    chave = autenticar_cofre(cofre, x_senha_mestra)

    segredo = banco.buscar_segredo(cofre_id, segredo_id)
    if not segredo:
        raise HTTPException(status_code=404, detail="segredo não encontrado")

    aad = cripto.montar_aad(cofre_id, segredo_id)

    try:
        senha = cripto.decifrar(
            chave,
            segredo["nonce"],
            segredo["criptograma"],
            segredo["etiqueta"],
            aad,
        )
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=500, detail="registro adulterado")

    return {
        "id": segredo["id"],
        "titulo": segredo["titulo"],
        "usuario": segredo["usuario"],
        "url": segredo["url"],
        "senha": senha,
    }


@app.put("/cofres/{cofre_id}/segredos/{segredo_id}")
def atualizar_segredo(
    cofre_id: str,
    segredo_id: str,
    dados: AtualizaSegredo,
    x_senha_mestra: str = Header(...),
):
    cofre = obter_cofre_ou_404(cofre_id)
    chave = autenticar_cofre(cofre, x_senha_mestra)

    segredo = banco.buscar_segredo(cofre_id, segredo_id)
    if not segredo:
        raise HTTPException(status_code=404, detail="segredo não encontrado")

    aad = cripto.montar_aad(cofre_id, segredo_id)
    nonce, criptograma, etiqueta = cripto.cifrar(chave, dados.senha, aad)

    atualizados = {
        "nonce": nonce,
        "criptograma": criptograma,
        "etiqueta": etiqueta,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }

    if dados.titulo is not None:
        atualizados["titulo"] = dados.titulo
    if dados.usuario is not None:
        atualizados["usuario"] = dados.usuario
    if dados.url is not None:
        atualizados["url"] = dados.url

    banco.atualizar_segredo(segredo_id, atualizados)

    return {"mensagem": "segredo atualizado", "id": segredo_id}


@app.delete("/cofres/{cofre_id}/segredos/{segredo_id}")
def deletar_segredo(
    cofre_id: str,
    segredo_id: str,
    x_senha_mestra: str = Header(...),
):
    cofre = obter_cofre_ou_404(cofre_id)
    autenticar_cofre(cofre, x_senha_mestra)

    segredo = banco.buscar_segredo(cofre_id, segredo_id)
    if not segredo:
        raise HTTPException(status_code=404, detail="segredo não encontrado")

    banco.remover_segredo(segredo_id)
    return {"mensagem": "segredo removido"}
