import re, os, sys, json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
import io

# Determina o diretório base (BASE_PATH), considerando o caso de execução via PyInstaller (.exe)
if getattr(sys, 'frozen', False):
    # Se o aplicativo estiver empacotado como .exe, os arquivos estarão em sys._MEIPASS
    BASE_PATH = sys._MEIPASS
else:
    # Caso contrário, estamos executando o código fonte; use o diretório do arquivo atual
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Arquivos de credenciais e token (devem estar no mesmo diretório do script/executável)
CLIENT_SECRETS_FILE = os.path.join(BASE_PATH, 'client_secrets.json')
TOKEN_FILE = os.path.join(BASE_PATH, 'token.json')

# Escopo de acesso ao Google Drive (permite visualizar e editar arquivos do Drive do usuário)
SCOPES = ['https://www.googleapis.com/auth/drive']

def extrair_id_do_link(link: str) -> str:
    """
    Extrai o ID do arquivo do Google Drive a partir de um link do Colab ou do Drive.
    Suporta links do Colab (colab.research.google.com/drive/...) e links diretos do Drive (/d/ ou ?id=).
    Lança ValueError se nenhum ID válido for encontrado.
    """
    # Tenta encontrar o padrão de ID em diferentes formatos de URL
    match = re.search(r'drive/([A-Za-z0-9\-_]+)', link)
    if not match:
        match = re.search(r'/d/([A-Za-z0-9\-_]+)', link)
    if not match:
        match = re.search(r'id=([A-Za-z0-9\-_]+)', link)
    if match:
        return match.group(1)
    # Verifica se o usuário inseriu diretamente um ID (sequência de caracteres válida)
    if re.fullmatch(r'[A-Za-z0-9\-_]{15,}', link):
        return link  # interpreta a string pura como um ID de arquivo
    # Se nada foi encontrado, o link/ID é inválido
    raise ValueError("Link do notebook inválido ou ID do arquivo não encontrado.")

def converter_conteudo_para_notebook(conteudo_markdown: str) -> dict:
    """
    Converte o conteúdo de aula em markdown estruturado (Modo Aula) para o formato de um notebook Jupyter (.ipynb).
    Preserva rigorosamente as tags <br> e quebras de linha no markdown.
    Retorna um dicionário Python representando o conteúdo JSON do notebook.
    """
    # 1. Validação básica do conteúdo
    if not conteudo_markdown or conteudo_markdown.strip() == "":
        raise ValueError("O conteúdo da aula está vazio.")
    # Verifica se o conteúdo segue o formato esperado (deve iniciar com "### 1.")
    if not conteudo_markdown.strip().startswith("### 1"):
        raise ValueError("Formato de conteúdo inválido: seção inicial não encontrada (esperado início com '### 1.')")
    # 2. Separação do conteúdo em células markdown, dividindo pelas seções principais "### "
    partes = re.split(r'(?m)^### ', conteudo_markdown)
    # Se o conteúdo começar com "### ", a primeira parte será vazia; remove partes vazias resultantes
    partes = [parte for parte in partes if parte.strip() != ""]
    # Reconstitui cada parte com o cabeçalho "### " na primeira linha (foi removido pelo split)
    celulas_markdown = []
    for parte in partes:
        # Garante que cada parte inicie com "### " (adiciona se estiver faltando)
        texto_parte = parte.strip()
        if not texto_parte.startswith("###"):
            texto_parte = "### " + texto_parte
        celulas_markdown.append(texto_parte)
    # 3. Monta a estrutura de células do notebook com base nas partes obtidas
    cells = []
    for md in celulas_markdown:
        # Divide o texto da célula em linhas, preservando quebras de linha e espaços (splitlines com True mantém '\n')
        linhas = md.splitlines(True)
        cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": linhas
        }
        cells.append(cell)
    # 4. Monta o dicionário completo do notebook com metadata básica (compatível com Colab)
    notebook_dict = {
        "nbformat": 4,
        "nbformat_minor": 4,  # nbformat 4.x (usar minor 4 para compatibilidade com Colab)
        "metadata": {
            "colab": {
                "name": "Notebook Atualizado",  # nome visível no Colab (pode ser ajustado conforme necessidade)
                "toc_visible": True            # torna visível o sumário/TOC no Colab, facilitando navegação
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            }
        },
        "cells": cells
    }
    return notebook_dict

def enviar_notebook_para_drive(file_id: str, notebook_dict: dict):
    """
    Autentica na API do Google Drive e substitui o conteúdo do notebook existente identificado por file_id.
    Usa OAuth 2.0 para autorização, reutilizando um token salvo se disponível. Em caso de sucesso, o conteúdo 
    do arquivo no Drive é atualizado conforme o notebook_dict fornecido.
    """
    # Verifica se o arquivo de credenciais do OAuth existe antes de prosseguir
    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise FileNotFoundError("Arquivo 'client_secrets.json' não encontrado. Faça o download das credenciais OAuth do Google.")
    creds = None
    # Tenta carregar credenciais de um token salvo previamente
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None  # Em caso de erro ao ler o token (corrupção, escopo inválido, etc.)
    # Se não há credenciais válidas, inicia o fluxo de autenticação
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Atualiza token expirado automaticamente (requisição de refresh)
            creds.refresh(Request())
        else:
            # Executa o fluxo de autenticação no navegador (OAuth 2.0)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Abre uma janela do navegador para o usuário autorizar
        # Salva o token de acesso obtido para usos futuros, evitando autenticações manuais repetidas
        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(creds.to_json())
    # Chama a API do Google Drive para atualizar o conteúdo do arquivo
    try:
        service = build('drive', 'v3', credentials=creds)
        # Converte o notebook (dict) para uma string JSON e depois para bytes UTF-8
        notebook_json = json.dumps(notebook_dict, ensure_ascii=False)
        notebook_bytes = notebook_json.encode('utf-8')
        # Prepara o upload do conteúdo a partir de memória (sem gravar arquivo temporário em disco)
        media = MediaIoBaseUpload(io.BytesIO(notebook_bytes), mimetype='application/x-ipynb+json', resumable=False)
        # Executa a atualização do arquivo no Drive (mantém nome e propriedades, alterando apenas o conteúdo)
        service.files().update(fileId=file_id, media_body=media).execute()
    except HttpError as e:
        # Trata erros específicos da API do Drive (por exemplo, arquivo não encontrado ou permissões insuficientes)
        try:
            codigo = e.resp.status
        except Exception:
            codigo = None
        if codigo == 404:
            # ID não corresponde a um arquivo acessível (pode ser permissão ou ID incorreto)
            raise RuntimeError("Arquivo não encontrado no Drive ou você não tem permissão para acessá-lo.")
        else:
            # Tenta extrair mensagem de erro detalhada retornada pela API, se disponível
            mensagem_erro = ""
            try:
                erro_json = json.loads(e.content.decode("utf-8"))
                mensagem_erro = erro_json.get("error", {}).get("message", "")
            except Exception:
                mensagem_erro = str(e)
            raise RuntimeError(f"Erro da API do Drive: {mensagem_erro}")
    except Exception as e:
        # Erros gerais (por exemplo, problemas de conexão, interrupção, etc.)
        raise RuntimeError(f"Falha ao enviar o notebook: {e}")

def executar_interface() -> tuple[str, str]:
    """
    Cria a interface gráfica (Tkinter) para o usuário inserir o link do Colab e o conteúdo da aula.
    Retorna uma tupla (link, conteudo) com os dados inseridos, ou (None, None) se o usuário cancelar/fechar.
    """
    # Função interna a ser chamada quando o usuário clica no botão "Converter e Enviar"
    def on_submit():
        # Obtém valores dos campos de entrada
        user_link = entry_link.get().strip()
        user_content = text_content.get("1.0", tk.END)
        user_content = user_content.rstrip()  # remove newline extra no final do Text (evitar célula vazia)
        # Armazena os resultados e encerra a interface
        resultado['link'] = user_link
        resultado['content'] = user_content
        root.destroy()
    # Função interna para tratar cancelamento/fechamento da janela
    def on_cancel():
        resultado['link'] = None
        resultado['content'] = None
        root.destroy()
    # Inicializa a janela principal Tkinter
    root = tk.Tk()
    root.title("Atualizar Notebook Colab")
    # Define um ícone personalizado, se disponível (opcional)
    icon_path = os.path.join(BASE_PATH, "Icone.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass  # Se houver falha ao carregar o ícone, ignora (não crítico)
    # Aplica um estilo mais moderno (ttk) à interface
    style = ttk.Style(root)
    try:
        # Usa tema nativo do sistema se disponível (ex: 'vista' no Windows, 'clam' multiplataforma)
        if sys.platform.startswith("win"):
            style.theme_use("vista")
        else:
            style.theme_use("clam")
    except Exception:
        pass
    # Cria widgets da interface:
    # Rótulo e campo de texto para o link do Notebook Colab
    label_link = ttk.Label(root, text="Link do Notebook Colab:")
    entry_link = ttk.Entry(root, width=60)
    # Rótulo para a área de texto do conteúdo da aula
    label_content = ttk.Label(root, text="Conteúdo da Aula (Markdown):")
    # Caixa de texto com barra de rolagem para inserir/colar o conteúdo formatado
    text_content = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
    # Botões de ação
    btn_send = ttk.Button(root, text="Converter e Enviar", command=on_submit)
    btn_cancel = ttk.Button(root, text="Cancelar", command=on_cancel)
    # Posiciona os widgets usando grid com espaçamento (padx/pady)
    label_link.grid(row=0, column=0, padx=5, pady=5, sticky="E")
    entry_link.grid(row=0, column=1, padx=5, pady=5, sticky="WE")
    label_content.grid(row=1, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="W")
    text_content.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="WE")
    btn_send.grid(row=3, column=0, padx=5, pady=10, sticky="E")
    btn_cancel.grid(row=3, column=1, padx=5, pady=10, sticky="W")
    # Permite que a coluna 1 (com Entry/Text) expanda quando a janela é redimensionada
    root.grid_columnconfigure(1, weight=1)
    # Prepara dicionário para receber os resultados da interação do usuário
    resultado = {'link': None, 'content': None}
    # Define o protocolo para fechamento da janela (canto [X]) para acionar o cancelamento corretamente
    root.protocol("WM_DELETE_WINDOW", on_cancel)
    # Inicia o loop de eventos da interface (a execução ficará aqui até a janela ser fechada)
    root.mainloop()
    # Retorna os valores inseridos ou None se cancelado
    return resultado['link'], resultado['content']

def main():
    # Valida a existência do arquivo de credenciais antes de prosseguir
    if not os.path.exists(CLIENT_SECRETS_FILE):
        messagebox.showerror(
            "Erro de Pré-requisito",
            "Arquivo 'client_secrets.json' não encontrado.\nPor favor, baixe o arquivo de credenciais OAuth do Google Cloud e coloque-o junto ao executável."
        )
        return  # Interrompe a execução se não houver credenciais
    # Executa a interface gráfica para obter entradas do usuário
    link, conteudo = executar_interface()
    # Se o usuário fechou a janela ou clicou em cancelar, encerrar sem ações
    if not link or not conteudo:
        return
    # Tenta extrair o ID do arquivo do link fornecido
    try:
        file_id = extrair_id_do_link(link)
    except ValueError as e:
        messagebox.showerror("Link inválido", str(e))
        return
    # Tenta converter o conteúdo fornecido em um notebook .ipynb (formato JSON)
    try:
        notebook_dict = converter_conteudo_para_notebook(conteudo)
    except Exception as e:
        # Mostra mensagem de erro se o conteúdo não estiver no formato esperado ou ocorrer falha no parser
        messagebox.showerror("Erro de Parser", f"Não foi possível processar o conteúdo da aula.\n{e}")
        return
    # Tenta enviar (upload) o notebook para o Google Drive, substituindo o conteúdo existente
    try:
        enviar_notebook_para_drive(file_id, notebook_dict)
    except Exception as e:
        # Mostra mensagem de erro se ocorrer algum problema na atualização do arquivo no Drive
        messagebox.showerror("Erro ao Enviar para o Colab", str(e))
        return
    # Se tudo correr corretamente, informa o sucesso ao usuário
    messagebox.showinfo("Sucesso", "Notebook atualizado com sucesso no Google Colab!")

if __name__ == "__main__":
    main()
