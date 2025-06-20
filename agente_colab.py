# ======================
# Imports e Dependências
# ======================
import os
import re
import json
import sys
import argparse
import tempfile
import logging
from pathlib import Path
from typing import List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ====================
# Configurações Globais
# ====================
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS = Path('credentials/client_secrets.json')
TOKEN_FILE = Path('credentials/token.json')
LOG_FILE = Path('logs/agent_colab.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================
# Funções de Autenticação Drive
# ============================
def check_credentials() -> bool:
    """Verifica existência do arquivo de credenciais"""
    if not CREDENTIALS.exists():
        logger.error(f"Credenciais não encontradas: {CREDENTIALS}")
        return False
    return True


def authenticate() -> 'Resource':
    """Autentica no Google Drive e retorna o serviço API"""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return build('drive', 'v3', credentials=creds)


# =================================
# Função para extrair ID de notebook
# =================================
def extract_notebook_id(url: str) -> str:
    """Extrai o ID do notebook a partir da URL do Colab"""
    patterns = [r'/d/([^/]+)', r'/drive/([^/?#]+)']
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    # fallback genérico para IDs longos
    ids = re.findall(r'[A-Za-z0-9_-]{25,}', url)
    return ids[0] if ids else ''


# ===================
# Parser Synapse → células
# ===================
def parse_synapse(text: str) -> List[Dict[str, str]]:
    """Converte texto do Synapse em lista de células para notebook"""
    pattern = re.compile(
        r'```markdown\n(.*?)\n```|▶️.*?```python\n(.*?)\n```|📖.*?```markdown\n(.*?)\n```',
        re.DOTALL
    )
    cells = []
    for md, code, read in pattern.findall(text):
        if md:
            cells.append({'type': 'markdown', 'content': md.strip()})
        if code:
            cells.append({'type': 'code', 'content': code.strip()})
            cells.append({'type': 'code', 'content': '# Pratique aqui'})
        if read:
            cells.append({'type': 'markdown', 'content': read.strip()})
    return cells


# =============================
# Montagem do JSON do Notebook
# =============================
def build_notebook(cells: List[Dict[str, str]]) -> str:
    """Gera string JSON de um notebook .ipynb a partir das células"""
    nb = {'nbformat': 4, 'nbformat_minor': 0, 'metadata': {}, 'cells': []}
    for c in cells:
        entry = {
            'markdown': {
                'cell_type': 'markdown', 'metadata': {},
                'source': [line + '\n' for line in c['content'].split('\n')]
            },
            'code': {
                'cell_type': 'code', 'metadata': {}, 'execution_count': None,
                'outputs': [],
                'source': [line + '\n' for line in c['content'].split('\n')]
            }
        }[c['type']]
        nb['cells'].append(entry)
    return json.dumps(nb, indent=2)


# =================
# Upload para Drive
# =================
def upload_notebook(service, notebook_id: str, notebook_content: str) -> None:
    """Salva notebook temporário e faz upload/substituição no Drive"""
    with tempfile.NamedTemporaryFile('w', suffix='.ipynb', delete=False) as tmp:
        tmp.write(notebook_content)
        tmp_path = tmp.name
    media = MediaFileUpload(tmp_path, mimetype='application/vnd.google-colaboratory')
    service.files().update(fileId=notebook_id, media_body=media).execute()
    os.remove(tmp_path)
    logger.info(f"Notebook {notebook_id} atualizado com sucesso.")


# ===========================
# Função Principal (CLI entry)
# ===========================
def main():
    parser = argparse.ArgumentParser(
        description="Agente CLI: parser Synapse + Colab Drive"
    )
    parser.add_argument('--url', '-u', required=True, help='URL do notebook Colab')
    parser.add_argument('--input', '-i', help='Arquivo com saída do Synapse (ou STDIN)')
    args = parser.parse_args()

    if not check_credentials():
        parser.exit(1)

    service = authenticate()
    notebook_id = extract_notebook_id(args.url)
    if not notebook_id:
        logger.error("Não foi possível extrair o ID do notebook.")
        parser.exit(1)

    if args.input:
        text = Path(args.input).read_text(encoding='utf-8')
    else:
        logger.info("Aguardando stdin do Synapse (CTRL+D para terminar)...")
        text = sys.stdin.read()

    cells = parse_synapse(text)
    if not cells:
        logger.error("Parser não encontrou blocos válidos.")
        parser.exit(1)

    nb_content = build_notebook(cells)
    upload_notebook(service, notebook_id, nb_content)


# ==========
# EntryPoint
# ==========
if __name__ == '__main__':
    main()