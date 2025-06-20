#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SCRIPT AUTOMATIZADO PARA CRIAR EXECUTÁVEL
Autor: Agente Colab Professional
Versão: 1.0
"""

import os
import sys
import subprocess
import platform

def verificar_dependencias():
  """Verificar e instalar dependências necessárias"""
  print("🔍 Verificando dependências...")
  
  try:
      import PyInstaller
      print("✅ PyInstaller já instalado")
  except ImportError:
      print("📦 Instalando PyInstaller...")
      subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
      print("✅ PyInstaller instalado com sucesso!")

def criar_executavel():
  """Criar executável do Agente Colab"""
  print("\n🚀 Criando executável do Agente Colab...")
  
  # Verificar se o arquivo existe
  if not os.path.exists("agente_colab.py"):
      print("❌ Arquivo 'agente_colab.py' não encontrado!")
      print("💡 Certifique-se de que o arquivo está no diretório atual.")
      return False
  
  # Comando para criar executável
  comando = [
      "pyinstaller",
      "--onefile",
      "--windowed",
      "--name=AgenteColab",
      "--clean",
      "--noconfirm",
      "agente_colab.py"
  ]
  
  # Adicionar ícone se existir
  if os.path.exists("icone.ico"):
      comando.insert(-1, "--icon=icone.ico")
      print("🎨 Ícone encontrado e adicionado!")
  
  try:
      print("⚙️ Executando PyInstaller...")
      resultado = subprocess.run(comando, capture_output=True, text=True)
      
      if resultado.returncode == 0:
          print("✅ Executável criado com sucesso!")
          print(f"📁 Localização: {os.path.abspath('dist/AgenteColab.exe')}")
          return True
      else:
          print("❌ Erro ao criar executável:")
          print(resultado.stderr)
          return False
          
  except Exception as e:
      print(f"❌ Erro inesperado: {e}")
      return False

def limpar_arquivos():
  """Limpar arquivos temporários"""
  print("\n🧹 Limpando arquivos temporários...")
  
  diretorios_para_remover = ['build', '__pycache__']
  arquivos_para_remover = ['AgenteColab.spec']
  
  for diretorio in diretorios_para_remover:
      if os.path.exists(diretorio):
          import shutil
          shutil.rmtree(diretorio)
          print(f"🗑️ Removido: {diretorio}")
  
  for arquivo in arquivos_para_remover:
      if os.path.exists(arquivo):
          os.remove(arquivo)
          print(f"🗑️ Removido: {arquivo}")

def main():
  """Função principal"""
  print("🚀 CRIADOR DE EXECUTÁVEL - AGENTE COLAB v4.0")
  print("=" * 50)
  
  # Verificar sistema operacional
  sistema = platform.system()
  print(f"💻 Sistema: {sistema}")
  
  # Verificar dependências
  verificar_dependencias()
  
  # Criar executável
  if criar_executavel():
      print("\n🎉 SUCESSO!")
      print("📁 Seu executável está na pasta 'dist/'")
      
      # Perguntar se quer limpar arquivos temporários
      resposta = input("\n🧹 Limpar arquivos temporários? (s/n): ").lower()
      if resposta in ['s', 'sim', 'y', 'yes']:
          limpar_arquivos()
      
      print("\n✅ Processo concluído!")
      print("🚀 Você pode executar o AgenteColab.exe agora!")
  else:
      print("\n❌ Falha ao criar executável.")
      print("💡 Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
  main()