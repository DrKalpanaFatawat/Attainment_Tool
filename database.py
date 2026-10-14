import sqlite3
import os
from pathlib import Path
import bcrypt


BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "attainment.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT DEFAULT '',
                role TEXT NOT NULL DEFAULT 'faculty'
                    CHECK(role IN ('faculty', 'admin')),
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active', 'disabled')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            );

            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                subject_code TEXT DEFAULT '',
                student_count INTEGER,
                status TEXT NOT NULL,
                details TEXT DEFAULT '',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_logs_timestamp
            ON activity_logs(timestamp);

            CREATE INDEX IF NOT EXISTS idx_logs_username
            ON activity_logs(username);
        """)


def create_user(
    username,
    password,
    full_name,
    department="",
    role="faculty"
):
    username = username.strip().lower()
    full_name = full_name.strip()
    department = department.strip()

    # Public registration may create faculty accounts only.
    if role != "faculty":
        raise ValueError("Public registration is for faculty only.")

    if not username or not full_name:
        raise ValueError("Username and full name are required.")

    if len(username) < 4 or len(username) > 50:
        raise ValueError("Username must contain 4–50 characters.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO users
                (username, password_hash, full_name, department, role)
                VALUES (?, ?, ?, ?, 'faculty')
            """, (username, password_hash, full_name, department))
        return True, "Account created. You can now log in."

    except sqlite3.IntegrityError:
        return False, "That username is already registered."


def authenticate_user(username, password):
    username = username.strip().lower()

    with get_connection() as conn:
        user = conn.execute("""
            SELECT id, username, password_hash, full_name,
                   department, role, status
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

    if user is None:
        # Reduce username-enumeration timing differences.
        bcrypt.checkpw(
            password.encode("utf-8"),
            bcrypt.hashpw(
                b"invalid-password",
                bcrypt.gensalt(rounds=12)
            )
        )
        return None

    if user["status"] != "active":
        return None

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    ):
        return None

    return dict(user)


def update_last_login(user_id):
    with get_connection() as conn:
        conn.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (user_id,))


def record_activity(
    user_id,
    username,
    action,
    status="SUCCESS",
    subject_code="",
    student_count=None,
    details=""
):
    # Do not put passwords or student marks in this log.
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO activity_logs
            (user_id, username, action, status,
             subject_code, student_count, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            username,
            action,
            status,
            subject_code,
            student_count,
            details[:300]
        ))


def create_first_admin(username, password, full_name):
    """Used only by the one-time setup script."""
    username = username.strip().lower()

    if len(password) < 8:
        raise ValueError("Admin password must be at least 8 characters.")

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    with get_connection() as conn:
        admin_count = conn.execute(
            "SELECT COUNT(*) AS n FROM users WHERE role = 'admin'"
        ).fetchone()["n"]

        if admin_count:
            raise ValueError("An administrator already exists.")


        conn.execute("""
            INSERT INTO users
            (username, password_hash, full_name, department, role)
            VALUES (?, ?, ?, 'Administration', 'admin')
        """, (username, password_hash, full_name.strip()))


def get_dashboard_summary():
    with get_connection() as conn:
        return {
            "faculty": conn.execute("""
                SELECT COUNT(*) AS n FROM users
                WHERE role = 'faculty'
            """).fetchone()["n"],

            "active_faculty": conn.execute("""
                SELECT COUNT(*) AS n FROM users
                WHERE role = 'faculty' AND status = 'active'
            """).fetchone()["n"],

            "generated": conn.execute("""
                SELECT COUNT(*) AS n FROM activity_logs
                WHERE action = 'GENERATE'
                  AND status = 'SUCCESS'
            """).fetchone()["n"],

            "failed_logins": conn.execute("""
                SELECT COUNT(*) AS n FROM activity_logs
                WHERE action = 'LOGIN' AND status = 'FAILED'
            """).fetchone()["n"],
        }


def get_activity_logs(limit=500):
    limit = max(1, min(int(limit), 2000))

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT timestamp, username, action, subject_code,
                   student_count, status, details
            FROM activity_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def get_users():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, username, full_name, department,
                   role, status, created_at, last_login
            FROM users
            ORDER BY username
        """).fetchall()

    return [dict(row) for row in rows]


def set_user_status(user_id, status):
    if status not in ("active", "disabled"):
        raise ValueError("Invalid account status.")

    with get_connection() as conn:
        conn.execute("""
            UPDATE users
            SET status = ?
            WHERE id = ? AND role = 'faculty'
        """, (status, user_id))

def reset_faculty_password(username, new_password):
    username = username.strip().lower()

    if len(new_password) < 8 or len(new_password) > 14:
        raise ValueError(
            "Password must contain 8–14 characters."
        )

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE username = ?
              AND role = 'faculty'
              AND status = 'active'
        """, (password_hash, username))

        return cursor.rowcount > 0        
