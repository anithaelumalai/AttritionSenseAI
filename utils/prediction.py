import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.ml_pipeline import (
    load_trained_model,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES
)

def determine_risk_level(risk_score: float) -> Tuple[str, str]:
    """
    Classifies risk score into standard documented tiers:
    0–39  -> Low Risk (Green)
    40–69 -> Medium Risk (Amber/Orange)
    70–100 -> High Risk (Red)
    """
    if risk_score >= 70.0:
        return "High Risk", "#e63946"  # Coral Red
    elif risk_score >= 40.0:
        return "Medium Risk", "#f4a261"  # Amber Orange
    else:
        return "Low Risk", "#2a9d8f"  # Emerald Green

def identify_risk_factors(emp_record: Dict[str, Any], df_context: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
    """
    Extracts specific, concrete attrition risk drivers by evaluating
    the employee's actual attributes.
    """
    factors = []
    
    # 1. Overtime
    if str(emp_record.get("OverTime", "")).strip().lower() == "yes":
        factors.append({
            "factor": "Frequent Overtime",
            "detail": "Employee works overtime regularly, which is historically a leading driver of burnout and turnover.",
            "severity": "High"
        })
        
    # 2. Job Satisfaction
    job_sat = emp_record.get("JobSatisfaction", 3)
    if job_sat <= 2:
        factors.append({
            "factor": "Low Job Satisfaction",
            "detail": f"Job satisfaction rating is {job_sat}/4, indicating disengagement with day-to-day responsibilities.",
            "severity": "High" if job_sat == 1 else "Medium"
        })
        
    # 3. Environment Satisfaction
    env_sat = emp_record.get("EnvironmentSatisfaction", 3)
    if env_sat <= 2:
        factors.append({
            "factor": "Low Workplace Environment Satisfaction",
            "detail": f"Environment satisfaction rating is {env_sat}/4, pointing to physical or team culture friction.",
            "severity": "High" if env_sat == 1 else "Medium"
        })
        
    # 4. Work-Life Balance
    wlb = emp_record.get("WorkLifeBalance", 3)
    if wlb <= 2:
        factors.append({
            "factor": "Suboptimal Work-Life Balance",
            "detail": f"Work-life balance is rated {wlb}/4, signaling risk of exhaustion and work fatigue.",
            "severity": "High" if wlb == 1 else "Medium"
        })
        
    # 5. Promotion Stagnation
    years_promo = emp_record.get("YearsSinceLastPromotion", 0)
    years_co = emp_record.get("YearsAtCompany", 0)
    if years_promo >= 4 and years_co >= 3:
        factors.append({
            "factor": "Career Progression Stagnation",
            "detail": f"{years_promo} years have elapsed since last promotion, creating vulnerability to competitive poaching.",
            "severity": "High" if years_promo >= 6 else "Medium"
        })
        
    # 6. Commute Distance
    dist = emp_record.get("DistanceFromHome", 0)
    if dist >= 15:
        factors.append({
            "factor": "Long Daily Commute",
            "detail": f"Commute distance is {dist} miles, contributing to daily fatigue and higher turnover propensity.",
            "severity": "Medium"
        })
        
    # 7. Low Stock Option Incentive
    stock = emp_record.get("StockOptionLevel", 0)
    if stock == 0:
        factors.append({
            "factor": "Zero Equity Retention Tie",
            "detail": "Stock option level is 0, leaving no golden handcuffs or long-term equity alignment.",
            "severity": "Low"
        })
        
    # 8. Business Travel Frequency
    travel = str(emp_record.get("BusinessTravel", "")).strip()
    if travel == "Travel_Frequently":
        factors.append({
            "factor": "High Travel Burden",
            "detail": "Frequent business travel schedule strains personal schedule and increases stress.",
            "severity": "Medium"
        })
        
    # 9. Manager Relationship / Tenure
    years_mgr = emp_record.get("YearsWithCurrManager", 0)
    if years_mgr < 1 and years_co >= 2:
        factors.append({
            "factor": "Recent Manager Transition",
            "detail": "Under current manager for less than 1 year, often a vulnerable adjustment period.",
            "severity": "Low"
        })
        
    # 10. Low Salary Hike
    hike = emp_record.get("PercentSalaryHike", 15)
    if hike <= 12:
        factors.append({
            "factor": "Below-Average Salary Increment",
            "detail": f"Latest salary hike was {hike}%, which may cause sentiment of under-appreciation.",
            "severity": "Low"
        })
        
    return factors

def predict_employee_attrition(emp_record: Dict[str, Any], df_context: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Takes an employee record dictionary, automatically constructs the feature vector,
    invokes the Random Forest ML pipeline, and returns predictions, risk score,
    risk level, and identified risk factors.
    """
    pipeline, metadata = load_trained_model()
    
    # Prepare input dataframe with exact feature ordering
    input_data = {}
    for feat in NUMERICAL_FEATURES:
        val = emp_record.get(feat, 0)
        try:
            input_data[feat] = [float(val)]
        except (ValueError, TypeError):
            input_data[feat] = [0.0]
            
    for feat in CATEGORICAL_FEATURES:
        val = emp_record.get(feat, "")
        input_data[feat] = [str(val)]
        
    input_df = pd.DataFrame(input_data)
    
    # Run Random Forest inference
    prob = float(pipeline.predict_proba(input_df)[0][1])
    pred_class = int(pipeline.predict(input_df)[0])
    
    risk_score = round(prob * 100.0, 1)
    risk_level, color_hex = determine_risk_level(risk_score)
    prediction_label = "High Risk of Attrition" if risk_score >= 50.0 else "Likely to Stay"
    
    # Extract concrete risk drivers
    factors = identify_risk_factors(emp_record, df_context)

    # Growth Status and Confidence analysis
    from utils.ai_analysis import (
        evaluate_employee_growth_status,
        evaluate_prediction_confidence,
        check_priority_retention
    )
    confidence = evaluate_prediction_confidence(prob)
    growth_status = evaluate_employee_growth_status(emp_record)
    is_priority, priority_label = check_priority_retention(growth_status, risk_level)
    
    return {
        "employee_id": str(emp_record.get("EmployeeNumber", "")),
        "prediction": prediction_label,
        "predicted_class": pred_class,
        "attrition_probability": round(prob, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "color_hex": color_hex,
        "risk_factors": factors,
        "growth_status": growth_status,
        "confidence": confidence,
        "priority_retention": priority_label,
        "is_priority_retention": is_priority
    }
