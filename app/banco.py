import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_url = os.environ.get("SUPABASE_URL")
_key = os.environ.get("SUPABASE_KEY")

if not _url or not _key:
    raise RuntimeError(
        "SUPABASE_URL e SUPABASE_KEY precisam estar definidos no arquivo .env"
    )

supabase: Client = create_client(_url, _key)


def inserir_cofre(cofre: dict):
    return supabase.table("cofres").insert(cofre).execute()


def buscar_cofre(cofre_id: str):
    resposta = (
        supabase.table("cofres")
        .select("*")
        .eq("id", cofre_id)
        .execute()
    )
    return resposta.data[0] if resposta.data else None


def inserir_segredo(segredo: dict):
    return supabase.table("segredos").insert(segredo).execute()


def listar_segredos(cofre_id: str):
    resposta = (
        supabase.table("segredos")
        .select("id, titulo, usuario, url, criado_em, atualizado_em")
        .eq("cofre_id", cofre_id)
        .execute()
    )
    return resposta.data


def buscar_segredo(cofre_id: str, segredo_id: str):
    resposta = (
        supabase.table("segredos")
        .select("*")
        .eq("cofre_id", cofre_id)
        .eq("id", segredo_id)
        .execute()
    )
    return resposta.data[0] if resposta.data else None


def atualizar_segredo(segredo_id: str, dados: dict):
    return (
        supabase.table("segredos")
        .update(dados)
        .eq("id", segredo_id)
        .execute()
    )


def remover_segredo(segredo_id: str):
    return (
        supabase.table("segredos")
        .delete()
        .eq("id", segredo_id)
        .execute()
    )
