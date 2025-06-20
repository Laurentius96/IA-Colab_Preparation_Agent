import os
import re
import json
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# --------- Configurações ---------
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRETS_FILE = 'client_secrets.json'

# --------- Interface Gráfica ---------
def obter_dados_via_gui():
    root = tk.Tk()
    root.title("Agente Colab")
    root.geometry("600x500")

    # Link do Colab
    tk.Label(root, text="Link do Google Colab:", anchor="w").pack(fill="x", padx=10, pady=(10,5))
    link_var = tk.StringVar()
    tk.Entry(root, textvariable=link_var).pack(fill="x", padx=10)

    # Texto da aula
    tk.Label(root, text="Cole aqui a aula (Ctrl+V):", anchor="w").pack(fill="x", padx=10, pady=(10,5))
    texto_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
    texto_widget.pack(fill="both", expand=True, padx=10)

    def iniciar():
        link = link_var.get().strip()
        conteudo = texto_widget.get("1.0", tk.END).strip()
        if not link or not conteudo:
            messagebox.showerror("Erro", "Preencha o link e cole o texto da aula antes de continuar.")
            return
        root.destroy()
        global GUI_LINK, GUI_AULA
        GUI_LINK = link
        GUI_AULA = conteudo

    tk.Button(root, text="Iniciar", command=iniciar).pack(pady=10)
    root.mainloop()

# --------- Funções de Backend ---------

def check_requirements():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        messagebox.showerror(
            "Erro de Pré-requisito",
            f"Arquivo '{CLIENT_SECRETS_FILE}' não encontrado. Você precisa baixar as credenciais."
        )
        return False
    return True


def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        return build('drive', 'v3', credentials=creds)
    except HttpError as error:
        messagebox.showerror("Erro de Autenticação", str(error))
        return None


def parse_synapse_output(text):
    """Converte texto Modo Aula em lista de células para notebook."""
    # Remove seções opcionais
    if "🌊 Mergulhos Adicionais Opcionais" in text:
        text = text.split("🌊 Mergulhos Adicionais Opcionais")[0]

    # Regex para blocos de markdown, código e leitura
    pattern = re.compile(
        r"(```markdown\n(.*?)\n```)|"
        r"(▶️.*?```python\n(.*?)\n```)|"
        r"(📖.*?```markdown\n(.*?)\n```)"
        , re.DOTALL
    )

    cells = []
    for match in pattern.finditer(text):
        md, code, read = match.group(2), match.group(4), match.group(6)
        if md:
            # converte <br> em parágrafos
            content = md.replace('<br>', '\n\n').strip()
            cells.append({'type': 'markdown', 'content': content})
        elif code:
            code_content = code.strip()
            cells.append({'type': 'code', 'content': code_content})
            cells.append({'type': 'code', 'content': '# Pratique seu código aqui!'})
        elif read:
            content = read.replace('<br>', '\n\n').strip()
            cells.append({'type': 'markdown', 'content': content})
    return cells


def create_notebook_structure(cells_data):
    notebook = {
        'nbformat': 4,
        'nbformat_minor': 0,
        'metadata': {},
        'cells': []
    }
    for cell in cells_data:
        entry = {
            'metadata': {},
            'source': [line + '\n' for line in cell['content'].split('\n')]
        }
        if cell['type'] == 'markdown':
            entry['cell_type'] = 'markdown'
        else:
            entry.update({'cell_type': 'code', 'execution_count': None, 'outputs': []})
        notebook['cells'].append(entry)
    return json.dumps(notebook, indent=2)

# --------- Função Principal ---------

def main():
    obter_dados_via_gui()
    notebook_link = GUI_LINK
    synapse_output = GUI_AULA

    if not check_requirements():
        return
    service = authenticate()
    if not service:
        return

    # Extrai ID do Colab
    notebook_id = None
    if '/d/' in notebook_link:
        part = notebook_link.split('/d/')[1]
    elif '/drive/' in notebook_link:
        part = notebook_link.split('/drive/')[1]
    else:
        matches = re.findall(r'[A-Za-z0-9_-]{25,}', notebook_link)
        part = matches[0] if matches else ''
    notebook_id = part.split('?')[0].split('#')[0]
    if not notebook_id:
        messagebox.showerror("Erro de Link", "ID do Colab inválido. Verifique o link.")
        return

    cells = parse_synapse_output(synapse_output)
    if not cells:
        messagebox.showerror("Erro de Parser", "Não foi possível processar o conteúdo da aula.")
        return
    notebook_json = create_notebook_structure(cells)

    temp_file = 'temp_notebook.ipynb'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(notebook_json)

    if not messagebox.askyesno(
        "Confirmação",
        "Esta operação substituirá o notebook no Colab. Deseja continuar?"
    ):
        messagebox.showinfo("Cancelado", "Operação cancelada pelo usuário.")
        try:
            os.remove(temp_file)
        except PermissionError:
            pass
        return

    try:
        media = MediaFileUpload(temp_file, mimetype='application/vnd.google-colaboratory')
        service.files().update(fileId=notebook_id, media_body=media).execute()
        messagebox.showinfo("Sucesso", "Notebook atualizado com sucesso no Colab.")
    except HttpError as error:
        messagebox.showerror("Erro no Upload", str(error))
    finally:
        try:
            os.remove(temp_file)
        except PermissionError:
            pass

if __name__ == '__main__':
    main()