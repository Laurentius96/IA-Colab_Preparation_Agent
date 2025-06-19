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

def main():
  """Função principal que orquestra todo o processo."""
  service = authenticate()
  if not service:
      return

  # 1. Obter o ID do notebook do Google Colab
  notebook_link = input("Cole o link completo do seu Google Colab Notebook: ")
  
  # Verifica qual formato de URL foi usado e extrai o ID corretamente
  notebook_id = None
  
  if '/d/' in notebook_link:
      try:
          notebook_id = notebook_link.split('/d/')[1].split('/')[0]
      except IndexError:
          pass
  elif '/drive/' in notebook_link:
      try:
          # Para URLs do tipo: https://colab.research.google.com/drive/ID
          notebook_id = notebook_link.split('/drive/')[1].split('/')[0].split('#')[0].split('?')[0]
      except IndexError:
          pass
  
  # Se não conseguiu extrair o ID, tenta outros padrões comuns
  if not notebook_id:
      # Tenta extrair usando regex para capturar IDs do Google Drive
      import re
      id_pattern = r'[a-zA-Z0-9_-]{25,}'
      matches = re.findall(id_pattern, notebook_link)
      if matches:
          # Pega o primeiro match que parece ser um ID válido do Google Drive
          for match in matches:
              if len(match) >= 25:  # IDs do Google Drive geralmente têm pelo menos 25 caracteres
                  notebook_id = match
                  break
  
  if not notebook_id:
      print("Erro: Não foi possível extrair o ID do notebook do link fornecido.")
      print("Certifique-se de que você copiou o link completo do Google Colab.")
      return  # Agora o return está corretamente indentado

  print(f"ID do Notebook identificado: {notebook_id}")
      
  # 2. Obter a saída do Professor Synapse
  print("\n---")
  print("Agora, cole a aula completa do Professor Synapse. Pressione Ctrl+D (Linux/Mac) ou Ctrl+Z e Enter (Windows) quando terminar:")
  synapse_output = ""
  while True:
      try:
          line = input()
          synapse_output += line + '\n'
      except EOFError:
          break
          
  if not synapse_output.strip():
      print("Nenhum conteúdo foi colado. Abortando.")
      return
      
  # 3. Parsear o conteúdo e criar a estrutura do notebook
  parsed_cells = parse_synapse_output(synapse_output)
  if not parsed_cells:
      print("Não foi possível encontrar blocos de código/markdown no formato esperado.")
      return
      
  new_notebook_content = create_notebook_structure(parsed_cells)
  
  # 4. Salvar o conteúdo em um arquivo temporário
  temp_filename = 'temp_notebook.ipynb'
  with open(temp_filename, 'w', encoding='utf-8') as f:
      f.write(new_notebook_content)
      
  # 5. Fazer o upload e substituir o arquivo no Google Drive
  print("\n---")
  confirm = input(f"Você tem CERTEZA que deseja substituir o conteúdo do notebook com ID '{notebook_id}'? (s/n): ")
  if confirm.lower() == 's':
      try:
          media = MediaFileUpload(temp_filename, mimetype='application/vnd.google-colaboratory')
          service.files().update(
              fileId=notebook_id,
              media_body=media
          ).execute()
          print("\n✅ Sucesso! O seu notebook no Google Colab foi atualizado com a aula.")
          print("Pode ser necessário recarregar a página do Colab para ver as mudanças.")
      except HttpError as error:
          print(f"Ocorreu um erro ao atualizar o arquivo: {error}")
      finally:
          os.remove(temp_filename) # Limpa o arquivo temporário
  else:
      print("Operação cancelada pelo usuário.")
      os.remove(temp_filename)