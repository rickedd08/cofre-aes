# Cofre de Senhas Corporativo — AES-GCM

Projeto de laboratório de Criptografia Aplicada — Módulo 3.

## Equipe

- Integrante 1: Erick Eduardo
- Integrante 2: Thales


## Objetivo

Construir uma API funcional de cofre de senhas corporativo. As senhas persistidas são protegidas com AES-256-GCM. A senha-mestra não é armazenada; ela é transformada em uma chave de 32 bytes por PBKDF2 com HMAC-SHA-256.

## Tecnologias

- Python 3.10+
- FastAPI
- PyCryptodome
- Supabase / PostgreSQL
- Pydantic
- python-dotenv

## Estrutura

```text
cofre-aes/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── cripto.py
│   ├── banco.py
│   └── modelos.py
├── sql/
│   └── esquema.sql
├── testes/
│   ├── resultados.md
│   └── evidencias/
├── .env.exemplo
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalação

```powershell
python --version
mkdir cofre-aes
cd cofre-aes
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Supabase

1. Criar um projeto próprio da equipe no Supabase.
2. Abrir o SQL Editor.
3. Executar integralmente `sql/esquema.sql`.
4. Obter a URL do projeto e a chave pública `anon`/`publishable`.
5. Criar `.env` na raiz, sem publicar o arquivo:

```env
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_KEY=sua_chave_publica
```

O `.env` está bloqueado pelo `.gitignore`.

## Execução

Com o ambiente virtual ativo:

```powershell
uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

## Rotas

| Método | Rota | Função |
|---|---|---|
| POST | `/cofres` | cria um cofre |
| POST | `/cofres/{id}/abrir` | valida a senha-mestra |
| POST | `/cofres/{id}/segredos` | cria e cifra um segredo |
| GET | `/cofres/{id}/segredos` | lista metadados sem senhas |
| GET | `/cofres/{id}/segredos/{sid}` | decifra um segredo |
| PUT | `/cofres/{id}/segredos/{sid}` | troca a senha com novo nonce |
| DELETE | `/cofres/{id}/segredos/{sid}` | remove o segredo |

Com exceção da criação do cofre, as rotas usam o cabeçalho:

```text
X-Senha-Mestra: sua-senha
```

### Exemplo: criar cofre

Requisição:

```http
POST /cofres
Content-Type: application/json

{
  "nome": "Equipe 01",
  "senha_mestra": "senha-mestra-de-teste"
}
```

Resposta:

```json
{
  "id": "uuid-do-cofre"
}
```

### Exemplo: criar segredo

```http
POST /cofres/{id}/segredos
X-Senha-Mestra: senha-mestra-de-teste
Content-Type: application/json

{
  "titulo": "Banco de produção",
  "usuario": "admin",
  "url": "https://exemplo.local",
  "senha": "S3nh@-forte"
}
```

Resposta:

```json
{
  "id": "uuid-do-segredo"
}
```

### Exemplo: leitura

```http
GET /cofres/{id}/segredos/{sid}
X-Senha-Mestra: senha-mestra-de-teste
```

Resposta:

```json
{
  "id": "uuid-do-segredo",
  "titulo": "Banco de produção",
  "usuario": "admin",
  "url": "https://exemplo.local",
  "senha": "S3nh@-forte"
}
```

A rota de listagem não retorna `nonce`, `criptograma` ou `etiqueta`.

## Justificativa criptográfica

### PBKDF2

- HMAC-SHA-256
- 210.000 iterações
- chave derivada de 32 bytes
- sal aleatório de 16 bytes por cofre
- número de iterações armazenado no banco

O sal não é secreto e permite que cofres diferentes produzam chaves diferentes mesmo quando a senha-mestra coincidir.

### AES-256-GCM

Cada cifragem gera:

- nonce aleatório de 12 bytes;
- criptograma;
- etiqueta de autenticação de 16 bytes.

O nonce nunca é reutilizado. Atualizações geram um novo nonce.

### AAD

Para cada segredo:

```text
cofre_id|segredo_id
```

Esse valor é autenticado pelo GCM sem ser cifrado. Assim, um criptograma copiado de um registro para outro falha na verificação da etiqueta.

## O que fica armazenado

- sal;
- número de iterações;
- nonce, criptograma e etiqueta;
- verificador do cofre;
- título, usuário e URL.

## O que nunca é armazenado

- senha-mestra;
- chave derivada;
- senhas em texto claro;
- registros de senhas digitadas.

## Limitações

O sistema protege contra cópia integral do banco, consulta direta e adulteração dos registros. Ele não protege contra comprometimento do servidor de aplicação durante o uso, porque a senha-mestra passa pela memória do servidor. Também não resolve o problema de uma senha-mestra fraca ou divulgada pela equipe.

Auditoria de qual usuário acessou qual segredo não faz parte do escopo.

Título, usuário e URL permanecem em texto claro por decisão do projeto, portanto alguém com acesso ao banco consegue identificar quais sistemas são utilizados, mesmo sem conhecer as senhas.

## Testes obrigatórios

Os cinco testes definidos no roteiro do projeto estão em `testes/resultados.md`. As capturas reais devem ser colocadas em `testes/evidencias/` depois da execução.

## Segurança do repositório

Nunca faça commit do `.env`. Antes do primeiro `git add .`, confira:

```powershell
git status
```

O arquivo `.env` não pode aparecer.

## Referências

- DWORKIN, M. NIST SP 800-38D — Galois/Counter Mode.
- TURAN, M. S.; BARKER, E.; BURR, W.; CHEN, L. NIST SP 800-132 — Password-Based Key Derivation.
- OWASP. Password Storage Cheat Sheet.
- FERGUSON, N.; SCHNEIER, B.; KOHNO, T. Cryptography Engineering.
- PyCryptodome Documentation.
- FastAPI Documentation.
