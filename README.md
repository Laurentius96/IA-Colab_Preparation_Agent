 <div align="center">  <h1> IA | Colab Preparation Agent </div>

A lightweight desktop utility to automatically transform **Modo Aula** lessons (Markdown + code blocks) into interactive Google Colab notebooks by replacing an existing notebook’s contents on Drive.

---

## 📝 Overview

This project provides a Python script (and a Windows executable built with PyInstaller) that:

1. Presents a simple GUI (Tkinter/ttk) where the user pastes:

   * A **Colab link** (Drive ID).
   * The lesson **content** in “Modo Aula” format (Markdown + code blocks).
2. Parses the input, preserving:

   * Markdown structure.
   * Python code blocks.
   * `<br>` tags (ensuring spaces before/after when adjacent to text).
3. Dynamically generates a `.ipynb` file and uploads it via the Google Drive API (v3) to overwrite the existing notebook.
4. Automatically strips optional sections (“Mergulhos Adicionais Opcionais”) and injects “practice” cells after each code block.

> **Note:** For rock-solid stability, we maintain an **older stable version** of the parser/GUI which proved 100 % reliable. Future updates may refine this, but this version guarantees predictable behavior.

---

## 🚀 Features

* 🎨 **Intuitive GUI**: Single window for link & lesson input
* 🔍 **Smart Parser**

  * Detects `###` headings, \`\`\`\`markdown\`\`, `▶️ … ```python```, and `📖 … `markdown`.
  * Preserves `<br>` tags with appropriate spacing.
* 📄 **Notebook Generation**

  * Creates Jupyter-style markdown and code cells.
  * Inserts empty “practice” cells automatically after each code block.
* ☁️ **Direct Drive Upload** via Google Drive API
* 🔒 **OAuth2 Authentication**, with token storage (`token.json`)
* 🛠️ **Single-file Windows executable** via PyInstaller

---

## 📦 Repository Structure

```text
IA_Agente-De-Preparacao-Do-Colab/
├── agente_colab.py        # Main Python script
├── agente_colab.spec      # PyInstaller build spec
├── client_secrets.json    # OAuth2 credentials (do NOT commit secrets)
├── token.json             # Stored OAuth token
├── Icone.ico              # Custom app icon for Tkinter
├── build/                 # PyInstaller build artifacts
├── dist/                  # Generated executable (dist/agente_colab.exe)
├── README.md              # This README
└── LICENSE.md             # Project license
```

---

## ⚙️ Prerequisites

1. **Python 3.8+** installed (if running the `.py` directly)
2. Install dependencies:

   ```bash
   pip install \
     google-auth \
     google-auth-oauthlib \
     google-auth-httplib2 \
     google-api-python-client \
     pyinstaller
   ```

   *(Tkinter is included with standard Python on Windows and macOS.)*
3. **client\_secrets.json** from Google Cloud Console (OAuth 2.0 Desktop ID).
4. **Edit permission** on the target Colab notebook in Google Drive.

---

## 🚦 Usage

### Running the Python script

```bash
python agente_colab.py
```

1. Paste your **Colab link** (e.g. `https://colab.research.google.com/drive/SEU_ID`).
2. Paste the entire **lesson content** in “Modo Aula” format.
3. Click **Convert & Send** and wait for confirmation.

### Building the Windows Executable

```bash
pyinstaller --noconfirm --onefile --windowed agente_colab.spec
```

Place `client_secrets.json` (and `token.json` after first run) beside `dist/agente_colab.exe`.

---

## 📚 Example

1. Launch the application.
2. Enter:

   * **Colab Link**:

     ```text
     https://colab.research.google.com/drive/1lEuFgPC8vFYuOu3nyn3j20heIfaoG6Ag
     ```
   * **Lesson Content**:

     ```markdown
     ### 3. 🕸️ Profundezas e Conexões

     <br>
     `print()` is widely replaced by *logging* frameworks in production…
     <br>

     ---
     <br>
     ```
3. Click **Convert & Send**.
4. See success message once the notebook is updated.

---

## 🔧 Contributing

1. Open an issue to discuss your idea or bug.
2. Fork the repo & create a branch (`feature/awesome`).
3. Implement, document, add tests.
4. Submit a Pull Request.

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


