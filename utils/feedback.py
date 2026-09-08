import os
import sys
import pandas as pd
from typing import Dict, Any, Tuple, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection, migrate_feedback_table_if_needed
from utils.email_service import send_feedback_notification_email

CSV_FEEDBACK_PATH = os.path.join(PROJECT_ROOT, "data", "feedback.csv")

from datetime import datetime

def save_employee_feedback(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Saves feedback to SQLite FIRST, syncs data/feedback.csv, and ONLY then dispatches HR notification email.
    If database insertion fails, NO email is dispatched.
    If email fails or is unconfigured, the feedback remains safely committed to SQLite.
    Updates the record's email_status ('Sent', 'Not Configured', or 'Failed') accordingly.
    """
    is_anon = 1 if data.get("is_anonymous", False) else 0
    emp_id = None if is_anon else str(data.get("employee_id", ""))
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Step 1: Input Validation
    try:
        job_sat = max(1, min(5, int(data.get("job_satisfaction", 3))))
        wlb = max(1, min(5, int(data.get("work_life_balance", 3))))
        mgr_supp = max(1, min(5, int(data.get("manager_support", 3))))
        workload = max(1, min(5, int(data.get("workload", 3))))
        career_growth = max(1, min(5, int(data.get("career_growth", 3))))
        recognition = max(1, min(5, int(data.get("recognition", 3))))
        comp_sat = max(1, min(5, int(data.get("compensation_satisfaction", 3))))
        intent_stay = max(1, min(5, int(data.get("intention_to_stay", 3))))
        comments = str(data.get("comments", "")).strip()
    except (ValueError, TypeError) as e:
        return False, f"Invalid feedback input values: {str(e)}"

    # Step 2: Open SQLite database and ALWAYS ensure schema migration on this connection
    conn = get_connection()
    feedback_id = None
    
    try:
        # ALWAYS run migration on this exact database connection BEFORE any insert
        migrate_feedback_table_if_needed(conn)
        
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO feedback (
                employee_id, is_anonymous,
                job_satisfaction, work_life_balance, manager_support,
                workload, career_growth, recognition,
                compensation_satisfaction, intention_to_stay,
                comments, email_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (
            emp_id, is_anon,
            job_sat, wlb, mgr_supp,
            workload, career_growth, recognition,
            comp_sat, intent_stay,
            comments, timestamp_str
        ))
        conn.commit()
        feedback_id = cur.lastrowid
    except Exception as db_err:
        conn.close()
        # NEVER send email if database save fails
        return False, f"Failed to save feedback to database: {str(db_err)}"

    # Step 3: Verify save succeeded
    if not feedback_id:
        conn.close()
        return False, "Failed to verify saved feedback in database."

    # Sync CSV with pending state
    sync_feedback_csv()

    # Step 4: Dispatch HR notification email
    email_payload = {
        "employee_id": data.get("employee_id", ""),
        "is_anonymous": is_anon == 1,
        "job_satisfaction": job_sat,
        "work_life_balance": wlb,
        "manager_support": mgr_supp,
        "workload": workload,
        "career_growth": career_growth,
        "recognition": recognition,
        "compensation_satisfaction": comp_sat,
        "intention_to_stay": intent_stay,
        "comments": comments,
        "created_at": timestamp_str
    }

    email_ok, email_msg = send_feedback_notification_email(email_payload)
    
    if email_ok:
        final_email_status = "Sent"
    elif "not configured" in email_msg.lower():
        final_email_status = "Not Configured"
    else:
        final_email_status = "Failed"

    # Step 5: Update record's email_status in database
    try:
        cur_update = conn.cursor()
        cur_update.execute("UPDATE feedback SET email_status = ? WHERE id = ?", (final_email_status, feedback_id))
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Sync CSV with final email status
    sync_feedback_csv()

    return True, email_msg

def sync_feedback_csv():
    """Syncs the entire feedback table to data/feedback.csv."""
    conn = get_connection()
    migrate_feedback_table_if_needed(conn)
    df = pd.read_sql_query("SELECT * FROM feedback ORDER BY id DESC", conn)
    conn.close()
    os.makedirs(os.path.dirname(CSV_FEEDBACK_PATH), exist_ok=True)
    df.to_csv(CSV_FEEDBACK_PATH, index=False)

def get_feedback_records(limit: int = 200) -> pd.DataFrame:
    """Retrieves all feedback records for authorized HR analytics directly from SQLite."""
    conn = get_connection()
    migrate_feedback_table_if_needed(conn)
    df = pd.read_sql_query("SELECT * FROM feedback ORDER BY id DESC LIMIT ?", conn, params=(limit,))
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
    migrate_feedback_table_if_needed(conn)
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
    migrate_feedback_table_if_needed(conn)
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
