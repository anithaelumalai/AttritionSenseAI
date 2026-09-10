import os
import sys
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection

def save_survey(
    employee_id: str,
    survey_data: Optional[Dict[str, Any]] = None,
    is_skipped: bool = False
) -> bool:
    """
    Saves an optional employee workplace survey response.
    
    CRITICAL RULES:
    - If skipped, is_skipped=1 and rating fields are NULL.
    - If submitted, unanswered fields MUST REMAIN NULL (None), NEVER converted to 0.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    data = survey_data or {}
    
    if is_skipped:
        work_env = None
        team_collab = None
        culture = None
        growth = None
        tools = None
        suggestions = "Survey skipped by employee."
        skipped_flag = 1
    else:
        # Strictly preserve None / NULL if not answered; never convert to 0
        work_env = data.get("work_environment")
        team_collab = data.get("team_collaboration")
        culture = data.get("culture_alignment")
        growth = data.get("growth_opportunities")
        tools = data.get("tools_resources")
        suggestions = data.get("suggestions")
        skipped_flag = 0

    cur.execute("""
        INSERT INTO surveys (
            employee_id, work_environment, team_collaboration,
            culture_alignment, growth_opportunities, tools_resources,
            suggestions, is_skipped, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(employee_id),
        work_env,
        team_collab,
        culture,
        growth,
        tools,
        suggestions,
        skipped_flag,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return True

def get_latest_survey(employee_id: str) -> Optional[Dict[str, Any]]:
    """Returns the most recent survey submission for the given employee."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM surveys 
        WHERE employee_id = ? 
        ORDER BY created_at DESC LIMIT 1
    """, (str(employee_id),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_surveys() -> List[Dict[str, Any]]:
    """Returns all surveys for aggregated reporting."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM surveys ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
