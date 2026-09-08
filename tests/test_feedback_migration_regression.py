import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import migrate_feedback_table_if_needed, get_db_path
from utils.feedback import save_employee_feedback, get_feedback_records, get_feedback_metrics

def test_missing_intention_to_stay_migration_and_save_first():
    print("=" * 70)
    print("REGRESSION TEST: MISSING 'intention_to_stay' AUTO-MIGRATION & SAVE-FIRST")
    print("=" * 70)

    test_db_path = os.path.join(PROJECT_ROOT, "database", "test_regression_legacy.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # 1. Create a legacy table DELIBERATELY missing intention_to_stay and email_status
    conn = sqlite3.connect(test_db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        is_anonymous INTEGER NOT NULL DEFAULT 0,
        job_satisfaction INTEGER NOT NULL,
        work_life_balance INTEGER NOT NULL,
        manager_support INTEGER NOT NULL,
        workload INTEGER NOT NULL,
        career_growth INTEGER NOT NULL,
        recognition INTEGER NOT NULL,
        compensation_satisfaction INTEGER NOT NULL,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Insert 2 existing legacy feedback entries
    cur.execute("INSERT INTO feedback (employee_id, job_satisfaction, work_life_balance, manager_support, workload, career_growth, recognition, compensation_satisfaction, comments) VALUES ('101', 4, 4, 4, 3, 4, 4, 4, 'Existing feedback from 2025');")
    cur.execute("INSERT INTO feedback (employee_id, job_satisfaction, work_life_balance, manager_support, workload, career_growth, recognition, compensation_satisfaction, comments) VALUES ('102', 3, 3, 3, 3, 3, 3, 3, 'Another old feedback');")
    conn.commit()

    # Verify column is missing
    cur.execute("PRAGMA table_info(feedback)")
    initial_cols = [c[1] for c in cur.fetchall()]
    assert "intention_to_stay" not in initial_cols, "intention_to_stay must NOT be present yet!"
    assert "email_status" not in initial_cols, "email_status must NOT be present yet!"
    print("[STEP 1 PASS] Created legacy feedback table with 2 rows. Verified intention_to_stay is missing.")
    conn.close()

    # 2. Mock get_connection to point to test_regression_legacy.db
    def get_test_conn():
        c = sqlite3.connect(test_db_path, check_same_thread=False)
        c.row_factory = sqlite3.Row
        return c

    # 3. Test submission with intention_to_stay
    new_payload = {
        "employee_id": "103",
        "is_anonymous": False,
        "job_satisfaction": 5,
        "work_life_balance": 4,
        "manager_support": 5,
        "workload": 3,
        "career_growth": 5,
        "recognition": 5,
        "compensation_satisfaction": 4,
        "intention_to_stay": 5,
        "comments": "Testing live auto-migration on submit"
    }

    email_dispatch_log = []
    def mock_send_email(payload):
        # Verify that when this email function is called, the feedback row is ALREADY in the database!
        verify_conn = get_test_conn()
        cur_v = verify_conn.cursor()
        cur_v.execute("SELECT id, employee_id, intention_to_stay FROM feedback WHERE employee_id = '103'")
        saved_row = cur_v.fetchone()
        verify_conn.close()
        assert saved_row is not None, "CRITICAL ERROR: Email was dispatched BEFORE the row was saved in DB!"
        assert saved_row["intention_to_stay"] == 5, f"Saved intention_to_stay mismatch: {saved_row['intention_to_stay']}"
        email_dispatch_log.append("email_dispatched_after_db_save")
        return True, "Notification email sent to HR (test@example.com)."

    with patch("utils.feedback.get_connection", side_effect=get_test_conn), \
         patch("utils.feedback.send_feedback_notification_email", side_effect=mock_send_email):

        success, msg = save_employee_feedback(new_payload)

        assert success is True, f"save_employee_feedback failed: {msg}"
        assert len(email_dispatch_log) == 1, "Email was not dispatched after successful save!"
        print(f"[STEP 2 PASS] save_employee_feedback succeeded! Email was dispatched strictly AFTER DB commit.")

    # 4. Verify database state
    verify_conn = get_test_conn()
    cur_v = verify_conn.cursor()
    cur_v.execute("PRAGMA table_info(feedback)")
    migrated_cols = [c[1] for c in cur_v.fetchall()]
    assert "intention_to_stay" in migrated_cols, "intention_to_stay was not migrated!"
    assert "email_status" in migrated_cols, "email_status was not migrated!"

    # Verify all 3 rows exist (data preservation check)
    cur_v.execute("SELECT id, employee_id, intention_to_stay, email_status, comments FROM feedback ORDER BY id ASC")
    all_rows = cur_v.fetchall()
    assert len(all_rows) == 3, f"Expected 3 rows, found {len(all_rows)}"
    assert all_rows[0]["employee_id"] == "101" and all_rows[0]["intention_to_stay"] == 3, "Legacy row 101 corrupted!"
    assert all_rows[1]["employee_id"] == "102" and all_rows[1]["intention_to_stay"] == 3, "Legacy row 102 corrupted!"
    assert all_rows[2]["employee_id"] == "103" and all_rows[2]["intention_to_stay"] == 5, "New row 103 incorrect!"
    assert all_rows[2]["email_status"] == "Sent", f"Expected email_status 'Sent', got {all_rows[2]['email_status']}"
    print("[STEP 3 PASS] Verified all columns added. Legacy rows preserved. New row saved with intention_to_stay=5 and email_status='Sent'.")
    verify_conn.close()

    # 5. Verify HR Feedback Analytics reads immediately from that same database
    with patch("utils.feedback.get_connection", side_effect=get_test_conn):
        records = get_feedback_records()
        metrics = get_feedback_metrics()

        assert len(records) == 3, f"Expected 3 records in HR analytics, got {len(records)}"
        assert "intention_to_stay" in records.columns, "intention_to_stay missing from HR records DataFrame!"
        assert metrics["total_feedback"] == 3
        # Avg stay: (3 + 3 + 5) / 3 = 3.67
        assert metrics["avg_intention_to_stay"] == 3.67, f"Expected avg stay 3.67, got {metrics['avg_intention_to_stay']}"
        print(f"[STEP 4 PASS] HR Analytics immediately retrieved 3 records from DB. Avg Stay Intent: {metrics['avg_intention_to_stay']}/5.")

    # 6. Verify failure isolation: If DB insert fails, NEVER send email
    email_dispatched_on_fail = []
    def fail_email_catcher(payload):
        email_dispatched_on_fail.append("sent")
        return True, "Email sent"

    with patch("utils.feedback.get_connection") as mock_bad_conn, \
         patch("utils.feedback.send_feedback_notification_email", side_effect=fail_email_catcher):
        
        mock_c = MagicMock()
        mock_c.cursor.side_effect = sqlite3.OperationalError("Simulated locked database")
        mock_bad_conn.return_value = mock_c

        fail_payload = {
            "employee_id": "104",
            "is_anonymous": False,
            "job_satisfaction": 4,
            "intention_to_stay": 4,
            "comments": "This should fail on DB"
        }
        fail_ok, fail_msg = save_employee_feedback(fail_payload)

        assert fail_ok is False, "Expected save to fail on DB error"
        assert "Simulated locked database" in fail_msg or "Failed to save feedback" in fail_msg
        assert len(email_dispatched_on_fail) == 0, "CRITICAL FAILURE: Email was sent despite database save failure!"
        print("[STEP 5 PASS] Database failure properly blocked email dispatch. Real DB error returned.")

    # Cleanup test DB
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    print("=" * 70)
    print("ALL REGRESSION CHECKS PASSED SUCCESSFULLY (5/5)!")
    print("=" * 70)

if __name__ == "__main__":
    test_missing_intention_to_stay_migration_and_save_first()
