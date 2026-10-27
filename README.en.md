# FastAPI on Master da Web

A Python API with FastAPI, PostgreSQL and private files on Object Storage.

| Service | What it runs |
| --- | --- |
| `api` | Uvicorn; `python migrate.py` runs once per deploy |

The database comes with the names libpq reads (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGSSLMODE`): psycopg connects with no configuration. The private bucket comes as `MW_STORAGE_*`, and each download link is signed and expires in 15 minutes.

`POST /files` stores a file; `GET /files` lists them with their links; `/docs` is the interactive documentation.

## Make it yours

1. In the console, open the project and follow **Your code**: copy this
   template to your GitHub and connect the copy to the project.
2. Change `main.py` and `migrate.py`, then push: every push deploys, with no downtime.

## Run it on your machine

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export $(grep -v ^# .env.example | xargs)
python migrate.py && uvicorn main:app --reload
```

*[Português](README.md)*
