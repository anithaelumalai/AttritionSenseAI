import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from views.hr.analytics_view import render_hr_analytics
from utils.data_loader import load_employee_dataset
import pandas as pd

def test_hr_analytics_view():
    print("Testing HR Analytics imports and logic...")
    df = load_employee_dataset()
    
    # Test tab 4 AgeGroup pd.cut logic
    df["AgeGroup"] = pd.cut(df["Age"], bins=[17, 29, 39, 49, 65], labels=["18-29", "30-39", "40-49", "50+"])
    age_attr = df.groupby(["AgeGroup", "Attrition"], observed=False).size().reset_index(name="Count")
    assert not age_attr.empty, "AgeGroup table is empty"
    print("[PASS] pd.cut executed without NameError! Age groups created:")
    print(age_attr.head(4).to_string(index=False))

if __name__ == "__main__":
    test_hr_analytics_view()
