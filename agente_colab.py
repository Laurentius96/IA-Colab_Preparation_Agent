import os
import re
import json
import sys
import time
import tkinter as tk
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from tkinter import filedialog, simpledialog, scrolledtext, messagebox

def obter_dados_via_gui():
    root = tk.Tk()
    root.title("Agente Colab")
    root.geometry("600x500")
    
    # Link do Colab
    tk.Label(root, text="Link do Google Colab:", anchor="w").pack(fill="x", padx=10, pady=(10,0))
    link_var = tk.StringVar()
    tk.Entry(root, textvariable=link_var).pack(fill="x", padx=10)

    # Texto da aula
    tk.Label(root, text="Cole aqui a aula (Ctrl+V):", anchor="w").pack(fill="x", padx=10, pady=(10,0))
    texto_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
    texto_widget.pack(fill="both", expand=True, padx=10, pady=(0,10))

    def iniciar():
        link = link_var.get().strip()
        conteudo = texto_widget.get("1.0", tk.END).strip()
        if not link or not conteudo:
            messagebox.showerror("Erro", "Preencha o link e cole o texto da aula antes de continuar.")
            return
        root.destroy()
        # Variáveis globais que o main() vai usar
        global GUI_LINK, GUI_AULA
        GUI_LINK = link
        GUI_AULA = conteudo

    tk.Button(root, text="Iniciar", command=iniciar).pack(pady=(0,10))
    root.mainloop()

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

# =========================================================================
# 🧠 CÉREBRO DEFINITIVO - PARSER INTELIGENTE COM REGEX
# =========================================================================
def parse_synapse_output(text):
    """
    Analisa a saída completa e estruturada do Professor Synapse,
    convertendo-a em uma lista de células prontas para o Google Colab.
    """
    print("📝 Analisando a estrutura completa e complexa da aula...")
    print("🎯 Usando parser inteligente com regex avançado...")

    # ETAPA 1: Pré-filtragem - Remove a seção "Mergulhos Adicionais"
    original_length = len(text)
    if "🌊 Mergulhos Adicionais Opcionais" in text:
        text = text.split("🌊 Mergulhos Adicionais Opcionais")[0]
        print("✅ Seção 'Mergulhos Adicionais' removida com sucesso.")
        print(f"   📊 Texto reduzido de {original_length} para {len(text)} caracteres")
    else:
        print("ℹ️  Seção 'Mergulhos Adicionais' não encontrada (normal se não existir)")

    # ETAPA 2: Regex para encontrar todos os tipos de blocos que nos interessam.
    # Esta regex "caça" blocos de markdown ou pares de código/texto.
    # Padrão 1: Bloco de Markdown geral (```markdown)
    # Padrão 2: Bloco de Código (▶️ ... ```python)
    # Padrão 3: Bloco de Texto de Leitura (📖 ... ```markdown)
    
    print("🔍 Iniciando busca por padrões com regex...")
    
    pattern = re.compile(
        r"(```markdown\n(.*?)\n```)|(▶️.*?```python\n(.*?)\n```)|(📖.*?```markdown\n(.*?)\n```)", 
        re.DOTALL
    )
    
    matches = list(pattern.finditer(text))
    print(f"🎯 Encontrados {len(matches)} blocos válidos para processamento")
    
    cells = []
    code_blocks_found = 0
    markdown_blocks_found = 0
    reading_blocks_found = 0
    
    for i, match in enumerate(matches):
        print(f"📄 Processando bloco {i+1}/{len(matches)}...")
        
        # O resultado do match nos diz qual grupo foi encontrado
        # match.group(2) -> Bloco de Markdown geral
        # match.group(4) -> Bloco de Código Python
        # match.group(6) -> Bloco de Texto de Leitura
        
        if match.group(2):
            # Bloco de Markdown geral (teoria, títulos, etc.)
            content = match.group(2).replace('<br>', '').strip()
            cells.append({'type': 'markdown', 'content': content})
            markdown_blocks_found += 1
            print(f"   📖 Markdown adicionado: {len(content)} caracteres")
        
        elif match.group(4):
            # Bloco de Código Python
            content = match.group(4).strip()
            # Adiciona a célula de código
            cells.append({'type': 'code', 'content': content})
            # >>> AQUI ESTÁ A SUA FUNCIONALIDADE ESPECIAL <<<
            # Adiciona a célula de código em branco para prática
            cells.append({'type': 'code', 'content': '# Pratique seu código aqui!'})
            code_blocks_found += 1
            print(f"   ⚡ Código adicionado: {len(content)} caracteres")
            print(f"   🎯 Célula de prática adicionada!")
            
        elif match.group(6):
            # Bloco de Texto de Leitura
            content = match.group(6).strip()
            cells.append({'type': 'markdown', 'content': content})
            reading_blocks_found += 1
            print(f"   📚 Texto de leitura adicionado: {len(content)} caracteres")

    # ETAPA 3: Verificação e estatísticas finais
    if not cells:
        print("❌ ERRO: Nenhum bloco válido foi encontrado!")
        print("🔧 Possíveis causas:")
        print("   1. A estrutura do prompt pode ter mudado")
        print("   2. O texto não contém os padrões esperados (```markdown, ▶️, 📖)")
        print("   3. Formatação incorreta dos blocos de código")
        print("\n🔍 Mostrando uma amostra do texto para diagnóstico:")
        print("-" * 50)
        sample = text[:1000] + "..." if len(text) > 1000 else text
        print(sample)
        print("-" * 50)
        return []
    else:
        print("\n" + "=" * 60)
        print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📊 ESTATÍSTICAS DETALHADAS:")
        print(f"   🔢 Total de células criadas: {len(cells)}")
        print(f"   📖 Blocos de markdown (teoria): {markdown_blocks_found}")
        print(f"   📚 Blocos de leitura: {reading_blocks_found}")
        print(f"   ⚡ Blocos de código: {code_blocks_found}")
        print(f"   🎯 Células de prática: {code_blocks_found}")
        print("=" * 60)
        
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
    # obtém link e aula pela interface gráfica
    obter_dados_via_gui()
    notebook_link = GUI_LINK
    synapse_output = GUI_AULA
    print("=" * 70)
    print("📅 Versão: DEFINITIVA - Parser Inteligente")
    print("🧠 Cérebro: Regex Avançado para Estruturas Complexas")
    print("🎯 Especialidade: Modo Aula do Professor Synapse")
    print("👤 Desenvolvido para: Transformar Aulas em Notebooks Interativos")
    print("=" * 70)
    
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

    print("\n" + "=" * 70)
    
    # 1. Obter o ID do notebook do Google Colab
    print("📎 PASSO 1: IDENTIFICAR O NOTEBOOK")
    print("-" * 35)
    
    
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
    print("\n" + "=" * 70)
    print("📚 PASSO 2: COLAR AULA COMPLETA DO PROFESSOR SYNAPSE")
    print("-" * 35)
    print("📝 Cole TODA a aula do Professor Synapse (Modo Aula) abaixo.")
    print("   🧠 PARSER INTELIGENTE: Detecta automaticamente:")
    print("   📖 Teoria e explicações (markdown)")
    print("   ⚡ Códigos executáveis (python)")
    print("   📚 Textos de leitura")
    print("   🎯 Adiciona células de prática após cada código!")
    print("   🚫 Remove automaticamente 'Mergulhos Adicionais'")
    print("   Dica: Ctrl+V para colar, depois pressione:")
    print("   • Windows: Ctrl+Z e Enter")
    print("   • Linux/Mac: Ctrl+D")
    print("-" * 70)
    
    
    line_count = 0
    
    
    
    print(f"✅ Conteúdo colado: {line_count} linhas, {len(synapse_output)} caracteres")
            
    if not synapse_output.strip():
        print("❌ Nenhum conteúdo foi colado. Abortando.")
        input("Pressione Enter para sair...")
        return
        
    # 3. Parsear o conteúdo e criar a estrutura do notebook
    print("\n" + "=" * 70)
    print("⚙️  PASSO 3: PROCESSANDO COM PARSER INTELIGENTE")
    print("-" * 35)
    
    parsed_cells = parse_synapse_output(synapse_output)
    if not parsed_cells:
        print("❌ Não foi possível processar o conteúdo.")
        print("   O parser inteligente não encontrou padrões válidos.")
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
    print("\n" + "=" * 70)
    print("🚨 PASSO 4: CONFIRMAÇÃO FINAL")
    print("-" * 35)
    print("⚠️  ATENÇÃO: Esta operação irá SUBSTITUIR completamente o conteúdo atual do notebook!")
    print(f"📋 Notebook ID: {notebook_id}")
    print(f"📊 Células a serem criadas: {len(parsed_cells)}")
    print("🎯 RESULTADO: Notebook interativo com teoria + prática!")
    print("-" * 70)
    
    confirm = input("Você tem ABSOLUTA CERTEZA que deseja continuar? (digite 'SIM' em maiúsculas): ")
    
    if confirm == 'SIM':
        try:
            print("\n📤 Enviando aula completa para o Google Drive...")
            print("⏳ Aguarde, isso pode levar alguns segundos...")
            
            media = MediaFileUpload(temp_filename, mimetype='application/vnd.google-colaboratory')
            result = service.files().update(
                fileId=notebook_id,
                media_body=media
            ).execute()
            
            print("\n🎉 SUCESSO TOTAL!")
            print("=" * 70)
            print("✅ Seu notebook no Google Colab foi atualizado com PARSER INTELIGENTE!")
            print("🧠 Estrutura complexa processada com sucesso!")
            print("📚 Contém: Teoria + Códigos + Células de Prática")
            print("🚫 Mergulhos Adicionais removidos automaticamente")
            print("💡 IMPORTANTE: Recarregue a página do Colab para ver as mudanças.")
            print(f"🔗 Link direto: https://colab.research.google.com/drive/{notebook_id}")
            print("=" * 70)
            
        except HttpError as error:
            print(f"\n❌ ERRO ao atualizar o arquivo: {error}")
            print("🔧 Possíveis soluções:")
            print("   1. Verifique se o ID do notebook está correto")
            print("   2. Certifique-se de que tem permissão para editar o notebook")
            print("   3. Tente executar o script novamente")
            
        finally:
            # Limpeza do arquivo temporário
            try:
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
    
    print("\n" + "=" * 70)
    print("🏁 AGENTE DE PREPARAÇÃO DO COLAB - VERSÃO DEFINITIVA")
    print("=" * 70)
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