import sqlite3
import os
import sys
import pandas as pd
from typing import Optional, List, Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "app.db")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_path() -> str:
    """Returns the absolute path to the SQLite database file."""
    return os.path.abspath(DB_PATH)

def migrate_feedback_table_if_needed(conn: sqlite3.Connection) -> List[str]:
    """
    Safely inspects the feedback table and adds any missing columns using ALTER TABLE.
    Ensures table exists first without dropping or deleting existing data.
    Returns the list of column names in the feedback table.
    """
    cur = conn.cursor()
    
    # 1. Guarantee table exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        is_anonymous INTEGER NOT NULL DEFAULT 0,
        job_satisfaction INTEGER NOT NULL DEFAULT 3,
        work_life_balance INTEGER NOT NULL DEFAULT 3,
        manager_support INTEGER NOT NULL DEFAULT 3,
        workload INTEGER NOT NULL DEFAULT 3,
        career_growth INTEGER NOT NULL DEFAULT 3,
        recognition INTEGER NOT NULL DEFAULT 3,
        compensation_satisfaction INTEGER NOT NULL DEFAULT 3,
        intention_to_stay INTEGER NOT NULL DEFAULT 3,
        comments TEXT,
        email_status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    # 2. Inspect existing columns
    cur.execute("PRAGMA table_info(feedback)")
    existing_cols = {row[1]: row for row in cur.fetchall()}
    
    # Required columns and their fallback definitions for ALTER TABLE
    column_definitions = {
        "employee_id": "ALTER TABLE feedback ADD COLUMN employee_id TEXT",
        "is_anonymous": "ALTER TABLE feedback ADD COLUMN is_anonymous INTEGER NOT NULL DEFAULT 0",
        "job_satisfaction": "ALTER TABLE feedback ADD COLUMN job_satisfaction INTEGER NOT NULL DEFAULT 3",
        "work_life_balance": "ALTER TABLE feedback ADD COLUMN work_life_balance INTEGER NOT NULL DEFAULT 3",
        "manager_support": "ALTER TABLE feedback ADD COLUMN manager_support INTEGER NOT NULL DEFAULT 3",
        "workload": "ALTER TABLE feedback ADD COLUMN workload INTEGER NOT NULL DEFAULT 3",
        "career_growth": "ALTER TABLE feedback ADD COLUMN career_growth INTEGER NOT NULL DEFAULT 3",
        "recognition": "ALTER TABLE feedback ADD COLUMN recognition INTEGER NOT NULL DEFAULT 3",
        "compensation_satisfaction": "ALTER TABLE feedback ADD COLUMN compensation_satisfaction INTEGER NOT NULL DEFAULT 3",
        "intention_to_stay": "ALTER TABLE feedback ADD COLUMN intention_to_stay INTEGER NOT NULL DEFAULT 3",
        "comments": "ALTER TABLE feedback ADD COLUMN comments TEXT",
        "email_status": "ALTER TABLE feedback ADD COLUMN email_status TEXT DEFAULT 'Pending'",
        "created_at": "ALTER TABLE feedback ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    
    for col_name, alter_stmt in column_definitions.items():
        if col_name not in existing_cols:
            try:
                cur.execute(alter_stmt)
            except sqlite3.OperationalError:
                pass
    conn.commit()

    # 3. Re-query to return the verified column list
    cur.execute("PRAGMA table_info(feedback)")
    final_cols = [row[1] for row in cur.fetchall()]
    return final_cols

def init_database(db_path: str = DB_PATH):
    """Initializes all SQLite database tables."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    # 1. Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('employee', 'hr')),
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Chat history table (Employee BuddyBot)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        sender TEXT NOT NULL CHECK(sender IN ('user', 'buddybot')),
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 3. Employee feedback table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        is_anonymous INTEGER NOT NULL DEFAULT 0,
        job_satisfaction INTEGER NOT NULL CHECK(job_satisfaction BETWEEN 1 AND 5),
        work_life_balance INTEGER NOT NULL CHECK(work_life_balance BETWEEN 1 AND 5),
        manager_support INTEGER NOT NULL CHECK(manager_support BETWEEN 1 AND 5),
        workload INTEGER NOT NULL CHECK(workload BETWEEN 1 AND 5),
        career_growth INTEGER NOT NULL CHECK(career_growth BETWEEN 1 AND 5),
        recognition INTEGER NOT NULL CHECK(recognition BETWEEN 1 AND 5),
        compensation_satisfaction INTEGER NOT NULL CHECK(compensation_satisfaction BETWEEN 1 AND 5),
        intention_to_stay INTEGER NOT NULL DEFAULT 3 CHECK(intention_to_stay BETWEEN 1 AND 5),
        comments TEXT,
        email_status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Non-destructive schema migration check for existing databases
    migrate_feedback_table_if_needed(conn)

    
    # 4. Prediction history table (HR)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        prediction TEXT NOT NULL,
        probability REAL NOT NULL,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        risk_factors TEXT NOT NULL,
        recommendations TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()

def seed_users_if_needed(csv_path: Optional[str] = None, db_path: str = DB_PATH):
    """
    Seeds HR admin accounts and Employee accounts for ONLY the ACTUAL EmployeeNumber
    values present in employees.csv.
    """
    from utils.auth import hash_password
    
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    # Check if HR accounts exist
    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'hr'")
    hr_count = cur.fetchone()["cnt"]
    
    if hr_count == 0:
        # Default HR accounts
        hr_accounts = [
            ("admin", "admin123"),
            ("hr_manager", "hr123")
        ]
        for username, password in hr_accounts:
            pwd_hash, salt = hash_password(password)
            cur.execute(
                "INSERT OR IGNORE INTO users (identifier, role, password_hash, salt) VALUES (?, 'hr', ?, ?)",
                (username, pwd_hash, salt)
            )
        conn.commit()
        print("Seeded default HR accounts: 'admin' and 'hr_manager'")
        
    # Check if Employee accounts are seeded
    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'employee'")
    emp_count = cur.fetchone()["cnt"]
    
    if emp_count == 0:
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "employees.csv")
            
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if "EmployeeNumber" in df.columns:
                # Use ONLY actual EmployeeNumbers from dataset
                actual_emp_ids = sorted(df["EmployeeNumber"].unique().tolist())
                print(f"Seeding {len(actual_emp_ids)} employee accounts from actual EmployeeNumbers...")
                
                # Precompute standard password hash to speed up seeding
                default_password = "emp123"
                pwd_hash, salt = hash_password(default_password)
                
                batch_data = [
                    (str(emp_id), "employee", pwd_hash, salt)
                    for emp_id in actual_emp_ids
                ]
                
                cur.executemany(
                    "INSERT OR IGNORE INTO users (identifier, role, password_hash, salt) VALUES (?, ?, ?, ?)",
                    batch_data
                )
                conn.commit()
                print(f"Successfully seeded {len(actual_emp_ids)} employee accounts with default password 'emp123'.")
    
    conn.close()

if __name__ == "__main__":
    init_database()
    seed_users_if_needed()
    print("Database initialized and verified.")
