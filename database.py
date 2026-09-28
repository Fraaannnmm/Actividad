import os
import sqlite3
from pathlib import Path
from typing import Any

from auth import hash_password

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "users.db"))

def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('profesor', 'estudiante'))
            )
            """
        )
        users = (
            ("maria@ujap.edu.ve", "profesor123", "profesor"),
            ("estudiante@ujap.edu.ve", "estudiante123", "estudiante"),
        )
        for email, password, role in users:
            connection.execute(
                """
                INSERT OR IGNORE INTO users (email, password_hash, role)
                VALUES (?, ?, ?)
                """,
                (email, hash_password(password), role),
            )

def find_user(email: str) -> dict[str, Any] | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT email, password_hash, role FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None