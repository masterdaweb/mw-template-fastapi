# FastAPI na Master da Web

Uma API em Python com FastAPI, PostgreSQL e arquivos privados no Object Storage.

| Serviço | O que roda |
| --- | --- |
| `api` | Uvicorn; `python migrate.py` roda uma vez por deploy |

O banco chega com os nomes que o libpq lê (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGSSLMODE`): o psycopg conecta sem configuração. O bucket privado chega como `MW_STORAGE_*`, e cada link de download é assinado e expira em 15 minutos.

`POST /files` guarda um arquivo; `GET /files` lista com os links; `/docs` é a documentação interativa.

## Torne o código seu

1. No console, abra o projeto e siga **Seu código**: copie este template
   para o seu GitHub e conecte a cópia ao projeto.
2. Altere `main.py` e `migrate.py` e faça push: cada push faz um deploy, sem tirar o
   app do ar.

## Rodar na sua máquina

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export $(grep -v ^# .env.example | xargs)
python migrate.py && uvicorn main:app --reload
```

*[English](README.en.md)*
