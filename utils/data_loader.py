import os
import pandas as pd
from typing import Optional, Dict, List, Any
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "employees.csv")

@st.cache_data(show_spinner=False)
def load_employee_dataset(filepath: str = DATA_PATH) -> pd.DataFrame:
    """
    Loads and caches the employee dataset.
    Ensures EmployeeNumber is parsed properly.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Employee dataset not found at {filepath}. Please run setup_data.py first.")
    
    df = pd.read_csv(filepath)
    # Ensure EmployeeNumber is integer
    if "EmployeeNumber" in df.columns:
        df["EmployeeNumber"] = df["EmployeeNumber"].astype(int)
    return df

def get_employee_by_id(emp_id: Any, df: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves complete employee record for the given EmployeeNumber.
    Returns None if EmployeeNumber does not exist.
    """
    if df is None:
        df = load_employee_dataset()
    try:
        emp_num = int(emp_id)
    except (ValueError, TypeError):
        return None
        
    record = df[df["EmployeeNumber"] == emp_num]
    if record.empty:
        return None
    return record.iloc[0].to_dict()

def get_all_employee_ids(df: Optional[pd.DataFrame] = None) -> List[int]:
    """Returns sorted list of all actual EmployeeNumbers present in dataset."""
    if df is None:
        df = load_employee_dataset()
    return sorted(df["EmployeeNumber"].unique().tolist())

def validate_employee_id(emp_id: Any, df: Optional[pd.DataFrame] = None) -> bool:
    """Checks if an EmployeeNumber exists in the dataset."""
    if df is None:
        df = load_employee_dataset()
    try:
        emp_num = int(emp_id)
        return emp_num in df["EmployeeNumber"].values
    except (ValueError, TypeError):
        return False

def get_dataset_summary(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Calculates high-level dataset statistics."""
    if df is None:
        df = load_employee_dataset()
        
    total_count = len(df)
    attrition_count = (df["Attrition"] == "Yes").sum() if "Attrition" in df.columns else 0
    attrition_rate = (attrition_count / total_count * 100) if total_count > 0 else 0.0
    
    return {
        "total_employees": total_count,
        "attrition_count": int(attrition_count),
        "attrition_rate": round(attrition_rate, 2),
        "avg_age": round(df["Age"].mean(), 1) if "Age" in df.columns else 0,
        "avg_monthly_income": round(df["MonthlyIncome"].mean(), 2) if "MonthlyIncome" in df.columns else 0,
        "departments": df["Department"].unique().tolist() if "Department" in df.columns else [],
        "job_roles": df["JobRole"].unique().tolist() if "JobRole" in df.columns else []
    }
