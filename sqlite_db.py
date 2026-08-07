import sqlite3
from datetime import (
    datetime,
    timezone
)
from typing import Any
from config import DB_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    connection.execute("""
        PRAGMA foreign_keys = ON
    """)

    return connection

def row_to_dict(
    row: sqlite3.Row | None
) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)

# ====================
# Initialize DB
# ====================
def init_db() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL 
                    COLLATE NOCASE
                    UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                UNIQUE(user_id, key)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY (user_id)
                REFERENCE users(id)
                ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id, id DESC)")

        connection.execute()

def create_user(
    email: str,
    password_hash: str
) -> dict[str, Any] | None:
    normalized_email = email.strip().lower()
    now = utc_now()

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
    
            cursor.execute("""
                INSERT INTO users (email, password_hash, created_at)
                VALUES (?, ?, ?)
            """, (normalized_email, password_hash, now))
    
            user_id = cursor.lastrowid
            connection.commit()
        return get_user_by_id(user_id)
    
    except sqlite3.IntegrityError:
        return None

def get_user_by_id(
    user_id: int
) -> dict[str, Any] | None:
    with get_connection() as connection:
        cursor = connection.cursor()

        row = cursor.execute("""
            SELECT id, email, created_at FROM users WHERE id = ?
        """, (user_id,)).fetchone()
    return row_to_dict(row)

def get_user_by_email(
    email: str
) -> dict[str, Any] | None:
    normalized_email = email.strip().lower()

    with get_connection() as connection:
        cursor = connection.cursor()

        row = cursor.execute("""
            SELECT id, email, password_hash, created_at FROM users WHERE email = ?
        """, (normalized_email)).fetchone()
    return row_to_dict(row)

    

