import sqlite3
from datetime import datetime

DB_NAME = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            description TEXT,
            date TEXT DEFAULT CURRENT_DATE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            UNIQUE(user_id, category)
        )
    ''')

    conn.commit()
    conn.close()

def register_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (user_id, username, first_name))
    conn.commit()
    conn.close()

def add_transaction(user_id, type_, amount, category, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (user_id, type, amount, category, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, type_, amount, category, description))
    conn.commit()
    conn.close()

def get_monthly_summary(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    month = datetime.now().strftime("%Y-%m")
    c.execute('''
        SELECT type, category, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND date LIKE ?
        GROUP BY type, category
        ORDER BY type, SUM(amount) DESC
    ''', (user_id, f"{month}%"))
    rows = c.fetchall()
    conn.close()
    return rows

def get_weekly_summary(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT type, category, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND date >= date('now', '-7 days')
        GROUP BY type, category
        ORDER BY type, SUM(amount) DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def set_budget(user_id, category, limit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO budgets (user_id, category, monthly_limit)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = ?
    ''', (user_id, category, limit, limit))
    conn.commit()
    conn.close()

def check_budget(user_id, category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    month = datetime.now().strftime("%Y-%m")

    c.execute('''
        SELECT SUM(amount) FROM transactions
        WHERE user_id = ? AND category = ? AND type = 'expense' AND date LIKE ?
    ''', (user_id, category, f"{month}%"))
    spent = c.fetchone()[0] or 0

    c.execute('''
        SELECT monthly_limit FROM budgets
        WHERE user_id = ? AND category = ?
    ''', (user_id, category))
    row = c.fetchone()
    conn.close()

    if row:
        return spent, row[0]
    return spent, None

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT user_id, first_name FROM users')
    rows = c.fetchall()
    conn.close()
    return rows
def get_recent_transactions(user_id, limit=5):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT id, type, amount, category, description, date
        FROM transactions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_transaction(user_id, transaction_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # user_id check makes sure users can only delete their own transactions
    c.execute('''
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
    ''', (transaction_id, user_id))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0
def delete_all_transactions(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        DELETE FROM transactions
        WHERE user_id = ?
    ''', (user_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected