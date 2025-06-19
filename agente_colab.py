import os
import re
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Escopos de permissão: Acesso total ao Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRETS_FILE = 'client_secrets.json'

def authenticate():
    """Lida com a autenticação do usuário e retorna o serviço da API."""
    creds = None
    # O arquivo token.json armazena os tokens de acesso e atualização do usuário.
    # Ele é criado automaticamente na primeira vez que você roda o script.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se não houver credenciais válidas, permite que o usuário faça login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva as credenciais para a próxima execução
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('drive', 'v3', credentials=creds)
        print("Autenticação com Google Drive bem-sucedida.")
        return service
    except HttpError as error:
        print(f"Ocorreu um erro ao construir o serviço da API: {error}")
        return None
    
def parse_synapse_output(text):
    """Analisa a saída do Professor Synapse e extrai células de código e markdown."""
    # Encontra todos os blocos de código Python
    code_blocks = re.findall(r"▶️.*?```python\n(.*?)\n```", text, re.DOTALL)
    # Encontra todos os blocos de markdown explicativos
    markdown_blocks = re.findall(r"📖.*?```markdown\n(.*?)\n```", text, re.DOTALL)
    
    # Intercala as células, começando pelo código
    cells = []
    num_pairs = min(len(code_blocks), len(markdown_blocks))
    for i in range(num_pairs):
        cells.append({'type': 'code', 'content': code_blocks[i]})
        # >>> AQUI ESTÁ A SUA FUNCIONALIDADE ESPECIAL <<<
        # Adiciona uma célula de código em branco para prática
        cells.append({'type': 'code', 'content': '# Pratique seu código aqui!'})
        cells.append({'type': 'markdown', 'content': markdown_blocks[i]})
        
    print(f"Foram encontradas e preparadas {len(cells)} células.")
    return cells    

def create_notebook_structure(cells_data):
    """Cria a estrutura JSON de um notebook .ipynb a partir dos dados das células."""
    notebook_cells = []
    for cell_item in cells_data:
        if cell_item['type'] == 'code':
            notebook_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + '\n' for line in cell_item['content'].split('\n')]
            })
        elif cell_item['type'] == 'markdown':
            notebook_cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + '\n' for line in cell_item['content'].split('\n')]
            })
            
    notebook_json = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": notebook_cells
    }
    return json.dumps(notebook_json, indent=2)
