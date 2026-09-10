import os
import sys
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection

def save_exit_feedback(
    employee_id: str,
    feedback_data: Optional[Dict[str, Any]] = None,
    is_skipped: bool = False
) -> bool:
    """
    Saves an optional employee exit interview response.
    
    CRITICAL DATA RULE:
    - If skipped, is_skipped=1 and optional rating fields are NULL.
    - If submitted, unanswered fields MUST REMAIN NULL (None), NEVER converted to 0.
    """
    conn = get_connection()
    cur = conn.cursor()
    data = feedback_data or {}

    if is_skipped:
        primary_reason = "Skipped"
        experience_rating = None
        recommend_company = None
        handover_status = "Skipped"
        detailed_feedback = "Exit feedback skipped by employee."
        skipped_flag = 1
    else:
        primary_reason = data.get("primary_reason")
        experience_rating = data.get("experience_rating")
        recommend_company = data.get("recommend_company")
        handover_status = data.get("handover_status")
        detailed_feedback = data.get("detailed_feedback")
        skipped_flag = 0

    cur.execute("""
        INSERT INTO exit_feedback (
            employee_id, primary_reason, experience_rating,
            recommend_company, handover_status, detailed_feedback,
            is_skipped, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(employee_id),
        primary_reason,
        experience_rating,
        recommend_company,
        handover_status,
        detailed_feedback,
        skipped_flag,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return True

def get_exit_feedback_for_employee(employee_id: str) -> Optional[Dict[str, Any]]:
    """Returns exit feedback submission for the employee if available."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM exit_feedback 
        WHERE employee_id = ? 
        ORDER BY created_at DESC LIMIT 1
    """, (str(employee_id),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_exit_feedback() -> List[Dict[str, Any]]:
    """Returns all exit feedback for HR review."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM exit_feedback ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
