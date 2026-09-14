# Resultados dos testes obrigatórios

> Este arquivo é o modelo de registro. As evidências abaixo devem ser preenchidas após executar a API com o Supabase da equipe. Não foram inventadas evidências de execução.

## Teste 1 — Nonces distintos

**Procedimento:** cadastrar duas vezes a mesma senha, com títulos diferentes, no mesmo cofre, e consultar `public.segredos`.

**Resultado esperado:** `nonce` e `criptograma` diferentes nos dois registros.

**Resultado observado:** preencher após a execução.

**Evidência:** colocar a captura em `testes/evidencias/01-nonces.png`.

## Teste 2 — Senha-mestra incorreta

**Procedimento:** solicitar a leitura de um segredo usando senha-mestra incorreta.

**Resultado esperado:** HTTP 401 e nenhum conteúdo do segredo na resposta.

**Resultado observado:** preencher após a execução.

**Evidência:** `testes/evidencias/02-senha-incorreta.png`.

## Teste 3 — O que o invasor enxerga

Executar no SQL Editor:

```sql
select titulo, usuario, nonce, criptograma, etiqueta
from public.segredos;
```

**Resultado esperado:** somente metadados e cadeias Base64; nenhuma senha legível.

**Resultado observado:** preencher após a execução.

**Evidência:** `testes/evidencias/03-banco.png`.

## Teste 4 — Registro adulterado

No Supabase, altere um caractere do criptograma:

```sql
update public.segredos
set criptograma = 'X' || substring(criptograma from 2)
where id = 'COLOQUE-AQUI-O-ID-DO-SEGREDO';
```

Depois tente ler o segredo pela API.

**Resultado esperado:** HTTP 500 com `registro adulterado`, sem texto claro.

**Resultado observado:** preencher após a execução.

**Evidência:** `testes/evidencias/04-adulteracao.png`.

## Teste 5 — Troca de criptogramas entre registros

Copiar `nonce`, `criptograma` e `etiqueta` de um segredo para outro e tentar ler o destino.

**Resultado esperado:** HTTP 500. O AAD contém `cofre_id|segredo_id`, impedindo a reutilização do criptograma em outro registro.

**Resultado observado:** preencher após a execução.

**Evidência:** `testes/evidencias/05-aad.png`.
