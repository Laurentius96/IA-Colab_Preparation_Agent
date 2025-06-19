import os
import re
import json
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Escopos de permissão: Acesso total ao Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRETS_FILE = 'client_secrets.json'

def check_requirements():
    """Verifica se todos os arquivos necessários estão presentes."""
    print("🔍 Verificando arquivos necessários...")
    
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"❌ Arquivo '{CLIENT_SECRETS_FILE}' não encontrado!")
        print("   Você precisa baixar as credenciais do Google Cloud Console.")
        return False
    else:
        print(f"✅ Arquivo '{CLIENT_SECRETS_FILE}' encontrado.")
    
    return True

def authenticate():
    """Lida com a autenticação do usuário e retorna o serviço da API."""
    print("🔐 Iniciando processo de autenticação...")
    
    creds = None
    # O arquivo token.json armazena os tokens de acesso e atualização do usuário.
    if os.path.exists('token.json'):
        print("✅ Arquivo token.json encontrado. Carregando credenciais...")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se não houver credenciais válidas, permite que o usuário faça login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Atualizando credenciais expiradas...")
            creds.refresh(Request())
        else:
            print("🌐 Iniciando fluxo de autenticação no navegador...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva as credenciais para a próxima execução
        print("💾 Salvando credenciais...")
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('drive', 'v3', credentials=creds)
        print("✅ Autenticação com Google Drive bem-sucedida!")
        return service
    except HttpError as error:
        print(f"❌ Erro ao construir o serviço da API: {error}")
        return None

def parse_synapse_output(text):
    """Analisa a saída do Professor Synapse e extrai células de código e markdown."""
    print("📝 Analisando conteúdo do Professor Synapse...")
    
    # Encontra todos os blocos de código Python
    code_blocks = re.findall(r"▶️.*?```python\n(.*?)\n```", text, re.DOTALL)
    # Encontra todos os blocos de markdown explicativos
    markdown_blocks = re.findall(r"📖.*?```markdown\n(.*?)\n```", text, re.DOTALL)
    
    print(f"🔍 Encontrados {len(code_blocks)} blocos de código")
    print(f"🔍 Encontrados {len(markdown_blocks)} blocos de markdown")
    
    # Se não encontrou nada, tenta padrões alternativos
    if len(code_blocks) == 0:
        print("⚠️  Tentando padrões alternativos para código...")
        # Tenta sem emoji
        code_blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        print(f"🔍 Encontrados {len(code_blocks)} blocos de código (padrão alternativo)")
    
    if len(markdown_blocks) == 0:
        print("⚠️  Tentando padrões alternativos para markdown...")
        # Tenta sem emoji
        markdown_blocks = re.findall(r"```markdown\n(.*?)\n```", text, re.DOTALL)
        print(f"🔍 Encontrados {len(markdown_blocks)} blocos de markdown (padrão alternativo)")
    
    # Intercala as células, começando pelo código
    cells = []
    num_pairs = min(len(code_blocks), len(markdown_blocks))
    
    for i in range(num_pairs):
        cells.append({'type': 'code', 'content': code_blocks[i]})
        # Adiciona uma célula de código em branco para prática
        cells.append({'type': 'code', 'content': '# Pratique seu código aqui!'})
        cells.append({'type': 'markdown', 'content': markdown_blocks[i]})
    
    # Se sobrou código sem markdown correspondente
    if len(code_blocks) > len(markdown_blocks):
        for i in range(len(markdown_blocks), len(code_blocks)):
            cells.append({'type': 'code', 'content': code_blocks[i]})
            cells.append({'type': 'code', 'content': '# Pratique seu código aqui!'})
    
    # Se sobrou markdown sem código correspondente
    if len(markdown_blocks) > len(code_blocks):
        for i in range(len(code_blocks), len(markdown_blocks)):
            cells.append({'type': 'markdown', 'content': markdown_blocks[i]})
        
    print(f"✅ Foram preparadas {len(cells)} células no total.")
    return cells

def create_notebook_structure(cells_data):
    """Cria a estrutura JSON de um notebook .ipynb a partir dos dados das células."""
    print("🏗️ Criando estrutura do notebook...")
    
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
    
    print(f"✅ Estrutura do notebook criada com {len(notebook_cells)} células.")
    return json.dumps(notebook_json, indent=2)

def main():
    """Função principal que orquestra todo o processo."""
    print("🚀 INICIANDO AGENTE DE PREPARAÇÃO DO COLAB")
    print("=" * 60)
    print("📅 Versão: 2.0 - Com Debug Completo")
    print("👤 Desenvolvido para: Preparação de Aulas do Professor Synapse")
    print("=" * 60)
    
    # Verificar arquivos necessários
    if not check_requirements():
        print("\n❌ Pré-requisitos não atendidos. Abortando.")
        input("Pressione Enter para sair...")
        return
    
    # Autenticar
    service = authenticate()
    if not service:
        print("\n❌ Falha na autenticação. Abortando.")
        input("Pressione Enter para sair...")
        return

    print("\n" + "=" * 60)
    
    # 1. Obter o ID do notebook do Google Colab
    print("📎 PASSO 1: IDENTIFICAR O NOTEBOOK")
    print("-" * 30)
    notebook_link = input("Cole o link completo do seu Google Colab Notebook: ")
    
    # Verifica qual formato de URL foi usado e extrai o ID corretamente
    notebook_id = None
    
    print("🔍 Analisando o link fornecido...")
    
    if '/d/' in notebook_link:
        try:
            notebook_id = notebook_link.split('/d/')[1].split('/')[0]
            print("✅ ID extraído usando padrão '/d/'")
        except IndexError:
            pass
    elif '/drive/' in notebook_link:
        try:
            # Para URLs do tipo: https://colab.research.google.com/drive/ID
            notebook_id = notebook_link.split('/drive/')[1].split('/')[0].split('#')[0].split('?')[0]
            print("✅ ID extraído usando padrão '/drive/'")
        except IndexError:
            pass
    
    # Se não conseguiu extrair o ID, tenta outros padrões comuns
    if not notebook_id:
        print("⚠️  Tentando padrões alternativos...")
        # Tenta extrair usando regex para capturar IDs do Google Drive
        id_pattern = r'[a-zA-Z0-9_-]{25,}'
        matches = re.findall(id_pattern, notebook_link)
        if matches:
            # Pega o primeiro match que parece ser um ID válido do Google Drive
            for match in matches:
                if len(match) >= 25:  # IDs do Google Drive geralmente têm pelo menos 25 caracteres
                    notebook_id = match
                    print("✅ ID extraído usando regex")
                    break
    
    if not notebook_id:
        print("❌ ERRO: Não foi possível extrair o ID do notebook do link fornecido.")
        print("   Certifique-se de que você copiou o link completo do Google Colab.")
        print("   Exemplo: https://colab.research.google.com/drive/SEU_ID_AQUI")
        input("Pressione Enter para sair...")
        return

    print(f"✅ ID do Notebook identificado: {notebook_id}")
        
    # 2. Obter a saída do Professor Synapse
    print("\n" + "=" * 60)
    print("📚 PASSO 2: COLAR CONTEÚDO DO PROFESSOR SYNAPSE")
    print("-" * 30)
    print("📝 Cole todo o conteúdo da aula do Professor Synapse abaixo.")
    print("   Dica: Ctrl+V para colar, depois pressione:")
    print("   • Windows: Ctrl+Z e Enter")
    print("   • Linux/Mac: Ctrl+D")
    print("-" * 60)
    
    synapse_output = ""
    line_count = 0
    
    while True:
        try:
            line = input()
            synapse_output += line + '\n'
            line_count += 1
            if line_count % 10 == 0:  # Mostra progresso a cada 10 linhas
                print(f"📄 {line_count} linhas coladas...")
        except EOFError:
            break
    
    print(f"✅ Conteúdo colado: {line_count} linhas, {len(synapse_output)} caracteres")
            
    if not synapse_output.strip():
        print("❌ Nenhum conteúdo foi colado. Abortando.")
        input("Pressione Enter para sair...")
        return
        
    # 3. Parsear o conteúdo e criar a estrutura do notebook
    print("\n" + "=" * 60)
    print("⚙️  PASSO 3: PROCESSANDO CONTEÚDO")
    print("-" * 30)
    
    parsed_cells = parse_synapse_output(synapse_output)
    if not parsed_cells:
        print("❌ Não foi possível encontrar blocos de código/markdown no formato esperado.")
        print("   Verifique se o conteúdo contém os marcadores corretos:")
        print("   • ▶️ seguido de ```python")
        print("   • 📖 seguido de ```markdown")
        print("\n🔍 Mostrando uma amostra do conteúdo colado:")
        print("-" * 40)
        print(synapse_output[:500] + "..." if len(synapse_output) > 500 else synapse_output)
        print("-" * 40)
        input("Pressione Enter para sair...")
        return
        
    new_notebook_content = create_notebook_structure(parsed_cells)
    
    # 4. Salvar o conteúdo em um arquivo temporário
    temp_filename = 'temp_notebook.ipynb'
    print(f"💾 Salvando conteúdo temporário em '{temp_filename}'...")
    
    try:
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(new_notebook_content)
        print("✅ Arquivo temporário criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo temporário: {e}")
        input("Pressione Enter para sair...")
        return
        
    # 5. Fazer o upload e substituir o arquivo no Google Drive
    print("\n" + "=" * 60)
    print("🚨 PASSO 4: CONFIRMAÇÃO FINAL")
    print("-" * 30)
    print("⚠️  ATENÇÃO: Esta operação irá SUBSTITUIR completamente o conteúdo atual do notebook!")
    print(f"📋 Notebook ID: {notebook_id}")
    print(f"📊 Células a serem criadas: {len(parsed_cells)}")
    print("-" * 60)
    
    confirm = input("Você tem ABSOLUTA CERTEZA que deseja continuar? (digite 'SIM' em maiúsculas): ")
    
    if confirm == 'SIM':
        try:
            print("\n📤 Enviando para o Google Drive...")
            print("⏳ Aguarde, isso pode levar alguns segundos...")
            
            media = MediaFileUpload(temp_filename, mimetype='application/vnd.google-colaboratory')
            result = service.files().update(
                fileId=notebook_id,
                media_body=media
            ).execute()
            
            print("\n🎉 SUCESSO TOTAL!")
            print("=" * 60)
            print("✅ O seu notebook no Google Colab foi atualizado com a aula!")
            print("💡 IMPORTANTE: Recarregue a página do Colab para ver as mudanças.")
            print(f"🔗 Link direto: https://colab.research.google.com/drive/{notebook_id}")
            print("=" * 60)
            
        except HttpError as error:
            print(f"\n❌ ERRO ao atualizar o arquivo: {error}")
            print("🔧 Possíveis soluções:")
            print("   1. Verifique se o ID do notebook está correto")
            print("   2. Certifique-se de que tem permissão para editar o notebook")
            print("   3. Tente executar o script novamente")
            
        finally:
            # Limpeza do arquivo temporário
            try:
                import time
                time.sleep(0.5)
                os.remove(temp_filename)
                print(f"🧹 Arquivo temporário '{temp_filename}' removido.")
            except (PermissionError, FileNotFoundError):
                print(f"ℹ️  O arquivo temporário '{temp_filename}' será removido automaticamente.")
    else:
        print("\n❌ Operação cancelada pelo usuário.")
        print("   Para confirmar, você deve digitar exatamente 'SIM' em maiúsculas.")
        try:
            os.remove(temp_filename)
            print(f"🧹 Arquivo temporário '{temp_filename}' removido.")
        except (PermissionError, FileNotFoundError):
            pass
    
    print("\n" + "=" * 60)
    print("🏁 AGENTE DE PREPARAÇÃO DO COLAB FINALIZADO")
    print("=" * 60)
    input("Pressione Enter para sair...")

# ESTA É A PARTE MAIS IMPORTANTE - A CHAMADA DA FUNÇÃO MAIN
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação interrompida pelo usuário (Ctrl+C).")
        print("👋 Até logo!")
    except Exception as e:
        print(f"\n💥 ERRO INESPERADO: {e}")
        print("🔧 Por favor, verifique se todas as dependências estão instaladas:")
        print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        input("Pressione Enter para sair...")