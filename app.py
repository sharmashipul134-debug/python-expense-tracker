import logging
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("EXPENSE_TRACKER_DB", BASE_DIR / "expenses.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-development-key")

logging.basicConfig(
    filename=BASE_DIR / "app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Education", "Entertainment", "Salary", "Other"]
TYPES = {"income", "expense"}


def get_db():
    """Open a SQLite connection with named-column access."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the transactions table if it does not exist."""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                kind TEXT NOT NULL CHECK(kind IN ('income', 'expense')),
                category TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
    logger.info("Database initialized at %s", DATABASE)


def get_summary():
    with get_db() as db:
        row = db.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN kind='income' THEN amount ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN kind='expense' THEN amount ELSE 0 END), 0) AS expenses
            FROM transactions
        """).fetchone()
    income = float(row["income"])
    expenses = float(row["expenses"])
    return {"income": income, "expenses": expenses, "balance": income - expenses}


@app.route("/")
def index():
    selected_kind = request.args.get("kind", "all")
    if selected_kind not in {"all", "income", "expense"}:
        selected_kind = "all"

    query = "SELECT * FROM transactions"
    params = []
    if selected_kind != "all":
        query += " WHERE kind = ?"
        params.append(selected_kind)
    query += " ORDER BY transaction_date DESC, id DESC LIMIT 100"

    with get_db() as db:
        transactions = db.execute(query, params).fetchall()

    summary = get_summary()
    recent_expenses = [t for t in transactions if t["kind"] == "expense"][:5]
    return render_template(
        "index.html",
        transactions=transactions,
        summary=summary,
        selected_kind=selected_kind,
        categories=CATEGORIES,
        today=date.today().isoformat(),
        recent_expenses=recent_expenses,
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    title = request.form.get("title", "").strip()
    raw_amount = request.form.get("amount", "").strip()
    kind = request.form.get("kind", "").strip()
    category = request.form.get("category", "Other").strip()
    transaction_date = request.form.get("transaction_date", "").strip()
    notes = request.form.get("notes", "").strip()[:300]

    try:
        amount = float(raw_amount)
        if not title:
            raise ValueError("Please enter a transaction title.")
        if amount <= 0 or amount > 1_000_000_000:
            raise ValueError("Amount must be greater than 0 and within a reasonable limit.")
        if kind not in TYPES:
            raise ValueError("Choose income or expense.")
        if category not in CATEGORIES:
            category = "Other"
        datetime.strptime(transaction_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        flash("Please check the title, amount, type, and date. Amount must be a positive number.", "error")
        return redirect(url_for("index"))

    try:
        with get_db() as db:
            db.execute(
                """INSERT INTO transactions (title, amount, kind, category, transaction_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (title, amount, kind, category, transaction_date, notes),
            )
        logger.info("Transaction added: kind=%s category=%s amount=%.2f", kind, category, amount)
        flash("Transaction added successfully.", "success")
    except sqlite3.Error:
        logger.exception("Could not save transaction")
        flash("The transaction could not be saved. Please try again.", "error")

    return redirect(url_for("index"))


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    try:
        with get_db() as db:
            cursor = db.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        if cursor.rowcount:
            logger.info("Transaction deleted: id=%s", transaction_id)
            flash("Transaction deleted.", "success")
        else:
            flash("Transaction was not found.", "error")
    except sqlite3.Error:
        logger.exception("Could not delete transaction")
        flash("Could not delete this transaction.", "error")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="That page could not be found."), 404


@app.errorhandler(500)
def server_error(_error):
    logger.exception("Unexpected server error")
    return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
