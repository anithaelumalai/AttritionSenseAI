import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.ml_pipeline import load_trained_model, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from utils.database import get_connection
from utils.email_service import send_priority_retention_alert_email

# Cache for batch workforce analysis
_WORKFORCE_ANALYSIS_CACHE: Optional[pd.DataFrame] = None

# Permitted Growth Status labels (Decision-support only, never derogatory)
GROWTH_STATUS_HIGH = "High Growth Potential"
GROWTH_STATUS_STABLE = "Stable Contributor"
GROWTH_STATUS_SUPPORT = "Needs Support"
VALID_GROWTH_STATUSES = {GROWTH_STATUS_HIGH, GROWTH_STATUS_STABLE, GROWTH_STATUS_SUPPORT}

# Permitted Attrition Risk labels
RISK_LOW = "Low Risk"
RISK_MEDIUM = "Medium Risk"
RISK_HIGH = "High Risk"
VALID_RISK_LEVELS = {RISK_LOW, RISK_MEDIUM, RISK_HIGH}

# Priority Retention labels
PRIORITY_RETENTION_LABEL = "Priority Retention"
NO_PRIORITY_RETENTION_LABEL = "No Priority Retention"

def evaluate_employee_growth_status(
    emp_record: Dict[str, Any],
    feedback_data: Optional[Dict[str, Any]] = None,
    survey_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Evaluates employee performance & career growth indicators:
    PerformanceRating, JobInvolvement, TrainingTimesLastYear,
    PercentSalaryHike, YearsSinceLastPromotion, JobLevel, Education.
    
    CRITICAL RULES:
    - Strictly returns one of: 'High Growth Potential', 'Stable Contributor', 'Needs Support'.
    - Never uses derogatory words.
    - Presented as an AI decision-support indicator, NOT a final employment decision.
    - Mind-Free Game activity and Weekend Quiz scores are NEVER used here.
    - Missing feedback or survey is NEVER penalized.
    """
    try:
        perf_rating = float(emp_record.get("PerformanceRating", 3) or 3)
    except (ValueError, TypeError):
        perf_rating = 3.0

    try:
        job_involvement = float(emp_record.get("JobInvolvement", 3) or 3)
    except (ValueError, TypeError):
        job_involvement = 3.0

    try:
        training_times = float(emp_record.get("TrainingTimesLastYear", 2) or 2)
    except (ValueError, TypeError):
        training_times = 2.0

    try:
        salary_hike = float(emp_record.get("PercentSalaryHike", 14) or 14)
    except (ValueError, TypeError):
        salary_hike = 14.0

    try:
        years_since_promo = float(emp_record.get("YearsSinceLastPromotion", 0) or 0)
    except (ValueError, TypeError):
        years_since_promo = 0.0

    # Composite Growth Score (0 to 100)
    score = 0.0
    
    # 1. Performance Rating (Max 35 pts)
    # In IBM dataset: 3 = Excellent, 4 = Outstanding
    if perf_rating >= 4.0:
        score += 35.0
    elif perf_rating >= 3.0:
        score += 25.0
    else:
        score += 10.0

    # 2. Job Involvement (Max 25 pts)
    # 1 = Low, 2 = Medium, 3 = High, 4 = Very High
    if job_involvement >= 4.0:
        score += 25.0
    elif job_involvement >= 3.0:
        score += 20.0
    elif job_involvement >= 2.0:
        score += 10.0
    else:
        score += 0.0

    # 3. Training Engagement (Max 15 pts)
    if training_times >= 3.0:
        score += 15.0
    elif training_times >= 2.0:
        score += 10.0
    elif training_times >= 1.0:
        score += 5.0

    # 4. Salary Hike & Recognition (Max 15 pts)
    if salary_hike >= 18.0:
        score += 15.0
    elif salary_hike >= 14.0:
        score += 10.0
    elif salary_hike >= 12.0:
        score += 5.0

    # 5. Career Progression Pace (Max 10 pts)
    if years_since_promo <= 1.0:
        score += 10.0
    elif years_since_promo <= 3.0:
        score += 5.0
    elif years_since_promo >= 7.0:
        score -= 5.0  # Prolonged stagnation

    # 6. Optional Feedback Integration (Adjust only if feedback exists)
    if feedback_data and isinstance(feedback_data, dict):
        valid_ratings = [
            v for k, v in feedback_data.items()
            if k in ["job_satisfaction", "career_growth", "manager_support", "recognition"]
            and v is not None and isinstance(v, (int, float)) and v > 0
        ]
        if valid_ratings:
            avg_fb = sum(valid_ratings) / len(valid_ratings)
            if avg_fb >= 4.0:
                score += 5.0
            elif avg_fb <= 2.0:
                score -= 5.0

    # Categorization
    # Strict 3-category classification
    if perf_rating <= 2.0 or (job_involvement <= 1.0 and training_times <= 1.0) or score < 42.0:
        return GROWTH_STATUS_SUPPORT
    elif score >= 68.0:
        return GROWTH_STATUS_HIGH
    else:
        return GROWTH_STATUS_STABLE

def evaluate_attrition_risk(probability: float) -> str:
    """
    Standardizes attrition probability to strictly:
    - 'Low Risk' (0.00 to 0.39)
    - 'Medium Risk' (0.40 to 0.69)
    - 'High Risk' (0.70 to 1.00)
    """
    if probability >= 0.70:
        return RISK_HIGH
    elif probability >= 0.40:
        return RISK_MEDIUM
    else:
        return RISK_LOW

def evaluate_prediction_confidence(probability: float) -> float:
    """
    Prediction Confidence is calculated as:
    max(probability, 1 - probability) * 100%
    """
    conf = max(probability, 1.0 - probability) * 100.0
    return round(conf, 1)

def check_priority_retention(growth_status: str, attrition_risk: str) -> Tuple[bool, str]:
    """
    PRIORITY RETENTION LOGIC:
    ONLY trigger Priority Retention when:
      Growth Status == 'High Growth Potential' AND Attrition Risk == 'High Risk'
    
    All other 8 combinations return:
      False, 'No Priority Retention'
    """
    is_priority = (growth_status == GROWTH_STATUS_HIGH and attrition_risk == RISK_HIGH)
    label = PRIORITY_RETENTION_LABEL if is_priority else NO_PRIORITY_RETENTION_LABEL
    return is_priority, label

def record_priority_retention_alert(
    employee_id: str,
    growth_status: str,
    attrition_risk: str,
    emp_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Safely records a Priority Retention alert for an employee.
    Prevents duplicate notifications for the same employee and risk status.
    Dispatches HR email if SMTP is configured, or logs in-app alert.
    """
    is_priority, label = check_priority_retention(growth_status, attrition_risk)
    if not is_priority:
        return {
            "recorded": False,
            "status": "not_applicable",
            "message": "Employee does not meet Priority Retention criteria."
        }

    conn = get_connection()
    cur = conn.cursor()

    # Check for existing alert for this employee and risk
    cur.execute("""
        SELECT id, notification_status, created_at 
        FROM retention_alerts 
        WHERE employee_id = ? AND growth_status = ? AND attrition_risk = ?
        ORDER BY created_at DESC LIMIT 1
    """, (str(employee_id), growth_status, attrition_risk))
    existing = cur.fetchone()

    if existing:
        conn.close()
        return {
            "recorded": False,
            "status": "duplicate",
            "alert_id": existing["id"],
            "message": f"Priority Retention alert already active for Employee #{employee_id}."
        }

    # Prepare notification
    notification_type = "email"
    notification_status = "logged"
    
    details = emp_details or {}
    email_payload = {
        "employee_id": str(employee_id),
        "department": details.get("Department", details.get("department", "Corporate")),
        "job_role": details.get("JobRole", details.get("job_role", "Specialist")),
        "confidence": details.get("confidence", details.get("PredictionConfidence", 85.0)),
        "attrition_probability": details.get("attrition_probability", details.get("probability", 0.75))
    }

    email_sent, email_msg = send_priority_retention_alert_email(email_payload)
    if email_sent:
        notification_status = "sent"
    else:
        notification_status = "logged"

    # Insert alert record
    cur.execute("""
        INSERT INTO retention_alerts (
            employee_id, growth_status, attrition_risk,
            notification_type, notification_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(employee_id),
        growth_status,
        attrition_risk,
        notification_type,
        notification_status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    alert_id = cur.lastrowid
    conn.close()

    return {
        "recorded": True,
        "alert_id": alert_id,
        "status": notification_status,
        "message": f"Priority Retention alert created for Employee #{employee_id}: {email_msg}"
    }

def get_active_retention_alerts() -> List[Dict[str, Any]]:
    """Fetches all logged retention alerts from database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, employee_id, growth_status, attrition_risk, notification_type, notification_status, alert_acknowledged, created_at
        FROM retention_alerts
        ORDER BY created_at DESC
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_workforce_ai_analysis(
    df_source: Optional[pd.DataFrame] = None,
    force_refresh: bool = False
) -> pd.DataFrame:
    """
    Performs vectorized inference on ALL 1,470 records from employees.csv.
    Generates:
    - EmployeeNumber / Employee ID
    - Name (Employee #ID)
    - Department, JobRole, Age, MonthlyIncome
    - AttritionRisk ('Low Risk', 'Medium Risk', 'High Risk')
    - AttritionProbability (float)
    - RiskScore (0-100)
    - PredictionConfidence (e.g. 88.5%)
    - GrowthStatus ('High Growth Potential', 'Stable Contributor', 'Needs Support')
    - PriorityRetention ('Priority Retention', 'No Priority Retention')
    - IsPriorityRetention (bool)
    
    Caches the result in memory for near-instant retrieval (<5ms after first load).
    """
    global _WORKFORCE_ANALYSIS_CACHE

    if _WORKFORCE_ANALYSIS_CACHE is not None and not force_refresh and df_source is None:
        return _WORKFORCE_ANALYSIS_CACHE.copy()

    if df_source is None:
        csv_path = os.path.join(PROJECT_ROOT, "data", "employees.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"employees.csv not found at {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        df = df_source.copy()

    pipeline, metadata = load_trained_model()

    # Prepare model inputs
    X_input = pd.DataFrame()
    for feat in NUMERICAL_FEATURES:
        if feat in df.columns:
            X_input[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0.0)
        else:
            X_input[feat] = 0.0

    for feat in CATEGORICAL_FEATURES:
        if feat in df.columns:
            X_input[feat] = df[feat].astype(str)
        else:
            X_input[feat] = "Unknown"

    # Batch model prediction
    probs = pipeline.predict_proba(X_input)[:, 1]

    # Vectorized analysis computation
    results = []
    for idx, row in df.iterrows():
        emp_id = str(row["EmployeeNumber"])
        prob = float(probs[idx])
        risk_score = round(prob * 100.0, 1)
        attrition_risk = evaluate_attrition_risk(prob)
        confidence = evaluate_prediction_confidence(prob)
        
        row_dict = row.to_dict()
        growth_status = evaluate_employee_growth_status(row_dict)
        is_priority, priority_label = check_priority_retention(growth_status, attrition_risk)
        
        results.append({
            "EmployeeNumber": emp_id,
            "Employee_ID": emp_id,
            "Name": f"Employee #{emp_id}",
            "Department": str(row.get("Department", "General")),
            "JobRole": str(row.get("JobRole", "Specialist")),
            "Age": int(row.get("Age", 35)),
            "MonthlyIncome": float(row.get("MonthlyIncome", 5000)),
            "AttritionRisk": attrition_risk,
            "AttritionProbability": round(prob, 4),
            "RiskScore": risk_score,
            "PredictionConfidence": confidence,
            "ConfidenceFormatted": f"{confidence}%",
            "GrowthStatus": growth_status,
            "PriorityRetention": priority_label,
            "IsPriorityRetention": is_priority
        })

    analysis_df = pd.DataFrame(results)
    _WORKFORCE_ANALYSIS_CACHE = analysis_df.copy()
    return analysis_df.copy()
