import os
import sys
import pandas as pd
from typing import Dict, Any, Tuple, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection
from utils.email_service import send_feedback_notification_email

CSV_FEEDBACK_PATH = os.path.join(PROJECT_ROOT, "data", "feedback.csv")

from datetime import datetime

def save_employee_feedback(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Saves feedback to SQLite, syncs data/feedback.csv, and triggers HR notification email.
    Records email_status ('Sent', 'Not Configured', or 'Failed') for dashboard audit.
    """
    is_anon = 1 if data.get("is_anonymous", False) else 0
    emp_id = None if is_anon else str(data.get("employee_id", ""))
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare payload with timestamp for email
    email_payload = {
        **data,
        "created_at": timestamp_str
    }
    email_ok, email_msg = send_feedback_notification_email(email_payload)
    
    if email_ok:
        email_status = "Sent"
    elif "not configured" in email_msg.lower():
        email_status = "Not Configured"
    else:
        email_status = "Failed"

    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO feedback (
                employee_id, is_anonymous,
                job_satisfaction, work_life_balance, manager_support,
                workload, career_growth, recognition,
                compensation_satisfaction, intention_to_stay,
                comments, email_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp_id, is_anon,
            int(data.get("job_satisfaction", 3)),
            int(data.get("work_life_balance", 3)),
            int(data.get("manager_support", 3)),
            int(data.get("workload", 3)),
            int(data.get("career_growth", 3)),
            int(data.get("recognition", 3)),
            int(data.get("compensation_satisfaction", 3)),
            int(data.get("intention_to_stay", 3)),
            str(data.get("comments", "")).strip(),
            email_status,
            timestamp_str
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        return False, f"Failed to save feedback to database: {str(e)}"
    finally:
        conn.close()
        
    # Sync to CSV
    sync_feedback_csv()
    
    return True, email_msg

def sync_feedback_csv():
    """Syncs the entire feedback table to data/feedback.csv."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM feedback ORDER BY id DESC", conn)
    conn.close()
    os.makedirs(os.path.dirname(CSV_FEEDBACK_PATH), exist_ok=True)
    df.to_csv(CSV_FEEDBACK_PATH, index=False)

def get_feedback_records(limit: int = 200) -> pd.DataFrame:
    """Retrieves all feedback records for authorized HR analytics."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?", conn, params=(limit,))
    conn.close()
    return df

def get_feedback_metrics() -> Dict[str, Any]:
    """Calculates aggregated feedback metrics for HR dashboard."""
    df = get_feedback_records()
    if df.empty:
        return {
            "total_feedback": 0,
            "anonymous_count": 0,
            "identified_count": 0,
            "avg_job_satisfaction": 0.0,
            "avg_work_life_balance": 0.0,
            "avg_manager_support": 0.0,
            "avg_workload": 0.0,
            "avg_career_growth": 0.0,
            "avg_recognition": 0.0,
            "avg_compensation": 0.0,
            "avg_intention_to_stay": 0.0,
            "stay_intent_pct": 0.0
        }
        
    total = len(df)
    anon = int(df["is_anonymous"].sum())
    stay_intent_favorable = ((df["intention_to_stay"] >= 4).sum() / total) * 100.0
    
    return {
        "total_feedback": total,
        "anonymous_count": anon,
        "identified_count": total - anon,
        "avg_job_satisfaction": round(df["job_satisfaction"].mean(), 2),
        "avg_work_life_balance": round(df["work_life_balance"].mean(), 2),
        "avg_manager_support": round(df["manager_support"].mean(), 2),
        "avg_workload": round(df["workload"].mean(), 2),
        "avg_career_growth": round(df["career_growth"].mean(), 2),
        "avg_recognition": round(df["recognition"].mean(), 2),
        "avg_compensation": round(df["compensation_satisfaction"].mean(), 2),
        "avg_intention_to_stay": round(df["intention_to_stay"].mean(), 2),
        "stay_intent_pct": round(stay_intent_favorable, 1)
    }

def get_latest_feedback() -> Optional[Dict[str, Any]]:
    """Retrieves the most recent feedback submission for HR Dashboard."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_common_concerns(limit: int = 20) -> list:
    """Retrieves recent employee comments/concerns for sentiment review."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT employee_id, is_anonymous, comments, created_at, job_satisfaction, work_life_balance, workload "
        "FROM feedback WHERE comments IS NOT NULL AND TRIM(comments) != '' "
        "ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
