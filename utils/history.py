import os
import sys
import json
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection

CSV_HISTORY_PATH = os.path.join(PROJECT_ROOT, "data", "prediction_history.csv")

def save_prediction_record(
    employee_id: str,
    prediction: str,
    probability: float,
    risk_score: float,
    risk_level: str,
    risk_factors: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    growth_status: Optional[str] = None,
    confidence: Optional[float] = None,
    priority_retention: Optional[int] = 0
) -> int:
    """Saves a prediction record to both SQLite and synced CSV."""
    conn = get_connection()
    cur = conn.cursor()
    
    factors_json = json.dumps(risk_factors)
    recs_json = json.dumps(recommendations)
    
    cur.execute("""
        INSERT INTO prediction_history (
            employee_id, prediction, probability, risk_score, risk_level, risk_factors, recommendations,
            growth_status, confidence, priority_retention
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(employee_id), prediction, probability, risk_score, risk_level,
        factors_json, recs_json, growth_status, confidence, priority_retention
    ))
    
    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    # Sync to CSV
    sync_prediction_history_csv()
    return record_id

def sync_prediction_history_csv():
    """Syncs the entire prediction_history table to data/prediction_history.csv."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM prediction_history ORDER BY id DESC", conn)
    conn.close()
    os.makedirs(os.path.dirname(CSV_HISTORY_PATH), exist_ok=True)
    df.to_csv(CSV_HISTORY_PATH, index=False)

def get_all_prediction_history(limit: int = 500) -> pd.DataFrame:
    """Retrieves prediction history for HR review."""
    conn = get_connection()
    query = "SELECT * FROM prediction_history ORDER BY created_at DESC LIMIT ?"
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_prediction_history_for_employee(employee_id: str) -> pd.DataFrame:
    """Retrieves prediction history for a single employee."""
    conn = get_connection()
    query = "SELECT * FROM prediction_history WHERE employee_id = ? ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn, params=(str(employee_id),))
    conn.close()
    return df
