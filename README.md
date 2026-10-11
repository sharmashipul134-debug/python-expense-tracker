# PennyWise — Python Expense Tracker

A responsive personal finance dashboard built with **Python, Flask, SQLite, HTML, and CSS**. Add income and expenses, categorize transactions, view your totals, filter activity, and delete transactions.

## Features

- Dashboard with available balance, total income, and total expenses
- Add income and expense transactions
- Category, date, and optional note fields
- Transaction history with income/expense filtering
- Delete transactions with a confirmation prompt
- Persistent storage using SQLite
- Input validation, parameterized SQL queries, error pages, and logging
- Responsive layout for desktop and mobile
- Health-check endpoint at `/health`

## Tech stack

- Python 3.10+
- Flask
- SQLite (included with Python)
- HTML5 and CSS3

## Run locally on Windows

1. Install Python 3.10 or newer from https://www.python.org/downloads/ and select **Add Python to PATH** during setup.
2. Open this folder in VS Code.
3. Open **Terminal → New Terminal** and run:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
   ```

4. Open http://127.0.0.1:5000 in your browser.
5. Stop the server with `Ctrl+C`.

If PowerShell blocks virtual-environment activation, you can use Command Prompt instead:

```bat
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python app.py
```

## Project structure

```text
expense-tracker/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── index.html
│   └── error.html
└── static/
    └── style.css
```

The `expenses.db` database and `app.log` log file are created automatically when the application runs. They are intentionally excluded from Git.

## Configuration

For local development, Flask uses a development secret key. Before public deployment, set a strong `SECRET_KEY` environment variable. Set `FLASK_DEBUG=0` (or leave it unset) in production and use a production WSGI server such as Gunicorn.

Optional database path:

- Windows PowerShell: `$env:EXPENSE_TRACKER_DB="C:\path\to\expenses.db"`
- Linux/macOS: `export EXPENSE_TRACKER_DB=/path/to/expenses.db`

## Deployment

This app can be deployed to a Python hosting provider that supports Flask and persistent storage. Make sure the SQLite database path is on a persistent disk; otherwise data may be lost when the service restarts or redeploys. Use a production server (for example, Gunicorn on Linux) and configure `SECRET_KEY` securely. Do not use Flask's development server for public production traffic.

Example start command on a compatible Linux host:

```bash
gunicorn app:app
```

Add `gunicorn` to `requirements.txt` if your selected host requires it.

## Important notes

- This is an educational portfolio project, not a banking service.
- Data is stored locally in SQLite by default; there is no login or cloud sync.
- Do not enter sensitive financial information into a publicly deployed demo.
- The transaction list displays up to the latest 100 entries.

## Suggested demo video

1. Open the dashboard.
2. Add a sample income transaction.
3. Add a sample expense.
4. Show the totals updating.
5. Filter by income and expenses.
6. Delete a sample transaction.
7. Briefly show the project files and README.

## License

This project is provided for learning and portfolio use.
