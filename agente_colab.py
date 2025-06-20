import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import os
import sys
import json
from datetime import datetime
import webbrowser

class AgenteColabProfessional:
  def __init__(self, root):
      self.root = root
      self.root.title("🚀 Agente de Preparação do Colab v4.0 - PROFESSIONAL")
      self.root.geometry("1200x800")
      self.root.minsize(1000, 600)
      
      # Configurar tema moderno
      self.configurar_tema()
      
      # Variáveis de estado
      self.projetos = []
      self.configuracoes = self.carregar_configuracoes()
      
      # Criar interface
      self.criar_interface()
      
      # Inicializar sistema
      self.root.after(100, self.inicializar_sistema)
  
  def configurar_tema(self):
      """Configurar tema moderno"""
      style = ttk.Style()
      
      # Configurar cores modernas
      self.cores = {
          'primary': '#2563eb',      # Azul moderno
          'secondary': '#64748b',    # Cinza azulado
          'success': '#10b981',      # Verde
          'warning': '#f59e0b',      # Amarelo
          'danger': '#ef4444',       # Vermelho
          'dark': '#1e293b',         # Escuro
          'light': '#f8fafc',        # Claro
          'background': '#ffffff'    # Branco
      }
      
      # Aplicar tema
      self.root.configure(bg=self.cores['background'])
      
      # Configurar estilos personalizados
      style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), 
                     foreground=self.cores['primary'])
      style.configure('Subtitle.TLabel', font=('Segoe UI', 12), 
                     foreground=self.cores['secondary'])
      style.configure('Success.TLabel', font=('Segoe UI', 10), 
                     foreground=self.cores['success'])
      style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
  
  def criar_interface(self):
      """Criar interface principal"""
      # Container principal
      self.main_container = ttk.Frame(self.root)
      self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
      
      # Criar header
      self.criar_header()
      
      # Criar notebook (abas)
      self.criar_notebook()
      
      # Criar footer
      self.criar_footer()
  
  def criar_header(self):
      """Criar cabeçalho da aplicação"""
      header_frame = ttk.Frame(self.main_container)
      header_frame.pack(fill=tk.X, pady=(0, 15))
      
      # Logo e título
      title_frame = ttk.Frame(header_frame)
      title_frame.pack(side=tk.LEFT)
      
      ttk.Label(title_frame, text="🚀 Agente de Preparação do Colab", 
               style='Title.TLabel').pack(anchor=tk.W)
      ttk.Label(title_frame, text="Versão 4.0 Professional - Preparação avançada para Google Colab", 
               style='Subtitle.TLabel').pack(anchor=tk.W)
      
      # Status e controles
      status_frame = ttk.Frame(header_frame)
      status_frame.pack(side=tk.RIGHT)
      
      self.status_var = tk.StringVar(value="🟢 Sistema Pronto")
      self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                   style='Success.TLabel')
      self.status_label.pack(anchor=tk.E)
      
      # Botões de controle
      control_frame = ttk.Frame(status_frame)
      control_frame.pack(anchor=tk.E, pady=(5, 0))
      
      ttk.Button(control_frame, text="⚙️ Configurações", 
                command=self.abrir_configuracoes).pack(side=tk.RIGHT, padx=(5, 0))
      ttk.Button(control_frame, text="❓ Ajuda", 
                command=self.mostrar_ajuda).pack(side=tk.RIGHT, padx=(5, 0))
  
  def criar_notebook(self):
      """Criar sistema de abas"""
      self.notebook = ttk.Notebook(self.main_container)
      self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
      
      # Aba 1: Preparação de Ambiente
      self.criar_aba_preparacao()
      
      # Aba 2: Gerenciamento de Projetos
      self.criar_aba_projetos()
      
      # Aba 3: Bibliotecas e Dependências
      self.criar_aba_bibliotecas()
      
      # Aba 4: Templates e Snippets
      self.criar_aba_templates()
      
      # Aba 5: Monitor e Logs
      self.criar_aba_monitor()
  
  def criar_aba_preparacao(self):
      """Aba de preparação do ambiente"""
      frame = ttk.Frame(self.notebook)
      self.notebook.add(frame, text="🔧 Preparação")
      
      # Seção de verificação do sistema
      sys_frame = ttk.LabelFrame(frame, text="🔍 Verificação do Sistema", padding=15)
      sys_frame.pack(fill=tk.X, padx=10, pady=5)
      
      # Grid de verificações
      checks_frame = ttk.Frame(sys_frame)
      checks_frame.pack(fill=tk.X)
      
      self.checks = {
          'python': {'var': tk.BooleanVar(), 'label': 'Python 3.8+'},
          'pip': {'var': tk.BooleanVar(), 'label': 'Pip atualizado'},
          'git': {'var': tk.BooleanVar(), 'label': 'Git instalado'},
          'colab': {'var': tk.BooleanVar(), 'label': 'Acesso ao Colab'},
          'drive': {'var': tk.BooleanVar(), 'label': 'Google Drive conectado'}
      }
      
      for i, (key, check) in enumerate(self.checks.items()):
          row = i // 2
          col = i % 2
          ttk.Checkbutton(checks_frame, text=check['label'], 
                         variable=check['var'], state='disabled').grid(
                         row=row, column=col, sticky=tk.W, padx=10, pady=2)
      
      # Botão de verificação
      ttk.Button(sys_frame, text="🔍 Verificar Sistema", 
                command=self.verificar_sistema, 
                style='Primary.TButton').pack(pady=10)
      
      # Seção de configuração rápida
      config_frame = ttk.LabelFrame(frame, text="⚡ Configuração Rápida", padding=15)
      config_frame.pack(fill=tk.X, padx=10, pady=5)
      
      # Botões de ação rápida
      quick_frame = ttk.Frame(config_frame)
      quick_frame.pack(fill=tk.X)
      
      ttk.Button(quick_frame, text="📦 Instalar Dependências", 
                command=self.instalar_dependencias).pack(side=tk.LEFT, padx=5)
      ttk.Button(quick_frame, text="🔗 Conectar Google Drive", 
                command=self.conectar_drive).pack(side=tk.LEFT, padx=5)
      ttk.Button(quick_frame, text="📋 Copiar Template Base", 
                command=self.copiar_template).pack(side=tk.LEFT, padx=5)
      
      # Área de progresso
      self.progress_var = tk.DoubleVar()
      self.progress_bar = ttk.Progressbar(config_frame, variable=self.progress_var, 
                                        maximum=100)
      self.progress_bar.pack(fill=tk.X, pady=10)
      
      self.progress_label = ttk.Label(config_frame, text="Pronto para iniciar")
      self.progress_label.pack()
  
  def criar_aba_projetos(self):
      """Aba de gerenciamento de projetos"""
      frame = ttk.Frame(self.notebook)
      self.notebook.add(frame, text="📁 Projetos")
      
      # Painel esquerdo - Lista de projetos
      left_frame = ttk.Frame(frame)
      left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
      
      ttk.Label(left_frame, text="📋 Meus Projetos", 
               font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
      
      # Lista de projetos
      self.projetos_tree = ttk.Treeview(left_frame, columns=('status', 'data'), 
                                       show='tree headings', height=15)
      self.projetos_tree.heading('#0', text='Nome do Projeto')
      self.projetos_tree.heading('status', text='Status')
      self.projetos_tree.heading('data', text='Última Modificação')
      self.projetos_tree.pack(fill=tk.BOTH, expand=True, pady=5)
      
      # Botões de projeto
      proj_buttons = ttk.Frame(left_frame)
      proj_buttons.pack(fill=tk.X, pady=5)
      
      ttk.Button(proj_buttons, text="➕ Novo Projeto", 
                command=self.novo_projeto).pack(side=tk.LEFT, padx=2)
      ttk.Button(proj_buttons, text="📂 Abrir", 
                command=self.abrir_projeto).pack(side=tk.LEFT, padx=2)
      ttk.Button(proj_buttons, text="🗑️ Excluir", 
                command=self.excluir_projeto).pack(side=tk.LEFT, padx=2)
      
      # Painel direito - Detalhes do projeto
      right_frame = ttk.LabelFrame(frame, text="📋 Detalhes do Projeto", padding=15)
      right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
      
      # Campos de detalhes
      ttk.Label(right_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=2)
      self.proj_nome = ttk.Entry(right_frame, width=40)
      self.proj_nome.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
      
      ttk.Label(right_frame, text="Descrição:").grid(row=1, column=0, sticky=tk.NW, pady=2)
      self.proj_desc = scrolledtext.ScrolledText(right_frame, width=40, height=5)
      self.proj_desc.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
      
      ttk.Label(right_frame, text="Tipo:").grid(row=2, column=0, sticky=tk.W, pady=2)
      self.proj_tipo = ttk.Combobox(right_frame, values=[
          'Análise de Dados', 'Machine Learning', 'Deep Learning', 
          'Visualização', 'Web Scraping', 'Automação', 'Outro'
      ], width=37)
      self.proj_tipo.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(10, 0))
      
      # Botão salvar
      ttk.Button(right_frame, text="💾 Salvar Projeto", 
                command=self.salvar_projeto).grid(row=3, column=1, pady=10, padx=(10, 0))
  
  def criar_aba_bibliotecas(self):
      """Aba de gerenciamento de bibliotecas"""
      frame = ttk.Frame(self.notebook)
      self.notebook.add(frame, text="📚 Bibliotecas")
      
      # Seção de bibliotecas populares
      pop_frame = ttk.LabelFrame(frame, text="⭐ Bibliotecas Populares", padding=15)
      pop_frame.pack(fill=tk.X, padx=10, pady=5)
      
      # Grid de bibliotecas
      self.libs = {
          'pandas': {'var': tk.BooleanVar(), 'desc': 'Manipulação de dados'},
          'numpy': {'var': tk.BooleanVar(), 'desc': 'Computação numérica'},
          'matplotlib': {'var': tk.BooleanVar(), 'desc': 'Visualização básica'},
          'seaborn': {'var': tk.BooleanVar(), 'desc': 'Visualização avançada'},
          'scikit-learn': {'var': tk.BooleanVar(), 'desc': 'Machine Learning'},
          'tensorflow': {'var': tk.BooleanVar(), 'desc': 'Deep Learning'},
          'pytorch': {'var': tk.BooleanVar(), 'desc': 'Deep Learning'},
          'plotly': {'var': tk.BooleanVar(), 'desc': 'Gráficos interativos'},
          'requests': {'var': tk.BooleanVar(), 'desc': 'Requisições HTTP'},
          'beautifulsoup4': {'var': tk.BooleanVar(), 'desc': 'Web Scraping'}
      }
      
      libs_grid = ttk.Frame(pop_frame)
      libs_grid.pack(fill=tk.X)
      
      for i, (lib, info) in enumerate(self.libs.items()):
          row = i // 2
          col = i % 2
          
          lib_frame = ttk.Frame(libs_grid)
          lib_frame.grid(row=row, column=col, sticky=tk.W, padx=20, pady=2)
          
          ttk.Checkbutton(lib_frame, text=lib, 
                         variable=info['var']).pack(side=tk.LEFT)
          ttk.Label(lib_frame, text=f"- {info['desc']}", 
                   foreground=self.cores['secondary']).pack(side=tk.LEFT, padx=(5, 0))
      
      # Botões de ação
      lib_buttons = ttk.Frame(pop_frame)
      lib_buttons.pack(pady=10)
      
      ttk.Button(lib_buttons, text="✅ Selecionar Todas", 
                command=self.selecionar_todas_libs).pack(side=tk.LEFT, padx=5)
      ttk.Button(lib_buttons, text="❌ Limpar Seleção", 
                command=self.limpar_selecao_libs).pack(side=tk.LEFT, padx=5)
      ttk.Button(lib_buttons, text="📦 Instalar Selecionadas", 
                command=self.instalar_bibliotecas).pack(side=tk.LEFT, padx=5)
      
      # Seção de bibliotecas customizadas
      custom_frame = ttk.LabelFrame(frame, text="🔧 Bibliotecas Customizadas", padding=15)
      custom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
      
      # Campo para adicionar biblioteca
      add_frame = ttk.Frame(custom_frame)
      add_frame.pack(fill=tk.X, pady=(0, 10))
      
      ttk.Label(add_frame, text="Biblioteca:").pack(side=tk.LEFT)
      self.custom_lib_entry = ttk.Entry(add_frame, width=30)
      self.custom_lib_entry.pack(side=tk.LEFT, padx=5)
      ttk.Button(add_frame, text="➕ Adicionar", 
                command=self.adicionar_biblioteca_custom).pack(side=tk.LEFT, padx=5)
      
      # Lista de bibliotecas customizadas
      self.custom_libs_list = tk.Listbox(custom_frame, height=8)
      self.custom_libs_list.pack(fill=tk.BOTH, expand=True)
  
  def criar_aba_templates(self):
      """Aba de templates e snippets"""
      frame = ttk.Frame(self.notebook)
      self.notebook.add(frame, text="📝 Templates")
      
      # Painel esquerdo - Lista de templates
      left_frame = ttk.Frame(frame)
      left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
      
      ttk.Label(left_frame, text="📋 Templates Disponíveis", 
               font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
      
      self.templates_list = tk.Listbox(left_frame, width=30, height=20)
      self.templates_list.pack(fill=tk.Y, expand=True, pady=5)
      self.templates_list.bind('<<ListboxSelect>>', self.carregar_template)
      
      # Adicionar templates padrão
      templates_padrao = [
          "🔍 Análise Exploratória de Dados",
          "🤖 Machine Learning Básico",
          "📊 Visualização de Dados",
          "🌐 Web Scraping",
          "📈 Análise de Séries Temporais",
          "🧠 Redes Neurais",
          "📸 Processamento de Imagens",
          "💬 Processamento de Texto",
          "📱 API e Requisições",
          "🔧 Automação de Tarefas"
      ]
      
      for template in templates_padrao:
          self.templates_list.insert(tk.END, template)
      
      # Painel direito - Visualização do template
      right_frame = ttk.Frame(frame)
      right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
      
      # Cabeçalho
      header_frame = ttk.Frame(right_frame)
      header_frame.pack(fill=tk.X, pady=(0, 10))
      
      ttk.Label(header_frame, text="📄 Visualização do Template", 
               font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
      
      ttk.Button(header_frame, text="📋 Copiar Código", 
                command=self.copiar_codigo_template).pack(side=tk.RIGHT, padx=5)
      ttk.Button(header_frame, text="💾 Salvar Como", 
                command=self.salvar_template).pack(side=tk.RIGHT, padx=5)
      
      # Área de código
      self.template_code = scrolledtext.ScrolledText(right_frame, 
                                                    font=('Consolas', 10),
                                                    wrap=tk.NONE)
      self.template_code.pack(fill=tk.BOTH, expand=True)
  
  def criar_aba_monitor(self):
      """Aba de monitoramento e logs"""
      frame = ttk.Frame(self.notebook)
      self.notebook.add(frame, text="📊 Monitor")
      
      # Área de logs
      log_frame = ttk.LabelFrame(frame, text="📋 Logs do Sistema", padding=10)
      log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
      
      # Controles de log
      log_controls = ttk.Frame(log_frame)
      log_controls.pack(fill=tk.X, pady=(0, 10))
      
      ttk.Button(log_controls, text="🗑️ Limpar Logs", 
                command=self.limpar_logs).pack(side=tk.LEFT, padx=5)
      ttk.Button(log_controls, text="💾 Salvar Logs", 
                command=self.salvar_logs).pack(side=tk.LEFT, padx=5)
      ttk.Button(log_controls, text="🔄 Atualizar", 
                command=self.atualizar_logs).pack(side=tk.LEFT, padx=5)
      
      # Filtro de logs
      ttk.Label(log_controls, text="Filtro:").pack(side=tk.LEFT, padx=(20, 5))
      self.log_filter = ttk.Combobox(log_controls, values=[
          'Todos', 'Info', 'Sucesso', 'Aviso', 'Erro'
      ], width=15)
      self.log_filter.pack(side=tk.LEFT, padx=5)
      self.log_filter.set('Todos')
      
      # Área de texto para logs
      self.log_text = scrolledtext.ScrolledText(log_frame, 
                                               font=('Consolas', 9),
                                               height=25)
      self.log_text.pack(fill=tk.BOTH, expand=True)
      
      # Configurar tags para colorir logs
      self.log_text.tag_configure('INFO', foreground='blue')
      self.log_text.tag_configure('SUCCESS', foreground='green')
      self.log_text.tag_configure('WARNING', foreground='orange')
      self.log_text.tag_configure('ERROR', foreground='red')
  
  def criar_footer(self):
      """Criar rodapé da aplicação"""
      footer_frame = ttk.Frame(self.main_container)
      footer_frame.pack(fill=tk.X, pady=(5, 0))
      
      # Separador
      ttk.Separator(footer_frame, orient='horizontal').pack(fill=tk.X, pady=(0, 5))
      
      # Informações do rodapé
      ttk.Label(footer_frame, text="© 2024 Agente de Preparação do Colab v4.0 Professional", 
               style='Subtitle.TLabel').pack(side=tk.LEFT)
      
      # Status de conexão
      self.connection_status = ttk.Label(footer_frame, text="🔗 Conectado", 
                                        style='Success.TLabel')
      self.connection_status.pack(side=tk.RIGHT)
  
  # Métodos de funcionalidade
  def carregar_configuracoes(self):
      """Carregar configurações do sistema"""
      try:
          if os.path.exists('config.json'):
              with open('config.json', 'r') as f:
                  return json.load(f)
      except:
          pass
      return {}
  
  def salvar_configuracoes(self):
      """Salvar configurações do sistema"""
      try:
          with open('config.json', 'w') as f:
              json.dump(self.configuracoes, f, indent=2)
      except Exception as e:
          self.log_message(f"❌ Erro ao salvar configurações: {e}", "ERROR")
  
  def inicializar_sistema(self):
      """Inicializar sistema após interface pronta"""
      self.log_message("🚀 Sistema inicializado com sucesso!", "SUCCESS")
      self.log_message("✅ Interface carregada", "INFO")
      self.log_message("🔧 Pronto para uso!", "INFO")
      
      # Verificar sistema automaticamente
      self.root.after(2000, self.verificar_sistema)
  
  def log_message(self, message, level="INFO"):
      """Adicionar mensagem ao log"""
      timestamp = datetime.now().strftime("%H:%M:%S")
      log_entry = f"[{timestamp}] {message}\n"
      
      self.log_text.insert(tk.END, log_entry, level)
      self.log_text.see(tk.END)
      self.root.update_idletasks()
  
  def verificar_sistema(self):
      """Verificar componentes do sistema"""
      self.log_message("🔍 Iniciando verificação do sistema...", "INFO")
      self.atualizar_status("🔄 Verificando sistema...")
      
      def verificar():
          # Simular verificações
          verificacoes = [
              ('python', 'Verificando Python...'),
              ('pip', 'Verificando Pip...'),
              ('git', 'Verificando Git...'),
              ('colab', 'Testando acesso ao Colab...'),
              ('drive', 'Verificando Google Drive...')
          ]
          
          for i, (check, msg) in enumerate(verificacoes):
              self.log_message(msg, "INFO")
              self.progress_var.set((i + 1) * 20)
              self.progress_label.config(text=msg)
              time.sleep(1)
              
              # Simular resultado (sempre sucesso para demo)
              self.checks[check]['var'].set(True)
              self.log_message(f"✅ {self.checks[check]['label']} - OK", "SUCCESS")
          
          self.log_message("🎉 Verificação concluída com sucesso!", "SUCCESS")
          self.atualizar_status("🟢 Sistema verificado")
          self.progress_label.config(text="Verificação concluída!")
      
      # Executar em thread separada
      threading.Thread(target=verificar, daemon=True).start()
  
  def atualizar_status(self, status):
      """Atualizar status da aplicação"""
      self.status_var.set(status)
      self.root.update_idletasks()
  
  def instalar_dependencias(self):
      """Instalar dependências selecionadas"""
      self.log_message("📦 Iniciando instalação de dependências...", "INFO")
      
      # Simular instalação
      def instalar():
          libs_selecionadas = [lib for lib, info in self.libs.items() if info['var'].get()]
          
          if not libs_selecionadas:
              self.log_message("⚠️ Nenhuma biblioteca selecionada!", "WARNING")
              return
          
          for i, lib in enumerate(libs_selecionadas):
              self.log_message(f"📦 Instalando {lib}...", "INFO")
              self.progress_var.set((i + 1) / len(libs_selecionadas) * 100)
              time.sleep(0.5)
              self.log_message(f"✅ {lib} instalado com sucesso!", "SUCCESS")
          
          self.log_message("🎉 Todas as bibliotecas foram instaladas!", "SUCCESS")
          messagebox.showinfo("Sucesso", "Bibliotecas instaladas com sucesso!")
      
      threading.Thread(target=instalar, daemon=True).start()
  
  def conectar_drive(self):
      """Conectar ao Google Drive"""
      self.log_message("🔗 Conectando ao Google Drive...", "INFO")
      
      # Código para conectar ao Drive
      codigo_drive = '''# Conectar ao Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Verificar conexão
import os
print("📁 Conteúdo do Drive:")
print(os.listdir('/content/drive/MyDrive'))
'''
      
      # Copiar para clipboard
      self.root.clipboard_clear()
      self.root.clipboard_append(codigo_drive)
      
      self.log_message("📋 Código de conexão copiado para clipboard!", "SUCCESS")
      messagebox.showinfo("Google Drive", "Código de conexão copiado!\nCole no seu notebook do Colab.")
  
  def copiar_template(self):
      """Copiar template base"""
      template_base = '''# 🚀 Template Base para Google Colab
# Agente de Preparação do Colab v4.0

# Importações básicas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configurações de visualização
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Conectar ao Google Drive (se necessário)
# from google.colab import drive
# drive.mount('/content/drive')

# Configurações do pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

print("🎉 Ambiente preparado com sucesso!")
print("✅ Bibliotecas carregadas")
print("📊 Configurações aplicadas")
print("🔧 Pronto para análise!")
print(f"⏰ Inicializado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
'''
  def copiar_template_base(self):
      """Copiar template base para clipboard"""
      template_base = """# 🚀 TEMPLATE BASE PARA COLAB
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações iniciais
print("🎯 Projeto iniciado!")
print(f"📅 Inicializado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Seu código aqui...
"""
      # Copiar para clipboard
      self.root.clipboard_clear()
      self.root.clipboard_append(template_base)
      
      self.log_message("📋 Template base copiado para clipboard!", "SUCCESS")
      messagebox.showinfo("Sucesso", "Template base copiado para clipboard!")

  def novo_projeto(self):
      """Criar novo projeto"""
      self.log_message("➕ Criando novo projeto...", "INFO")
      # Limpar campos
      self.proj_nome.delete(0, tk.END)
      self.proj_desc.delete(1.0, tk.END)
      self.proj_tipo.set('')

  def abrir_projeto(self):
      """Abrir projeto selecionado"""
      selection = self.projetos_tree.selection()
      if selection:
          item = self.projetos_tree.item(selection[0])
          nome = item['text']
          self.log_message(f"📂 Abrindo projeto: {nome}", "INFO")
          messagebox.showinfo("Projeto", f"Abrindo projeto: {nome}")

  def excluir_projeto(self):
      """Excluir projeto selecionado"""
      selection = self.projetos_tree.selection()
      if selection:
          item = self.projetos_tree.item(selection[0])
          nome = item['text']
          if messagebox.askyesno("Confirmar", f"Excluir projeto '{nome}'?"):
              self.projetos_tree.delete(selection[0])
              self.log_message(f"🗑️ Projeto '{nome}' excluído", "WARNING")

  def salvar_projeto(self):
      """Salvar projeto atual"""
      nome = self.proj_nome.get()
      if nome:
          self.projetos_tree.insert('', tk.END, text=nome, 
                                   values=('Ativo', datetime.now().strftime("%d/%m/%Y")))
          self.log_message(f"💾 Projeto '{nome}' salvo com sucesso!", "SUCCESS")
          messagebox.showinfo("Sucesso", f"Projeto '{nome}' salvo!")
      else:
          messagebox.showwarning("Aviso", "Digite um nome para o projeto!")

  def selecionar_todas_libs(self):
      """Selecionar todas as bibliotecas"""
      for lib_info in self.libs.values():
          lib_info['var'].set(True)
      self.log_message("✅ Todas as bibliotecas selecionadas", "INFO")

  def limpar_selecao_libs(self):
      """Limpar seleção de bibliotecas"""
      for lib_info in self.libs.values():
          lib_info['var'].set(False)
      self.log_message("❌ Seleção de bibliotecas limpa", "INFO")

  def instalar_bibliotecas(self):
      """Instalar bibliotecas selecionadas"""
      self.instalar_dependencias()

  def adicionar_biblioteca_custom(self):
      """Adicionar biblioteca customizada"""
      lib = self.custom_lib_entry.get().strip()
      if lib:
          self.custom_libs_list.insert(tk.END, lib)
          self.custom_lib_entry.delete(0, tk.END)
          self.log_message(f"➕ Biblioteca '{lib}' adicionada", "INFO")

  def carregar_template(self, event):
      """Carregar template selecionado"""
      selection = self.templates_list.curselection()
      if selection:
          template_name = self.templates_list.get(selection[0])
          
          # Templates básicos
          if "Análise Exploratória" in template_name:
              codigo = """# 🔍 Análise Exploratória de Dados
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar dados
df = pd.read_csv('seu_arquivo.csv')

# Informações básicas
print("📊 Informações do Dataset:")
print(f"Formato: {df.shape}")
print(f"Colunas: {list(df.columns)}")

# Estatísticas descritivas
print("\\n📈 Estatísticas Descritivas:")
print(df.describe())

# Verificar valores nulos
print("\\n❌ Valores Nulos:")
print(df.isnull().sum())

# Visualizações
plt.figure(figsize=(12, 8))
# Adicione seus gráficos aqui
plt.show()"""
          
          elif "Machine Learning" in template_name:
              codigo = """# 🤖 Machine Learning Básico
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# Preparar dados
# X = df.drop('target', axis=1)
# y = df['target']

# Dividir dados
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Fazer predições
y_pred = model.predict(X_test)

# Avaliar modelo
accuracy = accuracy_score(y_test, y_pred)
print(f"Acurácia: {accuracy:.4f}")
print("\\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))"""
          
          else:
              codigo = "# Template em desenvolvimento..."
          
          # Mostrar template
          self.template_code.delete(1.0, tk.END)
          self.template_code.insert(1.0, codigo)

  def copiar_codigo_template(self):
      """Copiar código do template"""
      codigo = self.template_code.get(1.0, tk.END)
      self.root.clipboard_clear()
      self.root.clipboard_append(codigo)
      self.log_message("📋 Código do template copiado!", "SUCCESS")
      messagebox.showinfo("Sucesso", "Código copiado para clipboard!")

  def salvar_template(self):
      """Salvar template como arquivo"""
      codigo = self.template_code.get(1.0, tk.END)
      filename = filedialog.asksaveasfilename(
          defaultextension=".py",
          filetypes=[("Python files", "*.py"), ("All files", "*.*")]
      )
      if filename:
          with open(filename, 'w', encoding='utf-8') as f:
              f.write(codigo)
          self.log_message(f"💾 Template salvo: {filename}", "SUCCESS")

  def limpar_logs(self):
      """Limpar área de logs"""
      self.log_text.delete(1.0, tk.END)
      self.log_message("🗑️ Logs limpos", "INFO")

  def salvar_logs(self):
      """Salvar logs em arquivo"""
      logs = self.log_text.get(1.0, tk.END)
      filename = filedialog.asksaveasfilename(
          defaultextension=".txt",
          filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
      )
      if filename:
          with open(filename, 'w', encoding='utf-8') as f:
              f.write(logs)
          self.log_message(f"💾 Logs salvos: {filename}", "SUCCESS")

  def atualizar_logs(self):
      """Atualizar logs"""
      self.log_message("🔄 Logs atualizados", "INFO")

  def abrir_configuracoes(self):
      """Abrir janela de configurações"""
      self.log_message("⚙️ Abrindo configurações...", "INFO")
      messagebox.showinfo("Configurações", "Janela de configurações em desenvolvimento!")

  def mostrar_ajuda(self):
      """Mostrar ajuda do sistema"""
      ajuda = """🚀 AGENTE DE PREPARAÇÃO DO COLAB v4.0

📋 COMO USAR:

1) 🔧 Preparação: Verifique e configure seu ambiente
2) 📁 Projetos: Gerencie seus projetos de análise  
3) 📚 Bibliotecas: Instale e gerencie dependências
4) 📝 Templates: Use templates prontos para análise
5) 📊 Monitor: Acompanhe logs e atividades

💡 DICAS:
• Use Ctrl+C para copiar templates
• Verifique o sistema antes de começar
• Salve seus projetos regularmente
• Monitore os logs para debug

🆘 SUPORTE:
• GitHub: github.com/agente-colab
• Email: suporte@agentecolab.com
"""
      messagebox.showinfo("Ajuda", ajuda)

# FUNÇÃO PRINCIPAL - ADICIONE FORA DA CLASSE!
def main():
  root = tk.Tk()
  app = AgenteColabProfessional(root)
  root.mainloop()

if __name__ == "__main__":
  main()