# IA Agente de Preparação Do Colab

Um pequeno utilitário desktop para transformar automaticamente aulas no **Modo Aula** (markdown + blocos de código) em notebooks interativos do Google Colab, substituindo diretamente o conteúdo de um notebook existente no Drive.



## 📝 Descrição

Este projeto fornece um script Python (e um executável Windows gerado com PyInstaller) que:

1. Abre uma GUI simples (Tkinter/ttk) para o usuário colar:
   - **Link** de um notebook Colab (Drive ID).
   - **Texto** da aula no formato “Modo Aula” (markdown + blocos de código).
2. Parseia o conteúdo, preservando rigorosamente:
   - Marcação markdown.
   - Blocos de código Python.
   - Tags `<br>` (com espaços antes e depois, quando há texto adjacente).
3. Gera dinamicamente um arquivo `.ipynb` e o envia à API do Google Drive, substituindo o notebook existente.
4. Remove automaticamente seções opcionais (“Mergulhos Adicionais Opcionais”) e adiciona células de prática após cada bloco de código.

> **Nota**: Para garantir estabilidade, mantemos uma **versão antiga** do parser/GUI — foi a que apresentou comportamento 100% confiável. Futuras versões podem evoluir para adotar melhorias, mas esta traz garantia de funcionamento.

---

## 🚀 Funcionalidades

- 🎨 **GUI intuitiva**: Entrada de link e texto em uma única janela.
- 🔍 **Parser inteligente**:
  - Detecta seções `###`, blocos ```markdown```, ▶️…```python``` e 📖…```markdown```.
  - Preserva `<br>` com inserção de espaços quando necessário.
- 📄 **Geração de notebook**:
  - Cria células de markdown e código no formato Jupyter.
  - Adiciona automaticamente células vazias de prática após cada bloco de código.
- ☁️ **Upload direto** ao Google Drive via API v3.
- 🔒 **Autenticação OAuth2** com armazenamento de token (token.json).
- 🛠️ **Empacotado para Windows** como `.exe` (PyInstaller).

---

## 📦 Estrutura do Repositório

```text
IA_Agente-De-Preparacao-Do-Colab/
├── agente_colab.py        # Script principal em Python
├── agente_colab.spec      # Arquivo de build PyInstaller
├── client_secrets.json    # Credenciais OAuth2 (não comitar senhas!)
├── token.json             # Token de acesso Google Drive
├── Icone.ico              # Ícone da aplicação (Tkinter)
├── build/                 # Pasta temporária do PyInstaller
├── dist/                  # Executável gerado (dist/agente_colab.exe)
├── README.md              # Este arquivo
└── LICENSE.md             # Licença do projeto
````

---

## ⚙️ Pré-requisitos

1. **Python 3.8+** instalado (para rodar o `.py` diretamente).
2. Bibliotecas Python:

   ```bash
   pip install \
     google-auth \
     google-auth-oauthlib \
     google-auth-httplib2 \
     google-api-python-client \
     tkinter \
     pyinstaller
   ```
3. **client\_secrets.json** obtido no Google Cloud Console (OAuth 2.0 Client ID, Desktop).
4. Permissão de edição para o notebook de destino no Google Drive.

---

## 🚦 Como usar

### Rodando o script em Python

```bash
python agente_colab.py
```

1. Cole o **link** do seu notebook Colab (ex: `https://colab.research.google.com/drive/SEU_ID`).
2. Cole todo o **texto da aula** no formato “Modo Aula” (markdown + blocos de código).
3. Confirme para que ele parseie e envie o novo `.ipynb` ao Drive.

### Gerando o executável Windows

```bash
pyinstaller --noconfirm --onefile \
    --windowed agente_colab.spec
```

O binário resultante ficará em `dist/agente_colab.exe`. Basta copiar `client_secrets.json` e `token.json` para a mesma pasta do `.exe`.

---

## 📚 Exemplo de uso

1. Abra o programa.

2. Insira:

   * **Link do Colab**:
     `https://colab.research.google.com/drive/1lEuFgPC8vFYuOu3nyn3j20heIfaoG6Ag`
   * **Conteúdo Modo Aula** (exemplo):

     ```markdown
     ## 🎓 Aula sobre: A Função print() e F-Strings

     <br>

     ### 🧭 Sumário da Aula
     ...
     ```

3. Clique em **Converter e Enviar**.

4. Aguarde a confirmação de sucesso.

---

## 🔧 Contribuições

1. Abra um issue descrevendo a melhoria ou bug.
2. Fork o repositório e crie um branch (`feature/nova-funcionalidade`).
3. Faça seu desenvolvimento e adicione testes.
4. Envie um Pull Request.

---

## 📜 License

<details open>
<summary><b>CC BY-NC-ND 4.0 License</b></summary>

This repository is licensed under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/).

### What this means:

- ✅ **You can share** — You are free to copy and redistribute the material in any medium or format
- ❌ **No commercial use** — You may not use the material for commercial purposes
- ❌ **No derivatives** — You may not remix, transform, or build upon the material
- ✅ **Attribution required** — You must give appropriate credit, provide a link to the license, and indicate if changes were made

For the complete license terms, please see the [LICENSE.md](LICENSE.md) file.
</details>

## 📫 Contact

For questions or suggestions about this repository, please contact me through GitHub.

---

*Feito com ❤️ por [Laurentius96](https://github.com/Laurentius96), baseada em uma versão estável anterior que comprovou total confiabilidade.*


