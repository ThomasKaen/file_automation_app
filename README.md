📂 File Automation App

Batch utility tool for automating everyday file operations.
Organize, rename, and compress files with a simple GUI — no scripting required.

✨ Features

Bulk Rename

Add prefixes / suffixes

Find & replace (regex supported)

Sequential numbering

Recursive or flat mode

Smart Folder Sorting

By extension (.jpg, .pdf, etc.)

By file type (Images, Videos, Audio, Docs, Archives, Other)

By modification date (YYYY-MM)

By size bucket (small / medium / large)

Zip / Unzip

Create compressed archives of selected folders

Extract archives safely

Safe operations

Avoid overwriting with auto _2, _3 naming

Preview before execution

🖥️ GUI Preview

(Add screenshots here: e.g., ![Rename Tab](docs/rename_tab.png))

Tabbed interface: Rename, Sort, Zip

Log panel for real-time feedback

🚀 Installation

Clone the repo:

git clone git@github.com:ThomasKaen/file_automation_app.git
cd file_automation_app


Create virtual environment:

python -m venv .venv
.venv\Scripts\activate    # Windows
# or
source .venv/bin/activate # Linux/macOS


Install requirements (only standard lib + Tkinter needed):

pip install -e .

▶️ Usage

Run the GUI:

python -m file_automation_app.adapters.gui_tk


Or after installing with entrypoints (if set in pyproject.toml):

file-automation

📦 Project Structure
file_automation_app/
├─ core/        # Logic (services, models, utils)
├─ adapters/    # GUI (tkinter)
├─ version.py
└─ README.md

⚡ Tech Stack

Python 3.11+

Tkinter / ttk

Standard library only (shutil, pathlib, zipfile)

📌 Roadmap

 Add AES-encrypted zipping

 Add file converters (CSV → XLSX, DOCX → PDF, etc.)

 Export logs to text file

 Theming with ttkbootstrap

📜 License

