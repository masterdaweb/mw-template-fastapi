"""
PostgreSQL from the binding, as libpq reads it: PGHOST, PGPORT, PGDATABASE,
PGUSER, PGPASSWORD and PGSSLMODE. psycopg needs nothing more than connect().
The app goes through the pooler; the release (migrate.py) gets the server
itself, from the same names.
"""
import os

import psycopg


def connect():
    if not os.environ.get('PGHOST'):
        raise RuntimeError('PGHOST is empty: connect a database to this service')
    return psycopg.connect(connect_timeout=5)
