import uuid
from html import escape
from urllib.parse import quote

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

import storage
from db import connect
from texts import texts

app = FastAPI(title='FastAPI on Master da Web')

MAX = 10 * 1024 * 1024


def probe(fn):
    try:
        return {'ok': True, 'detail': fn()}
    except Exception as e:  # each part reports its own failure
        return {'ok': False, 'detail': (str(e).splitlines() or [type(e).__name__])[0][:160]}


def database():
    with connect() as conn:
        return ' '.join(conn.execute('select version()').fetchone()[0].split()[:2])


def checks():
    return {'database': probe(database), 'storage': probe(storage.check)}


def files():
    with connect() as conn:
        rows = conn.execute('SELECT id, object_key, name, size, created_at FROM files ORDER BY id DESC LIMIT 20').fetchall()
    return [
        {'id': r[0], 'name': r[2], 'size': r[3], 'created_at': r[4].isoformat(), 'url': storage.signed_link(r[1], r[2])}
        for r in rows
    ]


@app.get('/health')
def health():
    """The platform's health check: the process is up."""
    return {'ok': True}


@app.get('/status.json')
def status():
    c = checks()
    ok = all(v['ok'] for v in c.values())
    return JSONResponse({'ok': ok, 'checks': c}, status_code=200 if ok else 503)


@app.get('/files')
def list_files():
    return {'files': files()}


@app.post('/files', status_code=201)
async def upload(request: Request, file: UploadFile = File(...)):
    """A file to the bucket, its row to PostgreSQL. JSON for API calls, back to the page for the form."""
    from_form = 'text/html' in request.headers.get('accept', '')
    body = await file.read()
    if not body:
        return RedirectResponse('/?error=empty', 303) if from_form else JSONResponse({'error': 'The file is empty.'}, 400)
    if len(body) > MAX:
        return RedirectResponse('/?error=failed', 303) if from_form else JSONResponse({'error': 'Up to 10 MB.'}, 413)
    key = f'files/{uuid.uuid4()}'
    name = file.filename or 'file'
    content_type = file.content_type or 'application/octet-stream'
    try:
        storage.put(key, body, content_type)
        with connect() as conn:
            row = conn.execute(
                'INSERT INTO files (object_key, name, size, content_type) VALUES (%s, %s, %s, %s) RETURNING id',
                (key, name, len(body), content_type),
            ).fetchone()
    except Exception as e:
        print(f'upload failed: {e}', flush=True)
        if from_form:
            return RedirectResponse('/?error=failed', 303)
        raise
    if from_form:
        return RedirectResponse(f'/?sent={quote(name)}', 303)
    return {'id': row[0], 'name': name, 'url': storage.signed_link(key, name)}


STYLE = """
:root { --bg: #f7f7f8; --card: #fff; --text: #18181b; --muted: #71717a; --line: #e4e4e7; --ok: #16a34a; --bad: #dc2626; --accent: #00796b; --on-accent: #fff; }
@media (prefers-color-scheme: dark) { :root { --bg: #0f0f11; --card: #18181b; --text: #f4f4f5; --muted: #a1a1aa; --line: #27272a; --accent: #2dd4bf; --on-accent: #042f2e; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 40px 16px 64px; }
.brand { color: var(--muted); font-size: 13px; letter-spacing: .02em; }
h1 { font-size: 30px; line-height: 1.2; margin: 6px 0 8px; }
h2 { font-size: 17px; margin: 0 0 14px; }
.lead { color: var(--muted); margin: 0 0 28px; max-width: 640px; }
.muted { color: var(--muted); margin: 14px 0 0; } .muted a { color: inherit; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
.checks, .files { list-style: none; padding: 0; margin: 0; }
.checks li, .files li { display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: baseline; padding: 8px 0; border-top: 1px solid var(--line); }
.checks li:first-child, .files li:first-child { border-top: 0; }
.files { margin-top: 16px; } .files a { color: inherit; font-weight: 600; } .files span { color: var(--muted); font-size: 13px; }
.dot { width: 9px; height: 9px; border-radius: 50%; flex: none; transform: translateY(-1px); }
.dot.ok { background: var(--ok); } .dot.bad { background: var(--bad); }
.name { font-weight: 600; min-width: 150px; }
.detail { color: var(--muted); overflow-wrap: anywhere; } .detail.bad { color: var(--bad); }
form { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
input[type=file] { flex: 1 1 260px; color: var(--muted); }
button { background: var(--accent); color: var(--on-accent); border: 0; border-radius: 8px; padding: 9px 16px; font: inherit; font-weight: 600; cursor: pointer; }
.note { margin: 12px 0 0; padding: 10px 12px; border-radius: 8px; font-size: 14px; }
.note.ok { background: color-mix(in srgb, var(--ok) 12%, transparent); }
.note.bad { background: color-mix(in srgb, var(--bad) 12%, transparent); color: var(--bad); }
ol { margin: 0; padding-left: 20px; } ol li { margin: 6px 0; }
footer { color: var(--muted); font-size: 13px; margin-top: 24px; } footer a { color: inherit; }
"""


def size(n: int) -> str:
    return f'{n / 1048576:.1f} MB' if n >= 1048576 else f'{max(1, round(n / 1024))} KB'


@app.get('/', response_class=HTMLResponse)
def home(request: Request, sent: str | None = None, error: str | None = None):
    lang, t = texts(request.headers.get('accept-language'))
    c = checks()
    listed = files() if c['database']['ok'] and c['storage']['ok'] else []
    labels = {'database': 'PostgreSQL', 'storage': 'Object Storage'}
    rows = '\n'.join(
        f'<li data-check="{k}" data-ok="{str(v["ok"]).lower()}"><span class="dot {"ok" if v["ok"] else "bad"}"></span>'
        f'<span class="name">{labels[k]}</span><span class="detail {"" if v["ok"] else "bad"}">{escape(v["detail"])}</span></li>'
        for k, v in c.items()
    )
    note = ''
    if sent:
        note = f'<p class="note ok" role="status">{escape(t["sent"].format(name=sent))}</p>'
    elif error:
        note = f'<p class="note bad" role="alert">{escape(t["empty"] if error == "empty" else t["failed"])}</p>'
    items = (
        '<ul class="files" data-testid="uploads">'
        + ''.join(f'<li><a href="{escape(f["url"])}">{escape(f["name"])}</a><span>{size(f["size"])} · {escape(t["download"])}</span></li>' for f in listed)
        + '</ul>'
        if listed
        else f'<p class="muted">{escape(t["none"])}</p>'
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FastAPI · Master da Web</title><style>{STYLE}</style></head>
<body><main>
<div class="brand">Python · FastAPI · Master da Web</div>
<h1>{escape(t['title'])}</h1>
<p class="lead">{escape(t['lead'])}</p>
<section><h2>{escape(t['reaches'])}</h2><ul class="checks" data-testid="checks">{rows}</ul></section>
<section><h2>{escape(t['send'])}</h2>
<form method="post" action="/files" enctype="multipart/form-data"><input type="file" name="file" required aria-label="{escape(t['file'])}"><button type="submit">{escape(t['submit'])}</button></form>
{note}
{items}
<p class="muted"><a href="/docs">/docs</a> — {escape(t['docs'])}</p>
</section>
<section><h2>{escape(t['next'])}</h2><ol><li>{escape(t['step1'])}</li><li>{escape(t['step2'])}</li><li>{escape(t['step3'])}</li></ol></section>
<footer><a href="/status.json">status.json</a></footer>
</main></body></html>"""
