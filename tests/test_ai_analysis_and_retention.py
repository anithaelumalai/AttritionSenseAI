import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.ai_analysis import (
    evaluate_employee_growth_status,
    evaluate_attrition_risk,
    evaluate_prediction_confidence,
    check_priority_retention,
    record_priority_retention_alert,
    get_workforce_ai_analysis,
    GROWTH_STATUS_HIGH,
    GROWTH_STATUS_STABLE,
    GROWTH_STATUS_SUPPORT,
    RISK_HIGH,
    RISK_MEDIUM,
    RISK_LOW,
    PRIORITY_RETENTION_LABEL,
    NO_PRIORITY_RETENTION_LABEL
)
from utils.database import init_database, get_connection

class TestAIAnalysisAndRetention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()

    def test_01_growth_status_labels_strictly_valid(self):
        """Verify Growth Status strictly produces one of the 3 approved labels."""
        valid_labels = {GROWTH_STATUS_HIGH, GROWTH_STATUS_STABLE, GROWTH_STATUS_SUPPORT}
        
        # Test high performer record
        high_emp = {
            "PerformanceRating": 4,
            "JobInvolvement": 4,
            "TrainingTimesLastYear": 4,
            "PercentSalaryHike": 20,
            "YearsSinceLastPromotion": 0
        }
        res_high = evaluate_employee_growth_status(high_emp)
        self.assertIn(res_high, valid_labels)
        self.assertEqual(res_high, GROWTH_STATUS_HIGH)

        # Test struggling performer record
        support_emp = {
            "PerformanceRating": 2,
            "JobInvolvement": 1,
            "TrainingTimesLastYear": 0,
            "PercentSalaryHike": 10,
            "YearsSinceLastPromotion": 8
        }
        res_supp = evaluate_employee_growth_status(support_emp)
        self.assertIn(res_supp, valid_labels)
        self.assertEqual(res_supp, GROWTH_STATUS_SUPPORT)

        # Test average contributor record
        stable_emp = {
            "PerformanceRating": 3,
            "JobInvolvement": 2,
            "TrainingTimesLastYear": 2,
            "PercentSalaryHike": 13,
            "YearsSinceLastPromotion": 2
        }
        res_stable = evaluate_employee_growth_status(stable_emp)
        self.assertIn(res_stable, valid_labels)
        self.assertEqual(res_stable, GROWTH_STATUS_STABLE)

    def test_02_attrition_risk_labels_strictly_valid(self):
        """Verify Attrition Risk strictly produces Low, Medium, or High Risk."""
        self.assertEqual(evaluate_attrition_risk(0.15), RISK_LOW)
        self.assertEqual(evaluate_attrition_risk(0.39), RISK_LOW)
        self.assertEqual(evaluate_attrition_risk(0.40), RISK_MEDIUM)
        self.assertEqual(evaluate_attrition_risk(0.69), RISK_MEDIUM)
        self.assertEqual(evaluate_attrition_risk(0.70), RISK_HIGH)
        self.assertEqual(evaluate_attrition_risk(0.95), RISK_HIGH)

    def test_03_prediction_confidence_calculation(self):
        """Verify confidence is max(p, 1-p) * 100%."""
        self.assertEqual(evaluate_prediction_confidence(0.85), 85.0)
        self.assertEqual(evaluate_prediction_confidence(0.15), 85.0)
        self.assertEqual(evaluate_prediction_confidence(0.50), 50.0)
        self.assertEqual(evaluate_prediction_confidence(0.724), 72.4)

    def test_04_priority_retention_combination_matrix(self):
        """
        Verify all 9 combinations of Growth Status & Attrition Risk:
        ONLY High Growth Potential + High Risk triggers Priority Retention.
        """
        growth_statuses = [GROWTH_STATUS_HIGH, GROWTH_STATUS_STABLE, GROWTH_STATUS_SUPPORT]
        risks = [RISK_HIGH, RISK_MEDIUM, RISK_LOW]

        for g in growth_statuses:
            for r in risks:
                is_priority, label = check_priority_retention(g, r)
                if g == GROWTH_STATUS_HIGH and r == RISK_HIGH:
                    self.assertTrue(is_priority, f"Failed for {g} + {r}")
                    self.assertEqual(label, PRIORITY_RETENTION_LABEL)
                else:
                    self.assertFalse(is_priority, f"Should be False for {g} + {r}")
                    self.assertEqual(label, NO_PRIORITY_RETENTION_LABEL)

    def test_05_priority_retention_alert_and_duplicate_prevention(self):
        """Verify alert logging and duplicate prevention."""
        test_emp_id = "TEST_EMP_9999"
        
        # Clean existing test alerts if any
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM retention_alerts WHERE employee_id = ?", (test_emp_id,))
        conn.commit()
        conn.close()

        # 1. Non-priority should not record
        non_pri_res = record_priority_retention_alert(test_emp_id, GROWTH_STATUS_STABLE, RISK_HIGH)
        self.assertFalse(non_pri_res["recorded"])
        self.assertEqual(non_pri_res["status"], "not_applicable")

        # 2. First priority alert should record
        first_alert = record_priority_retention_alert(
            test_emp_id,
            GROWTH_STATUS_HIGH,
            RISK_HIGH,
            {"department": "Engineering", "job_role": "Lead Architect"}
        )
        self.assertTrue(first_alert["recorded"])
        self.assertIn(first_alert["status"], ["sent", "logged"])

        # 3. Second call for same employee and risk must be detected as duplicate
        second_alert = record_priority_retention_alert(
            test_emp_id,
            GROWTH_STATUS_HIGH,
            RISK_HIGH,
            {"department": "Engineering", "job_role": "Lead Architect"}
        )
        self.assertFalse(second_alert["recorded"])
        self.assertEqual(second_alert["status"], "duplicate")

        # Clean up
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM retention_alerts WHERE employee_id = ?", (test_emp_id,))
        conn.commit()
        conn.close()

    def test_06_workforce_ai_analysis_1470_records(self):
        """Verify full workforce analysis handles all 1,470 records completely."""
        df_wf = get_workforce_ai_analysis(force_refresh=True)
        self.assertEqual(len(df_wf), 1470)
        required_cols = [
            "EmployeeNumber", "Name", "Department", "JobRole",
            "GrowthStatus", "AttritionRisk", "PredictionConfidence", "PriorityRetention"
        ]
        for col in required_cols:
            self.assertIn(col, df_wf.columns)

        # Check all records have valid GrowthStatus and AttritionRisk
        for gs in df_wf["GrowthStatus"].unique():
            self.assertIn(gs, {GROWTH_STATUS_HIGH, GROWTH_STATUS_STABLE, GROWTH_STATUS_SUPPORT})
        for ar in df_wf["AttritionRisk"].unique():
            self.assertIn(ar, {RISK_HIGH, RISK_MEDIUM, RISK_LOW})

if __name__ == "__main__":
    unittest.main()
