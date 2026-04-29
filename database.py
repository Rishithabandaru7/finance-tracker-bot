import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            description TEXT,
            date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            UNIQUE(user_id, category)
        )
    ''')

    conn.commit()
    c.close()
    conn.close()
    print("✅ Supabase database initialized")

def register_user(user_id, username, first_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (user_id, username, first_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    ''', (user_id, username, first_name))
    conn.commit()
    c.close()
    conn.close()

def add_transaction(user_id, type_, amount, category, description):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (user_id, type, amount, category, description)
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_id, type_, amount, category, description))
    conn.commit()
    c.close()
    conn.close()

def get_monthly_summary(user_id):
    conn = get_conn()
    c = conn.cursor()
    month = datetime.now().strftime("%Y-%m")
    c.execute('''
        SELECT type, category, SUM(amount)
        FROM transactions
        WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s
        GROUP BY type, category
        ORDER BY type, SUM(amount) DESC
    ''', (user_id, month))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def get_weekly_summary(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT type, category, SUM(amount)
        FROM transactions
        WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY type, category
        ORDER BY type, SUM(amount) DESC
    ''', (user_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def set_budget(user_id, category, limit):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO budgets (user_id, category, monthly_limit)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, category) DO UPDATE SET monthly_limit = %s
    ''', (user_id, category, limit, limit))
    conn.commit()
    c.close()
    conn.close()

def check_budget(user_id, category):
    conn = get_conn()
    c = conn.cursor()
    month = datetime.now().strftime("%Y-%m")

    c.execute('''
        SELECT SUM(amount) FROM transactions
        WHERE user_id = %s AND category = %s
        AND type = 'expense'
        AND TO_CHAR(date, 'YYYY-MM') = %s
    ''', (user_id, category, month))
    spent = c.fetchone()[0] or 0

    c.execute('''
        SELECT monthly_limit FROM budgets
        WHERE user_id = %s AND category = %s
    ''', (user_id, category))
    row = c.fetchone()
    c.close()
    conn.close()

    if row:
        return spent, row[0]
    return spent, None

def get_recent_transactions(user_id, limit=5):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT id, type, amount, category, description, date
        FROM transactions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    ''', (user_id, limit))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def delete_transaction(user_id, transaction_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        DELETE FROM transactions
        WHERE id = %s AND user_id = %s
    ''', (transaction_id, user_id))
    affected = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    return affected > 0

def delete_all_transactions(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        DELETE FROM transactions
        WHERE user_id = %s
    ''', (user_id,))
    affected = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    return affected

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT user_id, first_name FROM users')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows