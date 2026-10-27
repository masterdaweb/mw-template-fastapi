"""The release command (`python migrate.py`): once per deploy, before the
new version takes traffic. A failure stops the deploy; the old one stays."""
from db import connect

STEPS = [
    (
        '001_files',
        """
        CREATE TABLE files (
          id           bigserial PRIMARY KEY,
          object_key   text        NOT NULL UNIQUE,
          name         text        NOT NULL,
          size         bigint      NOT NULL,
          content_type text        NOT NULL,
          created_at   timestamptz NOT NULL DEFAULT now()
        )
        """,
    ),
]

with connect() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY, ran_at timestamptz NOT NULL DEFAULT now())')
    done = {r[0] for r in conn.execute('SELECT name FROM schema_migrations')}
    for name, sql in STEPS:
        if name in done:
            continue
        with conn.transaction():
            conn.execute(sql)
            conn.execute('INSERT INTO schema_migrations (name) VALUES (%s)', (name,))
        print(f'migrated {name}')
print('migrations up to date')
