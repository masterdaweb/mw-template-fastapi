"""The page in the visitor's language: Portuguese when the browser prefers it."""

EN = {
    'title': 'Your FastAPI API is live',
    'lead': 'Python with PostgreSQL and a private bucket: files sent below go to the bucket, their rows to the database, and they come back through links that expire in 15 minutes.',
    'reaches': 'What this API reaches',
    'send': 'Send a file',
    'file': 'File',
    'submit': 'Send to Object Storage',
    'sent': '{name} was saved.',
    'empty': 'Choose a file first.',
    'failed': 'The file could not be saved. See the service logs.',
    'none': 'No files yet.',
    'download': 'download (link valid for 15 min)',
    'docs': 'Interactive API docs',
    'next': 'Next steps',
    'step1': 'Make the code yours: in the console, open this project and follow “Your code” to copy it to your GitHub and connect it.',
    'step2': 'Add a route in main.py and a step in migrate.py, then push: the migration runs once, before the new version takes traffic.',
    'step3': 'Add your own domain on the api service, under Domains.',
}

PT = {
    'title': 'Sua API FastAPI está no ar',
    'lead': 'Python com PostgreSQL e um bucket privado: os arquivos enviados abaixo vão para o bucket, as linhas deles para o banco, e voltam por links que expiram em 15 minutos.',
    'reaches': 'O que esta API alcança',
    'send': 'Envie um arquivo',
    'file': 'Arquivo',
    'submit': 'Enviar para o Object Storage',
    'sent': '{name} foi salvo.',
    'empty': 'Escolha um arquivo primeiro.',
    'failed': 'Não foi possível salvar o arquivo. Veja os logs do serviço.',
    'none': 'Nenhum arquivo ainda.',
    'download': 'baixar (link válido por 15 min)',
    'docs': 'Documentação interativa da API',
    'next': 'Próximos passos',
    'step1': 'Torne o código seu: no console, abra este projeto e siga “Seu código” para copiá-lo para o seu GitHub e conectá-lo.',
    'step2': 'Crie uma rota em main.py e um passo em migrate.py e faça push: a migração roda uma vez, antes de a nova versão receber tráfego.',
    'step3': 'Adicione o seu domínio no serviço api, em Domínios.',
}


def texts(accept_language: str | None) -> tuple[str, dict]:
    first = (accept_language or '').split(',')[0].strip().lower()
    return ('pt-BR', PT) if first.startswith('pt') else ('en', EN)
