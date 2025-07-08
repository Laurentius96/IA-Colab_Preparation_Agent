import re, os, sys, json, io
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload


if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CLIENT_SECRETS = os.path.join(BASE_PATH, 'client_secrets.json')
TOKEN_FILE     = os.path.join(BASE_PATH, 'token.json')
SCOPES         = ['https://www.googleapis.com/auth/drive']


def extrair_id_do_link(link: str) -> str:
    """Extrai o ID do Colab/Drive (substitui múltiplos padrões)."""
    for pattern in (r'drive/([A-Za-z0-9\-_]+)',
                    r'/d/([A-Za-z0-9\-_]+)',
                    r'id=([A-Za-z0-9\-_]+)'):
        m = re.search(pattern, link)
        if m:
            return m.group(1)
    if re.fullmatch(r'[A-Za-z0-9\-_]{15,}', link):
        return link
    raise ValueError("ID inválido no link Colab/Drive.")


def converter_conteudo_para_notebook(raw: str) -> dict:
    """
    1) Isola tudo após o primeiro '---' de separador.
    2) Extrai cada fence ```markdown``` e ```python```.
    3) Para markdown: injeta ' ' antes/depois de <br> se colado a texto.
    4) Retorna dict ready‐to‐dump para .ipynb.
    """
    # 1) partida
    parts = re.split(r'(?m)^---\s*$', raw, maxsplit=1)
    if len(parts) < 2:
        raise ValueError("Layout inválido: não encontrou separador inicial '---'.")
    body = parts[1]

    # 2) encontra fences na ordem
    fence_re = re.compile(r'```(markdown|python)\s*\n(.*?)\n```', re.DOTALL)
    cells = []
    for m in fence_re.finditer(body):
        kind, content = m.group(1), m.group(2)
        lines = content.splitlines()
        if kind == 'markdown':
            # 3) preserva <br> mas garante espaço antes/depois se há texto adjacente
            fixed = [ re.sub(r'(?<=\S)<br>(?=\S)', ' <br> ', line)
                      for line in lines ]
            source = [ l + '\n' for l in fixed ]
            cell = {"cell_type":"markdown","metadata":{},"source":source}
        else:  # python
            source = [ l + '\n' for l in lines ]
            cell = {"cell_type":"code",
                    "execution_count":None,
                    "metadata":{},
                    "outputs":[],
                    "source":source}
        cells.append(cell)

    if not cells:
        raise ValueError("Parser não extraiu nenhum bloco de código/markdown.")
    
    # 4) monta notebook dict
    return {
      "nbformat": 4,
      "nbformat_minor": 4,
      "metadata": {
        "colab": {"toc_visible": True},
        "kernelspec": {
          "name": "python3",
          "display_name": "Python 3"
        }
      },
      "cells": cells
    }


def enviar_para_drive(file_id: str, nb_dict: dict):
    """Autentica e faz upload in-memory do .ipynb ao file_id no Drive."""
    if not os.path.exists(CLIENT_SECRETS):
        raise FileNotFoundError("client_secrets.json não encontrado.")

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    data = json.dumps(nb_dict, ensure_ascii=False).encode('utf-8')
    media = MediaIoBaseUpload(io.BytesIO(data),
                              mimetype='application/x-ipynb+json',
                              resumable=False)
    service.files().update(fileId=file_id, media_body=media).execute()


def executar_interface():
    """Tkinter/ttk GUI para obter link + conteúdo do usuário."""
    resultado = {'link':None,'conteudo':None}

    def on_ok():
        resultado['link'] = entry_link.get().strip()
        txt = text_area.get('1.0', 'end').rstrip()
        resultado['conteudo'] = txt
        root.destroy()

    root = tk.Tk()
    root.title("Modo Aula → Colab")
    ttk.Label(root, text="Colab URL (Drive ID):").grid(row=0,column=0,padx=5,pady=5,sticky='w')
    entry_link = ttk.Entry(root, width=60); entry_link.grid(row=0,column=1,padx=5,pady=5)
    ttk.Label(root, text="Conteúdo Modo Aula:").grid(row=1,column=0,columnspan=2,padx=5)
    text_area = scrolledtext.ScrolledText(root, width=80, height=20, wrap='word')
    text_area.grid(row=2,column=0,columnspan=2,padx=5,pady=5)
    ttk.Button(root, text="Enviar → Colab", command=on_ok).grid(row=3,column=0,columnspan=2,pady=10)
    root.mainloop()
    return resultado['link'], resultado['conteudo']


def main():
    link, aula = executar_interface()
    if not link or not aula:
        return

    try:
        fid = extrair_id_do_link(link)
        nb  = converter_conteudo_para_notebook(aula)
        enviar_para_drive(fid, nb)
        messagebox.showinfo("Sucesso", "Notebook atualizado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    main()
