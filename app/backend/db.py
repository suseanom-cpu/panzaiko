import sqlite3
from flask import g
from datetime import datetime

DB_PATH = "breads_full.db"

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        g._db = db
    return db

def init_db(app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            day TEXT NOT NULL,
            bread TEXT NOT NULL,
            sold INTEGER NOT NULL,
            leftover INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            bread TEXT NOT NULL,
            qty INTEGER NOT NULL,
            added_date TEXT NOT NULL,
            remaining INTEGER NOT NULL
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            detail TEXT,
            created_at TEXT NOT NULL
        )
        """)
        db.commit()

def log_action(user, action, detail=""):
    """操作ログを記録"""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO logs (user, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (user, action, detail, datetime.utcnow().isoformat())
    )
    db.commit()

def close_db(error):
    """データベース接続を閉じる"""
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()
