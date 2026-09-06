import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.auth import authenticate_employee, authenticate_hr
from utils.feedback import save_employee_feedback, get_latest_feedback, get_feedback_metrics, get_feedback_records

def test_full_feedback_workflow():
    print("=" * 65)
    print("TESTING FULL FEEDBACK -> HR WORKFLOW")
    print("=" * 65)

    # Step 1: Employee Login
    print("\n1. Testing Employee Login...")
    ok_emp, user_emp, msg_emp = authenticate_employee("1", "emp123")
    assert ok_emp and user_emp["role"] == "employee"
    print(f"[PASS] Employee #{user_emp['identifier']} successfully logged in.")

    # Record baseline feedback count
    metrics_before = get_feedback_metrics()
    count_before = metrics_before["total_feedback"]
    print(f"   Current total feedback count before new submission: {count_before}")

    # Step 2: Employee fills and submits feedback
    print("\n2. Submitting Feedback from Employee...")
    test_payload = {
        "employee_id": "1",
        "is_anonymous": True,  # test anonymous submission
        "job_satisfaction": 5,
        "work_life_balance": 4,
        "manager_support": 5,
        "workload": 3,
        "career_growth": 4,
        "recognition": 5,
        "compensation_satisfaction": 4,
        "intention_to_stay": 5,
        "comments": "Great flexibility and supportive team environment."
    }
    
    save_ok, email_msg = save_employee_feedback(test_payload)
    assert save_ok, f"Failed to save feedback: {email_msg}"
    print(f"[PASS] Feedback saved successfully! Status message: {email_msg}")

    # Step 3: Verify HR Email attempted / sent
    print("\n3. Verifying HR Notification Email behavior...")
    # Since SMTP is unconfigured in test environment, verify message properly reflects this
    assert "Feedback saved successfully, but HR email notification is not configured" in email_msg or "Notification email sent to HR" in email_msg
    print(f"[PASS] Email notification handled gracefully without false claims.")

    # Step 4: HR Login
    print("\n4. Testing HR Login...")
    ok_hr, user_hr, msg_hr = authenticate_hr("admin", "admin123")
    assert ok_hr and user_hr["role"] == "hr"
    print(f"[PASS] HR Administrator '{user_hr['identifier']}' successfully logged in.")

    # Step 5: HR Dashboard shows New Employee Feedback
    print("\n5. Verifying New Employee Feedback card in HR Dashboard...")
    latest = get_latest_feedback()
    assert latest is not None, "Latest feedback is None!"
    assert latest["is_anonymous"] == 1, "Expected anonymous flag to be 1"
    assert latest["employee_id"] is None, "Employee ID was exposed for anonymous feedback!"
    assert latest["job_satisfaction"] == 5, f"Expected Job Sat 5, got {latest['job_satisfaction']}"
    assert "Great flexibility" in latest["comments"], "Comments not matched in latest submission"
    assert latest["created_at"] is not None and len(latest["created_at"]) > 10, "Timestamp missing!"
    print(f"[PASS] Latest feedback visible: Submitter is Anonymous, Time: {latest['created_at']}, Comments: '{latest['comments']}'")

    # Step 6: Feedback Analytics automatically updated
    print("\n6. Verifying HR Feedback Analytics updated...")
    metrics_after = get_feedback_metrics()
    count_after = metrics_after["total_feedback"]
    assert count_after == count_before + 1, f"Expected {count_before + 1} submissions, found {count_after}"
    print(f"[PASS] Feedback Analytics metrics updated! New total submissions: {count_after}")
    print(f"       Avg Job Sat: {metrics_after['avg_job_satisfaction']}/5, Stay Intent: {metrics_after['stay_intent_pct']}%")

    print("\n" + "=" * 65)
    print("ALL WORKFLOW STEPS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    test_full_feedback_workflow()
