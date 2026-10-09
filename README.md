# Canteen Management System

A small Flask + SQLite web application for managing canteen menu items, stock, availability, and customer orders.

## Features
- Dashboard statistics for menu items, availability, orders, and sales
- Add, edit, delete, and toggle availability for menu items
- Place customer orders with stock validation
- Automatic stock deduction after a successful order
- Recent order history
- SQLite database is created automatically on first run

## Requirements
- Python 3.10 or newer
- Flask

## Run locally
1. Open this folder in VS Code.
2. Open the terminal in this folder.
3. Create a virtual environment (recommended):

   ```bash
   python -m venv .venv
   ```

4. Activate it on Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   python server.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

The `canteen.db` SQLite database is generated automatically and should normally not be committed to GitHub.

## Project structure
```text
canteen-management-system/
├── server.py
├── requirements.txt
├── README.md
├── .gitignore
└── templates/
    └── index.html
```

## Note
This is a clean, standalone implementation inspired by a typical canteen management workflow. It is not an export of the Base44 site's private source code, so its exact design and features may differ from the deployed site.
