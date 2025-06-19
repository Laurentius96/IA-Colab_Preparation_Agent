import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import os
import re
import json
import threading
import time
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Configuração para evitar erro do msedge
os.environ['BROWSER'] = 'default'

# Escopos de permissão: Acesso total ao Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRETS_FILE = 'client_secrets.json'

class AgenteColabGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Agente de Preparação do Colab v3.1 - CORRIGIDO")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variáveis
        self.service = None
        self.notebook_id = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2196F3', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🚀 Agente de Preparação do Colab v3.1", 
                              font=('Arial', 18, 'bold'),
                              bg='#2196F3', fg='white')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame,
                                 text="✅ VERSÃO CORRIGIDA - Sem erro do msedge",
                                 font=('Arial', 10),
                                 bg='#2196F3', fg='white')
        subtitle_label.pack()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # PASSO 1: Autenticação
        auth_frame = tk.LabelFrame(main_frame, text="📋 PASSO 1: Autenticação", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0')
        auth_frame.pack(fill='x', pady=5)
        
        self.auth_button = tk.Button(auth_frame, text="🔐 Autenticar com Google Drive",
                                    command=self.authenticate, bg='#4CAF50', fg='white',
                                    font=('Arial', 10, 'bold'), height=2)
        self.auth_button.pack(pady=10)
        
        self.auth_status = tk.Label(auth_frame, text="❌ Não autenticado", 
                                   font=('Arial', 10), bg='#f0f0f0')
        self.auth_status.pack()
        
        # PASSO 2: Link do Notebook
        link_frame = tk.LabelFrame(main_frame, text="📎 PASSO 2: Link do Notebook", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0')
        link_frame.pack(fill='x', pady=5)
        
        tk.Label(link_frame, text="Cole o link do seu Google Colab:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=10, pady=5)
        
        self.link_entry = tk.Entry(link_frame, font=('Arial', 10), width=70)
        self.link_entry.pack(padx=10, pady=5)
        
        self.validate_button = tk.Button(link_frame, text="✅ Validar Link",
                                        command=self.validate_link, bg='#FF9800', fg='white',
                                        font=('Arial', 10, 'bold'))
        self.validate_button.pack(pady=5)
        
        self.link_status = tk.Label(link_frame, text="", font=('Arial', 10), bg='#f0f0f0')
        self.link_status.pack()
        
        # PASSO 3: Conteúdo da Aula
        content_frame = tk.LabelFrame(main_frame, text="📚 PASSO 3: Aula do Professor Synapse", 
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0')
        content_frame.pack(fill='both', expand=True, pady=5)
        
        tk.Label(content_frame, text="Cole TODA a aula do Professor Synapse abaixo:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=10, pady=5)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, height=15, 
                                                     font=('Consolas', 9))
        self.content_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Botões de ação
        action_frame = tk.Frame(main_frame, bg='#f0f0f0')
        action_frame.pack(fill='x', pady=10)
        
        self.process_button = tk.Button(action_frame, text="⚡ PROCESSAR AULA",
                                       command=self.process_content, bg='#F44336', fg='white',
                                       font=('Arial', 12, 'bold'), height=2, width=20)
        self.process_button.pack(side='left', padx=5)
        
        self.clear_button = tk.Button(action_frame, text="🧹 Limpar Tudo",
                                     command=self.clear_all, bg='#9E9E9E', fg='white',
                                     font=('Arial', 10))
        self.clear_button.pack(side='right', padx=5)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
        # Log de status
        self.log_text = scrolledtext.ScrolledText(main_frame, height=6, 
                                                 font=('Consolas', 8), bg='#263238', fg='#4CAF50')
        self.log_text.pack(fill='x', pady=5)
        
        self.log("🚀 Agente de Preparação do Colab v3.1 iniciado!")
        self.log("✅ VERSÃO CORRIGIDA - Sem erro do msedge")
        self.log("📋 Siga os passos na ordem para processar sua aula.")
        
    def log(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def authenticate(self):
        """Autenticação com múltiplas tentativas e fallback"""
        self.log("🔐 Iniciando autenticação...")
        self.progress.start()
        
        def auth_thread():
            try:
                if not os.path.exists(CLIENT_SECRETS_FILE):
                    self.log(f"❌ Arquivo '{CLIENT_SECRETS_FILE}' não encontrado!")
                    messagebox.showerror("Erro", f"Arquivo '{CLIENT_SECRETS_FILE}' não encontrado!\nBaixe as credenciais do Google Cloud Console.")
                    return
                
                creds = None
                if os.path.exists('token.json'):
                    self.log("✅ Carregando credenciais salvas...")
                    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        self.log("🔄 Atualizando credenciais...")
                        creds.refresh(Request())
                    else:
                        self.log("🌐 Tentando autenticação automática...")
                        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                        
                        try:
                            # MÉTODO 1: Tentativa automática com navegador padrão
                            creds = flow.run_local_server(port=0, open_browser=True)
                            self.log("✅ Autenticação automática bem-sucedida!")
                            
                        except Exception as auto_error:
                            self.log(f"⚠️ Autenticação automática falhou: {auto_error}")
                            self.log("🔄 Tentando autenticação manual...")
                            
                            # MÉTODO 2: Autenticação manual
                            try:
                                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                                auth_url, _ = flow.authorization_url(prompt='consent')
                                
                                # Copia URL para clipboard
                                self.root.clipboard_clear()
                                self.root.clipboard_append(auth_url)
                                
                                self.log("📋 URL copiada para clipboard!")
                                
                                # Mostra a URL para o usuário
                                result = messagebox.askokcancel(
                                    "Autenticação Manual", 
                                    f"A URL de autenticação foi copiada para seu clipboard.\n\n"
                                    f"PASSOS:\n"
                                    f"1. Cole a URL no seu navegador (Ctrl+V)\n"
                                    f"2. Faça login no Google\n"
                                    f"3. Copie o código de autorização\n"
                                    f"4. Clique OK para continuar\n\n"
                                    f"URL: {auth_url[:50]}..."
                                )
                                
                                if result:
                                    # Pede o código de autorização
                                    auth_code = simpledialog.askstring(
                                        "Código de Autorização", 
                                        "Cole o código de autorização aqui:",
                                        show='*'
                                    )
                                    
                                    if auth_code:
                                        flow.fetch_token(code=auth_code.strip())
                                        creds = flow.credentials
                                        self.log("✅ Autenticação manual bem-sucedida!")
                                    else:
                                        raise Exception("Código de autorização não fornecido")
                                else:
                                    raise Exception("Autenticação cancelada pelo usuário")
                                    
                            except Exception as manual_error:
                                self.log(f"❌ Autenticação manual falhou: {manual_error}")
                                raise manual_error
                    
                    # Salva as credenciais
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                        
                self.service = build('drive', 'v3', credentials=creds)
                self.log("✅ Autenticação completa!")
                self.auth_status.config(text="✅ Autenticado com sucesso!", fg='green')
                self.auth_button.config(text="✅ Autenticado", state='disabled')
                
            except Exception as e:
                self.log(f"❌ Erro na autenticação: {e}")
                messagebox.showerror("Erro de Autenticação", 
                                    f"Erro na autenticação:\n{str(e)}\n\n"
                                    f"Dicas:\n"
                                    f"1. Verifique se o arquivo client_secrets.json está correto\n"
                                    f"2. Tente executar como administrador\n"
                                    f"3. Verifique sua conexão com a internet")
            finally:
                self.progress.stop()
                
        threading.Thread(target=auth_thread, daemon=True).start()
        
    def validate_link(self):
        """Valida o link do notebook"""
        link = self.link_entry.get().strip()
        if not link:
            messagebox.showwarning("Aviso", "Por favor, cole o link do notebook!")
            return
            
        self.log("🔍 Validando link do notebook...")
        
        # Extrai o ID do notebook
        notebook_id = None
        
        if '/d/' in link:
            try:
                notebook_id = link.split('/d/')[1].split('/')[0]
            except IndexError:
                pass
        elif '/drive/' in link:
            try:
                notebook_id = link.split('/drive/')[1].split('/')[0].split('#')[0].split('?')[0]
            except IndexError:
                pass
        
        if not notebook_id:
            id_pattern = r'[a-zA-Z0-9_-]{25,}'
            matches = re.findall(id_pattern, link)
            if matches:
                for match in matches:
                    if len(match) >= 25:
                        notebook_id = match
                        break
        
        if notebook_id:
            self.notebook_id = notebook_id
            self.log(f"✅ ID do notebook extraído: {notebook_id}")
            self.link_status.config(text=f"✅ Notebook ID: {notebook_id[:20]}...", fg='green')
        else:
            self.log("❌ Não foi possível extrair o ID do notebook!")
            self.link_status.config(text="❌ Link inválido!", fg='red')
            messagebox.showerror("Erro", "Link inválido! Certifique-se de colar o link completo do Google Colab.")
            
    def parse_synapse_output(self, text):
        """Parser inteligente para a aula do Professor Synapse"""
        self.log("📝 Analisando estrutura da aula...")
        
        # Remove "Mergulhos Adicionais"
        if "🌊 Mergulhos Adicionais Opcionais" in text:
            text = text.split("🌊 Mergulhos Adicionais Opcionais")[0]
            self.log("✅ Seção 'Mergulhos Adicionais' removida")
        
        # Regex para encontrar blocos
        pattern = re.compile(
            r"(```markdown\n(.*?)\n```)|(▶️.*?```python\n(.*?)\n```)|(📖.*?```markdown\n(.*?)\n```)", 
            re.DOTALL
        )
        
        matches = list(pattern.finditer(text))
        self.log(f"🎯 Encontrados {len(matches)} blocos válidos")
        
        cells = []
        code_blocks = 0
        
        for match in matches:
            if match.group(2):
                # Markdown
                content = match.group(2).replace('<br>', '').strip()
                cells.append({'type': 'markdown', 'content': content})
            elif match.group(4):
                # Código
                content = match.group(4).strip()
                cells.append({'type': 'code', 'content': content})
                cells.append({'type': 'code', 'content': '# Pratique seu código aqui!'})
                code_blocks += 1
            elif match.group(6):
                # Texto de leitura
                content = match.group(6).strip()
                cells.append({'type': 'markdown', 'content': content})
        
        self.log(f"✅ Processamento concluído: {len(cells)} células, {code_blocks} códigos")
        return cells
        
    def create_notebook_structure(self, cells_data):
        """Cria estrutura do notebook"""
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
                "colab": {"provenance": []},
                "kernelspec": {"name": "python3", "display_name": "Python 3"},
                "language_info": {"name": "python"}
            },
            "cells": notebook_cells
        }
        
        return json.dumps(notebook_json, indent=2)
        
    def process_content(self):
        """Processa o conteúdo e atualiza o notebook"""
        # Verificações
        if not self.service:
            messagebox.showerror("Erro", "Faça a autenticação primeiro!")
            return
            
        if not self.notebook_id:
            messagebox.showerror("Erro", "Valide o link do notebook primeiro!")
            return
            
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showerror("Erro", "Cole o conteúdo da aula!")
            return
            
        # Confirmação
        if not messagebox.askyesno("Confirmação", 
                                  f"Isso irá SUBSTITUIR o conteúdo do notebook!\n\nNotebook ID: {self.notebook_id}\n\nContinuar?"):
            return
            
        self.log("⚡ Iniciando processamento...")
        self.progress.start()
        
        def process_thread():
            try:
                # Parse do conteúdo
                parsed_cells = self.parse_synapse_output(content)
                if not parsed_cells:
                    self.log("❌ Nenhum bloco válido encontrado!")
                    messagebox.showerror("Erro", "Não foi possível processar o conteúdo!")
                    return
                
                # Criar estrutura do notebook
                notebook_content = self.create_notebook_structure(parsed_cells)
                
                # Salvar arquivo temporário
                temp_filename = 'temp_notebook.ipynb'
                with open(temp_filename, 'w', encoding='utf-8') as f:
                    f.write(notebook_content)
                
                self.log("📤 Enviando para Google Drive...")
                
                # Upload
                media = MediaFileUpload(temp_filename, mimetype='application/vnd.google-colaboratory')
                result = self.service.files().update(
                    fileId=self.notebook_id,
                    media_body=media
                ).execute()
                
                # Limpeza
                os.remove(temp_filename)
                
                self.log("🎉 SUCESSO! Notebook atualizado!")
                messagebox.showinfo("Sucesso!", 
                                   f"Notebook atualizado com sucesso!\n\n"
                                   f"Células criadas: {len(parsed_cells)}\n"
                                   f"Recarregue a página do Colab para ver as mudanças.\n\n"
                                   f"Link: https://colab.research.google.com/drive/{self.notebook_id}")
                
            except Exception as e:
                self.log(f"❌ Erro: {e}")
                messagebox.showerror("Erro", f"Erro ao processar: {e}")
            finally:
                self.progress.stop()
                
        threading.Thread(target=process_thread, daemon=True).start()
        
    def clear_all(self):
        """Limpa todos os campos"""
        self.content_text.delete(1.0, tk.END)
        self.link_entry.delete(0, tk.END)
        self.link_status.config(text="")
        self.notebook_id = None
        self.log("🧹 Campos limpos!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AgenteColabGUI(root)
    root.mainloop()