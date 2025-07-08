import sys
import os
import re
import json
import logging
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# --------- Configurações de Logging ---------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('agente_colab.log', encoding='utf-8'), logging.StreamHandler()]
)

# --------- Definição de caminhos ---------
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(__file__)

CLIENT_SECRETS_FILE = os.path.join(BASE_PATH, 'client_secrets.json')
TOKEN_FILE          = os.path.join(BASE_PATH, 'token.json')

SCOPES = ['https://www.googleapis.com/auth/drive']

def obter_dados_via_gui():
    """Exibe GUI para inserir link do Colab e colar a aula."""
    root = tk.Tk()
    root.title("Agente Colab")
    root.geometry("650x550")

    ttk.Label(root, text="Link do Google Colab:").pack(fill='x', padx=10, pady=(10,5))
    link_var = tk.StringVar()
    ttk.Entry(root, textvariable=link_var).pack(fill='x', padx=10)

    ttk.Label(root, text="Cole aqui a aula (Ctrl+V):").pack(fill='x', padx=10, pady=(10,5))
    texto_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
    texto_widget.pack(fill='both', expand=True, padx=10)

    status = ttk.Label(root, text="")
    status.pack(fill='x', padx=10)

    def iniciar():
        link = link_var.get().strip()
        conteudo = texto_widget.get("1.0", tk.END).strip()
        if not link or not conteudo:
            messagebox.showerror("Erro", "Preencha link e cole o texto da aula antes de continuar.")
            return
        status.config(text="Processando...")
        root.update_idletasks()
        root.destroy()
        return_values['link'] = link
        return_values['aula'] = conteudo

    return_values = {}
    ttk.Button(root, text="Iniciar", command=iniciar).pack(pady=10)
    root.mainloop()
    return return_values.get('link'), return_values.get('aula')


def check_requirements():
    """Verifica se o arquivo client_secrets existe."""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        logging.error("Arquivo client_secrets.json não encontrado.")
        messagebox.showerror("Erro de Pré-requisito", "Arquivo 'client_secrets.json' não encontrado."
                             " Baixe as credenciais no Console do Google Cloud.")
        return False
    return True


def authenticate():
    """Autentica no Google Drive e retorna o serviço."""
    creds = None
    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w', encoding='utf-8') as token_file:
                token_file.write(creds.to_json())
        service = build('drive', 'v3', credentials=creds)
        logging.info("Autenticação bem-sucedida no Google Drive.")
        return service
    except Exception as e:
        logging.exception("Falha na autenticação")
        messagebox.showerror("Erro de Autenticação", str(e))
        return None


def parse_synapse_output(text):
    """Analisa texto 'Modo Aula', aceita cabeçalhos diretos, tabelas, separadores e preserva <br>."""
    # Remove seções opcionais
    if "🌊 Mergulhos Adicionais Opcionais" in text:
        text = text.split("🌊 Mergulhos Adicionais Opcionais")[0]

    lines = text.splitlines(True)
    cells = []
    buffer = ''

    def flush_buffer():
        nonlocal buffer
        if buffer:
            cells.append({'type': 'markdown', 'content': buffer.rstrip()})
            buffer = ''

    for raw in lines:
        # Espaça <br> colado ao texto
        line = re.sub(r'(?<=\S)<br>(?=\S)', ' <br> ', raw)

        # Se a linha for só <br>, faz célula independente
        if line.strip() == '<br>':
            flush_buffer()
            cells.append({'type': 'markdown', 'content': '<br>\n'})
            continue

        # Sempre que encontrar um cabeçalho (##, ###), tabela (|...) ou separador (---), inicia nova célula
        if re.match(r'^(##+\s|---|\|)', line):
            flush_buffer()

        buffer += line

    # Flush final
    flush_buffer()
    return cells


def create_notebook_structure(cells_data):
    """Gera o JSON de um notebook a partir das células fornecidas."""
    notebook = {'nbformat':4,'nbformat_minor':0,'metadata':{},'cells':[]}
    for cell in cells_data:
        content = cell['content'].replace('<br>',' <br> ')
        lines = [l+'\n' for l in content.split('\n')]
        entry = {'metadata':{}, 'source':lines}
        if cell['type']=='markdown':
            entry['cell_type']='markdown'
        else:
            entry.update({'cell_type':'code','execution_count':None,'outputs':[]})
        notebook['cells'].append(entry)
    return json.dumps(notebook, indent=2)


def main():
    link, aula = obter_dados_via_gui()
    if not link or not aula:
        logging.warning("Inputs não fornecidos, encerrando.")
        return
    if not check_requirements():
        return
    service = authenticate()
    if not service:
        return

    # Extrai ID
    if '/d/' in link:
        part = link.split('/d/')[1]
    elif '/drive/' in link:
        part = link.split('/drive/')[1]
    else:
        m = re.findall(r'[A-Za-z0-9_-]{25,}', link)
        part = m[0] if m else ''
    notebook_id = part.split('?')[0].split('#')[0]
    if not notebook_id:
        messagebox.showerror("Erro de Link","ID inválido. Verifique o link.")
        return

    cells = parse_synapse_output(aula)
    if not cells:
        messagebox.showerror("Erro de Parser","Não foi possível processar a aula.")
        return
    nb_json = create_notebook_structure(cells)

    temp_file = os.path.join(BASE_PATH, 'temp_notebook.ipynb')
    with open(temp_file,'w',encoding='utf-8') as f:
        f.write(nb_json)

    if not messagebox.askyesno("Confirmação","Substituir o notebook no Colab?" ):
        os.remove(temp_file)
        return

    try:
        media = MediaFileUpload(temp_file, mimetype='application/vnd.google-colaboratory')
        service.files().update(fileId=notebook_id, media_body=media).execute()
        messagebox.showinfo("Sucesso","Notebook atualizado com sucesso.")
    except HttpError as e:
        logging.exception("Falha no upload")
        messagebox.showerror("Erro no Upload", str(e))
    finally:
        try: os.remove(temp_file)
        except: pass

if __name__=='__main__':
    main()
