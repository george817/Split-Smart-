import sqlite3
import pandas as pd

DB = "data/expenses.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paid_by TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        description TEXT,
        date TEXT DEFAULT CURRENT_DATE,
        group_name TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        group_name TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def add_expense(paid_by, amount, category, description, group_name):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (paid_by, amount, category, description, group_name) VALUES (?,?,?,?,?)",
              (paid_by, amount, category, description, group_name))
    conn.commit()
    conn.close()

def get_expenses(group_name):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE group_name=? ORDER BY date DESC",
        conn, params=(group_name,))
    conn.close()
    return df

def delete_expense(expense_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
