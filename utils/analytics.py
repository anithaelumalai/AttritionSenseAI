import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import plotly.express as px
import plotly.graph_objects as go

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.data_loader import load_employee_dataset
from utils.ml_pipeline import load_trained_model, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

def compute_overall_dataset_metrics() -> Dict[str, Any]:
    """
    Computes comprehensive organizational metrics and batch risk distribution
    for the entire 1,470-employee workforce using the trained Random Forest model.
    """
    df = load_employee_dataset()
    total_count = len(df)
    
    # Run batch inference if needed for organizational risk profile
    pipeline, metadata = load_trained_model()
    
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    probs = pipeline.predict_proba(X)[:, 1]
    scores = probs * 100.0
    
    high_risk_count = int((scores >= 70.0).sum())
    med_risk_count = int(((scores >= 40.0) & (scores < 70.0)).sum())
    low_risk_count = int((scores < 40.0).sum())
    
    avg_score = float(round(scores.mean(), 1))
    historical_attrition_count = int((df["Attrition"] == "Yes").sum())
    historical_attrition_rate = round((historical_attrition_count / total_count) * 100.0, 1)
    
    return {
        "total_employees": total_count,
        "historical_attrition_count": historical_attrition_count,
        "historical_attrition_rate": historical_attrition_rate,
        "avg_risk_score": avg_score,
        "high_risk_count": high_risk_count,
        "med_risk_count": med_risk_count,
        "low_risk_count": low_risk_count,
        "high_risk_pct": round((high_risk_count / total_count) * 100.0, 1),
        "med_risk_pct": round((med_risk_count / total_count) * 100.0, 1),
        "low_risk_pct": round((low_risk_count / total_count) * 100.0, 1),
    }

def create_attrition_by_department_chart(df: Optional[pd.DataFrame] = None) -> go.Figure:
    if df is None:
        df = load_employee_dataset()
        
    dept_attr = df.groupby(["Department", "Attrition"]).size().reset_index(name="Count")
    fig = px.bar(
        dept_attr,
        x="Department",
        y="Count",
        color="Attrition",
        barmode="group",
        color_discrete_map={"Yes": "#e63946", "No": "#2a9d8f"},
        title="Employee Attrition Distribution by Department"
    )
    fig.update_layout(
        xaxis_title="Department",
        yaxis_title="Headcount",
        legend_title="Attrition",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_attrition_by_job_role_chart(df: Optional[pd.DataFrame] = None) -> go.Figure:
    if df is None:
        df = load_employee_dataset()
        
    role_rate = df.groupby("JobRole")["Attrition"].apply(lambda x: (x == "Yes").mean() * 100.0).reset_index(name="AttritionRate")
    role_rate = role_rate.sort_values(by="AttritionRate", ascending=True)
    
    fig = px.bar(
        role_rate,
        y="JobRole",
        x="AttritionRate",
        orientation="h",
        color="AttritionRate",
        color_continuous_scale=["#2a9d8f", "#e9c46a", "#e63946"],
        title="Attrition Rate by Job Role (%)"
    )
    fig.update_layout(
        xaxis_title="Attrition Rate (%)",
        yaxis_title="Job Role",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_attrition_by_overtime_chart(df: Optional[pd.DataFrame] = None) -> go.Figure:
    if df is None:
        df = load_employee_dataset()
        
    ot_df = df.groupby(["OverTime", "Attrition"]).size().reset_index(name="Count")
    fig = px.bar(
        ot_df,
        x="OverTime",
        y="Count",
        color="Attrition",
        barmode="stack",
        color_discrete_map={"Yes": "#e63946", "No": "#2a9d8f"},
        title="Impact of Overtime on Employee Attrition"
    )
    fig.update_layout(
        xaxis_title="Overtime Status",
        yaxis_title="Headcount",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_attrition_by_satisfaction_chart(df: Optional[pd.DataFrame] = None) -> go.Figure:
    if df is None:
        df = load_employee_dataset()
        
    sat_df = df.groupby("JobSatisfaction")["Attrition"].apply(lambda x: (x == "Yes").mean() * 100.0).reset_index(name="Rate")
    sat_df["JobSatisfaction_Label"] = sat_df["JobSatisfaction"].map({
        1: "1 - Low", 2: "2 - Medium", 3: "3 - High", 4: "4 - Very High"
    })
    
    fig = px.bar(
        sat_df,
        x="JobSatisfaction_Label",
        y="Rate",
        color="Rate",
        color_continuous_scale=["#2a9d8f", "#e76f51"],
        title="Attrition Rate by Job Satisfaction Level (%)"
    )
    fig.update_layout(
        xaxis_title="Job Satisfaction Rating",
        yaxis_title="Attrition Rate (%)",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_income_distribution_chart(df: Optional[pd.DataFrame] = None) -> go.Figure:
    if df is None:
        df = load_employee_dataset()
        
    fig = px.box(
        df,
        x="Attrition",
        y="MonthlyIncome",
        color="Attrition",
        color_discrete_map={"Yes": "#e63946", "No": "#2a9d8f"},
        title="Monthly Compensation Distribution vs. Attrition"
    )
    fig.update_layout(
        xaxis_title="Attrition",
        yaxis_title="Monthly Income ($)",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_tenure_promotion_chart(df: Optional[pd.DataFrame] = None) -> go.Figure:
    if df is None:
        df = load_employee_dataset()
        
    fig = px.scatter(
        df,
        x="YearsAtCompany",
        y="YearsSinceLastPromotion",
        color="Attrition",
        color_discrete_map={"Yes": "#e63946", "No": "#2a9d8f"},
        opacity=0.7,
        title="Years at Company vs. Years Since Last Promotion"
    )
    fig.update_layout(
        xaxis_title="Total Years at Company",
        yaxis_title="Years Since Last Promotion",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_risk_distribution_donut(metrics: Dict[str, Any]) -> go.Figure:
    """Generates an executive donut chart showing current risk tier distribution."""
    labels = ["Low Risk (0-39)", "Medium Risk (40-69)", "High Risk (70-100)"]
    values = [metrics["low_risk_count"], metrics["med_risk_count"], metrics["high_risk_count"]]
    colors_list = ["#2a9d8f", "#f4a261", "#e63946"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors_list),
        textinfo="label+percent",
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        title="Workforce Risk Level Distribution",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig
