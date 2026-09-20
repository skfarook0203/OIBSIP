"""
OASIS INFOBYTE Python Programming Internship
Task 2: BMI Calculator (Advanced Version)
Module: database.py

Handles local SQLite database persistence, schema creation, parameterized queries,
record retrieval, and robust database error handling.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """Manages SQLite database storage for BMI user records."""

    def __init__(self, db_name: str = "bmi_calculator.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a database connection with WAL mode and row factory enabled."""
        conn = sqlite3.connect(self.db_name, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for improved concurrency and data integrity
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except sqlite3.Error:
            pass
        return conn

    def init_database(self) -> None:
        """Initializes the SQLite database and creates the records table if missing."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        date_time TEXT NOT NULL
                    );
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_name ON records(user_name);
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_date_time ON records(date_time);
                """)
                conn.commit()
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to initialize database: {err}")
            raise

    def insert_record(
        self,
        user_name: str,
        weight: float,
        height: float,
        bmi: float,
        category: str,
        date_time: Optional[str] = None,
    ) -> int:
        """
        Inserts a new BMI record for a named user.
        Returns the inserted record's ID.
        """
        if not date_time:
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = """
            INSERT INTO records (user_name, weight, height, bmi, category, date_time)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (
                        user_name.strip(),
                        float(weight),
                        float(height),
                        float(bmi),
                        category.strip(),
                        date_time,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to insert record: {err}")
            raise

    def get_user_records(self, user_name: str) -> List[Dict[str, Any]]:
        """Retrieves all BMI records for a specific user, ordered chronologically."""
        query = """
            SELECT id, user_name, weight, height, bmi, category, date_time
            FROM records
            WHERE user_name = ?
            ORDER BY date_time ASC, id ASC;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_name.strip(),))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to fetch records for '{user_name}': {err}")
            return []

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Retrieves all BMI records from the database, ordered chronologically."""
        query = """
            SELECT id, user_name, weight, height, bmi, category, date_time
            FROM records
            ORDER BY date_time DESC, id DESC;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to fetch all records: {err}")
            return []

    def get_all_users(self) -> List[str]:
        """Returns a sorted list of all distinct user names with records in the database."""
        query = """
            SELECT DISTINCT user_name
            FROM records
            WHERE user_name IS NOT NULL AND TRIM(user_name) != ''
            ORDER BY user_name ASC;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [row["user_name"] for row in rows]
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to fetch users: {err}")
            return []

    def delete_record(self, record_id: int) -> bool:
        """Deletes a record by its unique ID."""
        query = "DELETE FROM records WHERE id = ?;"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (record_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to delete record #{record_id}: {err}")
            return False

    def clear_user_history(self, user_name: str) -> bool:
        """Deletes all records for a specific named user."""
        query = "DELETE FROM records WHERE user_name = ?;"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_name.strip(),))
                conn.commit()
                return True
        except sqlite3.Error as err:
            print(f"[Database Error] Failed to clear history for '{user_name}': {err}")
            return False

    def seed_demo_data(self) -> None:
        """Populates the database with sample records if the table is currently empty."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM records;")
                count = cursor.fetchone()["count"]
                if count == 0:
                    sample_data = [
                        ("John", 78.5, 1.75, 25.63, "Overweight", "2026-04-10 08:30:00"),
                        ("John", 77.0, 1.75, 25.14, "Overweight", "2026-05-15 09:00:00"),
                        ("John", 75.2, 1.75, 24.56, "Normal weight", "2026-06-20 08:15:00"),
                        ("John", 73.8, 1.75, 24.10, "Normal weight", "2026-07-25 08:45:00"),
                        ("John", 72.0, 1.75, 23.51, "Normal weight", "2026-08-30 09:10:00"),
                        ("Sarah", 52.0, 1.62, 19.81, "Normal weight", "2026-05-01 07:45:00"),
                        ("Sarah", 51.5, 1.62, 19.62, "Normal weight", "2026-06-01 08:00:00"),
                        ("Sarah", 53.0, 1.62, 20.19, "Normal weight", "2026-07-01 07:50:00"),
                        ("Alex", 92.0, 1.70, 31.83, "Obesity", "2026-06-10 10:00:00"),
                        ("Alex", 89.5, 1.70, 30.97, "Obesity", "2026-07-15 09:30:00"),
                        ("Alex", 86.0, 1.70, 29.76, "Overweight", "2026-08-20 09:00:00"),
                    ]
                    cursor.executemany(
                        """
                        INSERT INTO records (user_name, weight, height, bmi, category, date_time)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        sample_data,
                    )
                    conn.commit()
        except sqlite3.Error as err:
            print(f"[Database Warning] Demo seeding skipped: {err}")
