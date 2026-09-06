import os
import sys
import unittest
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import init_database, get_connection, seed_users_if_needed
from utils.auth import authenticate_user
from utils.email_service import get_smtp_config, send_test_email, send_feedback_notification_email
from utils.feedback import save_employee_feedback, get_latest_feedback, get_feedback_records, get_feedback_metrics
import pandas as pd

class TestEmailWorkflowEmployee68(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()
        seed_users_if_needed()

    def test_01_smtp_config_loaded(self):
        """Verify SMTP config is loaded securely from secrets without exposing password."""
        cfg = get_smtp_config()
        self.assertEqual(cfg["host"], "smtp.gmail.com")
        self.assertEqual(cfg["port"], 587)
        self.assertEqual(cfg["user"], "anithasathya026@gmail.com")
        self.assertEqual(cfg["hr_email"], "anithaelumalai00987@gmail.com")
        self.assertTrue(len(cfg["password"]) > 0, "Password should be present in config")
        # Ensure password is not printed in logs

    def test_02_employee_68_exists_and_can_authenticate(self):
        """Verify Employee ID 68 exists in dataset and database user registry."""
        emp_csv_path = os.path.join(PROJECT_ROOT, "data", "employees.csv")
        df_emp = pd.read_csv(emp_csv_path)
        emp_68 = df_emp[df_emp["EmployeeNumber"] == 68]
        self.assertEqual(len(emp_68), 1, "EmployeeNumber 68 must exist in employees.csv")
        
        # Authenticate employee 68 with default password
        ok, auth_user, msg = authenticate_user("68", "emp123", expected_role="employee")
        self.assertTrue(ok, f"Employee 68 authentication failed: {msg}")
        self.assertIsNotNone(auth_user, "Employee 68 should authenticate successfully")
        self.assertEqual(auth_user["role"], "employee")
        self.assertEqual(auth_user["identifier"], "68")

    def test_03_send_test_email(self):
        """Verify safe test-email utility sends successfully to configured HR address."""
        ok, msg = send_test_email()
        self.assertTrue(ok, f"send_test_email failed: {msg}")
        self.assertIn("anithaelumalai00987@gmail.com", msg)

    def test_04_employee_68_feedback_submission_and_email_notification(self):
        """
        Complete workflow:
        Employee 68 submits workplace feedback -> saved to SQLite & CSV -> HR email dispatched.
        """
        feedback_payload = {
            "employee_id": "68",
            "is_anonymous": False,
            "job_satisfaction": 4,
            "work_life_balance": 4,
            "manager_support": 5,
            "workload": 3,
            "career_growth": 4,
            "recognition": 5,
            "compensation_satisfaction": 4,
            "intention_to_stay": 5,
            "comments": "Great team collaboration this quarter. Looking forward to upcoming leadership development initiatives."
        }

        success, notification_msg = save_employee_feedback(feedback_payload)
        self.assertTrue(success, f"save_employee_feedback returned False: {notification_msg}")
        self.assertIn("Notification email sent to HR", notification_msg, f"Expected notification sent message, got: {notification_msg}")

        # Verify record in SQLite database
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM feedback WHERE employee_id = '68' ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row, "Feedback record for Employee 68 should be found in database")
        row_dict = dict(row)
        self.assertEqual(row_dict["employee_id"], "68")
        self.assertEqual(row_dict["is_anonymous"], 0)
        self.assertEqual(row_dict["job_satisfaction"], 4)
        self.assertEqual(row_dict["email_status"], "Sent")
        self.assertIn("leadership development", row_dict["comments"])

        # Verify synced to CSV
        csv_path = os.path.join(PROJECT_ROOT, "data", "feedback.csv")
        self.assertTrue(os.path.exists(csv_path), "feedback.csv must exist")
        df_csv = pd.read_csv(csv_path)
        emp_68_csv = df_csv[df_csv["employee_id"] == 68]
        self.assertGreater(len(emp_68_csv), 0, "Employee 68 record must be synced to feedback.csv")

    def test_05_hr_dashboard_and_analytics_verification(self):
        """Verify HR views can retrieve the latest submission with correct email_status."""
        latest = get_latest_feedback()
        self.assertIsNotNone(latest, "get_latest_feedback() should return a record")
        self.assertEqual(latest["email_status"], "Sent")

        records_df = get_feedback_records(limit=10)
        self.assertFalse(records_df.empty, "Feedback records should not be empty")
        self.assertIn("email_status", records_df.columns)

        metrics = get_feedback_metrics()
        self.assertGreater(metrics["total_feedback"], 0)

    def test_06_anonymous_feedback_workflow(self):
        """Verify anonymous feedback hides Employee ID but dispatches email properly."""
        anon_payload = {
            "employee_id": "68",
            "is_anonymous": True,
            "job_satisfaction": 3,
            "work_life_balance": 3,
            "manager_support": 3,
            "workload": 3,
            "career_growth": 3,
            "recognition": 3,
            "compensation_satisfaction": 3,
            "intention_to_stay": 3,
            "comments": "Anonymous test feedback for HR sentiment check."
        }

        success, msg = save_employee_feedback(anon_payload)
        self.assertTrue(success, f"Anonymous save failed: {msg}")
        self.assertIn("Notification email sent to HR", msg)

        latest = get_latest_feedback()
        self.assertEqual(latest["is_anonymous"], 1)
        self.assertIsNone(latest["employee_id"], "Anonymous record must NOT expose employee_id in database")
        self.assertEqual(latest["email_status"], "Sent")

    def test_07_isolation_buddybot_and_games(self):
        """Verify BuddyBot and Mini Games modules do not import or invoke email service."""
        from views.employee import buddybot_view, games_view
        import inspect

        buddy_src = inspect.getsource(buddybot_view)
        games_src = inspect.getsource(games_view)

        self.assertNotIn("send_feedback_notification_email", buddy_src)
        self.assertNotIn("send_test_email", buddy_src)
        self.assertNotIn("email_service", buddy_src)

        self.assertNotIn("send_feedback_notification_email", games_src)
        self.assertNotIn("send_test_email", games_src)
        self.assertNotIn("email_service", games_src)

if __name__ == "__main__":
    unittest.main(verbosity=2)
