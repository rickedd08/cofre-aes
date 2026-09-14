from pydantic import BaseModel, Field


class NovoCofre(BaseModel):
    nome: str = Field(min_length=1)
    senha_mestra: str = Field(min_length=1)


class NovoSegredo(BaseModel):
    titulo: str = Field(min_length=1)
    usuario: str | None = None
    url: str | None = None
    senha: str = Field(min_length=1)


class AtualizaSegredo(BaseModel):
    titulo: str | None = None
    usuario: str | None = None
    url: str | None = None
    senha: str = Field(min_length=1)
