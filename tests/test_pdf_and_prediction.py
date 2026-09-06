import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.data_loader import get_employee_by_id
from utils.prediction import predict_employee_attrition
from utils.recommendation import generate_retention_recommendations
from utils.pdf_report import generate_pdf_report
from utils.history import save_prediction_record, get_all_prediction_history

def test_pipeline():
    print("Testing employee retrieval for Employee ID 1...")
    emp = get_employee_by_id(1)
    assert emp is not None, "Failed to load Employee 1"
    print(f"[PASS] Employee 1 loaded: Age={emp['Age']}, Dept={emp['Department']}, Role={emp['JobRole']}")

    print("\nTesting ML prediction...")
    pred = predict_employee_attrition(emp)
    print(f"[PASS] Prediction: {pred['prediction']}, Probability: {pred['attrition_probability']}, Risk Score: {pred['risk_score']}, Level: {pred['risk_level']}")
    print(f"       Detected {len(pred['risk_factors'])} risk factors:")
    for f in pred["risk_factors"]:
        print(f"         - {f['factor']} ({f['severity']})")

    print("\nTesting retention recommendations...")
    recs = generate_retention_recommendations(emp, pred["risk_factors"])
    print(f"[PASS] Generated {len(recs)} retention recommendations:")
    for r in recs:
        print(f"         - [{r['priority']}] {r['title']}")

    print("\nTesting PDF report generation...")
    pdf_bytes = generate_pdf_report(emp, pred, recs)
    assert len(pdf_bytes) > 1000, "PDF bytes too small"
    print(f"[PASS] PDF report generated successfully ({len(pdf_bytes)} bytes)")

    print("\nTesting prediction history logging...")
    rec_id = save_prediction_record(
        emp["EmployeeNumber"],
        pred["prediction"],
        pred["attrition_probability"],
        pred["risk_score"],
        pred["risk_level"],
        pred["risk_factors"],
        recs
    )
    print(f"[PASS] Saved prediction record #{rec_id}")

    hist_df = get_all_prediction_history(limit=5)
    assert len(hist_df) > 0, "No prediction history retrieved"
    print(f"[PASS] History retrieved {len(hist_df)} rows")

    print("\nALL PREDICTION, RECOMMENDATION, PDF, AND HISTORY TESTS PASSED!")

if __name__ == "__main__":
    test_pipeline()
