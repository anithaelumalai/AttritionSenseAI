import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report, confusion_matrix
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "attrition_model.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

# Columns to explicitly drop from ML training features
DROP_COLUMNS = ["EmployeeNumber", "EmployeeCount", "Over18", "StandardHours"]
TARGET_COLUMN = "Attrition"

CATEGORICAL_FEATURES = [
    "BusinessTravel",
    "Department",
    "EducationField",
    "Gender",
    "JobRole",
    "MaritalStatus",
    "OverTime"
]

NUMERICAL_FEATURES = [
    "Age",
    "DailyRate",
    "DistanceFromHome",
    "Education",
    "EnvironmentSatisfaction",
    "HourlyRate",
    "JobInvolvement",
    "JobLevel",
    "JobSatisfaction",
    "MonthlyIncome",
    "MonthlyRate",
    "NumCompaniesWorked",
    "PercentSalaryHike",
    "PerformanceRating",
    "RelationshipSatisfaction",
    "StockOptionLevel",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "WorkLifeBalance",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager"
]

def build_pipeline() -> Pipeline:
    """Constructs the Scikit-learn Pipeline with preprocessor and Random Forest."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=250,
            max_depth=12,
            min_samples_split=6,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
    return pipeline

def train_and_evaluate_model(df: pd.DataFrame) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Trains Random Forest on the dataset, calculates evaluation metrics,
    and extracts top feature importances.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Verify required columns
    missing_cols = [c for c in NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for ML: {missing_cols}")
        
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    y = df[TARGET_COLUMN].apply(lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true"] else 0)
    
    # 80/20 Stratified Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    # Calculate performance metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    conf_mat = confusion_matrix(y_test, y_pred).tolist()
    
    # Extract Feature Importances
    preprocessor = pipeline.named_steps["preprocessor"]
    rf = pipeline.named_steps["classifier"]
    
    cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = list(NUMERICAL_FEATURES) + list(cat_feature_names)
    importances = rf.feature_importances_
    
    feature_ranking = sorted(
        [{"feature": name, "importance": float(round(imp, 4))} for name, imp in zip(all_feature_names, importances)],
        key=lambda x: x["importance"],
        reverse=True
    )
    
    metadata = {
        "model_name": "RandomForestClassifier",
        "parameters": {
            "n_estimators": 250,
            "max_depth": 12,
            "min_samples_split": 6,
            "class_weight": "balanced",
            "random_state": 42
        },
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": conf_mat
        },
        "feature_ranking": feature_ranking[:20],
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "train_size": len(X_train),
        "test_size": len(X_test)
    }
    
    # Save model and metadata
    joblib.dump(pipeline, MODEL_PATH)
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Model successfully saved to {MODEL_PATH}")
    print(f"Metadata saved to {METADATA_PATH}")
    return pipeline, metadata

def load_trained_model() -> Tuple[Pipeline, Dict[str, Any]]:
    """Loads the trained pipeline and metadata from disk."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(f"Model artifacts not found at {MODEL_PATH}. Please run train_model.py first.")
    pipeline = joblib.load(MODEL_PATH)
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)
    return pipeline, metadata
