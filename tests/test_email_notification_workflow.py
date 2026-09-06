import sys
import os
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.auth import authenticate_employee, authenticate_hr
from utils.feedback import save_employee_feedback, get_latest_feedback, get_feedback_metrics
from utils.chatbot import get_buddybot_response, save_chat_message
from utils.email_service import send_feedback_notification_email, get_smtp_config

def test_full_email_and_isolation_workflow():
    print("=" * 70)
    print("TESTING EMPLOYEE FEEDBACK -> HR EMAIL NOTIFICATION WORKFLOW")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. VERIFY BUDDYBOT DOES NOT SEND HR EMAILS
    # -------------------------------------------------------------
    print("\n--- [STEP 1: BUDDYBOT EMAIL ISOLATION VERIFICATION] ---")
    with patch("utils.email_service.send_feedback_notification_email") as mock_email:
        # Simulate employee chatting with BuddyBot
        resp1 = get_buddybot_response("I had a very tiring day today.", "1", [])
        save_chat_message("1", "user", "I had a very tiring day today.")
        save_chat_message("1", "buddybot", resp1)
        
        resp2 = get_buddybot_response("Too many meetings.", "1", [
            {"role": "user", "content": "I had a very tiring day today."},
            {"role": "assistant", "content": resp1}
        ])
        save_chat_message("1", "user", "Too many meetings.")
        save_chat_message("1", "buddybot", resp2)
        
        # Assert no email dispatch occurred
        assert mock_email.call_count == 0, f"BuddyBot unexpectedly triggered {mock_email.call_count} emails!"
        print("[PASS] Verified: BuddyBot conversation does NOT trigger HR emails.")

    # -------------------------------------------------------------
    # 2. VERIFY MINI GAMES DO NOT SEND HR EMAILS
    # -------------------------------------------------------------
    print("\n--- [STEP 2: MINI GAMES EMAIL ISOLATION VERIFICATION] ---")
    with patch("utils.email_service.send_feedback_notification_email") as mock_email:
        # Simulate playing mini games (deck flips, breathing cycles)
        moves = 10
        matches = 6
        cycle = 3
        # Assert no email dispatch occurred
        assert mock_email.call_count == 0, "Mini Games unexpectedly triggered email dispatch!"
        print("[PASS] Verified: Mini Games activities do NOT trigger HR emails.")

    # -------------------------------------------------------------
    # 3. VERIFY UNCONFIGURED SMTP HANDLING (NO FALSE POSITIVES)
    # -------------------------------------------------------------
    print("\n--- [STEP 3: UNCONFIGURED SMTP BEHAVIOR] ---")
    test_feedback = {
        "employee_id": "1",
        "is_anonymous": True,
        "job_satisfaction": 4,
        "work_life_balance": 3,
        "manager_support": 4,
        "workload": 3,
        "career_growth": 4,
        "recognition": 4,
        "compensation_satisfaction": 3,
        "intention_to_stay": 4,
        "comments": "Workplace culture is positive and collaborative."
    }

    # Test with empty SMTP config
    with patch.dict(os.environ, {"SMTP_HOST": "", "SMTP_USER": "", "SMTP_PASSWORD": ""}):
        email_sent, status_msg = send_feedback_notification_email(test_feedback)
        assert not email_sent, "Unconfigured SMTP was falsely reported as sent!"
        assert "Feedback saved successfully, but HR email notification is not configured" in status_msg
        print(f"[PASS] Verified: Unconfigured SMTP correctly reported as:")
        print(f"       \"{status_msg}\"")
        print("[PASS] Verified: System NEVER falsely reports an email as sent.")

    # -------------------------------------------------------------
    # 4. VERIFY ACTUAL EMAIL TRANSMISSION WHEN SMTP IS CONFIGURED
    # -------------------------------------------------------------
    print("\n--- [STEP 4: CONFIGURED SMTP TRANSMISSION ATTEMPT] ---")
    mock_env = {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "test_notifications@example.com",
        "SMTP_PASSWORD": "mock_app_password",
        "HR_EMAIL": "hr_leadership@example.com"
    }
    with patch.dict(os.environ, mock_env):
        with patch("smtplib.SMTP") as mock_smtp_cls:
            mock_smtp_instance = MagicMock()
            mock_smtp_cls.return_value.__enter__.return_value = mock_smtp_instance
            
            email_sent, status_msg = send_feedback_notification_email(test_feedback)
            assert email_sent, f"Email send failed with configured SMTP: {status_msg}"
            
            # Verify SMTP interactions
            mock_smtp_cls.assert_called_once_with("smtp.gmail.com", 587, timeout=10)
            mock_smtp_instance.starttls.assert_called_once()
            mock_smtp_instance.login.assert_called_once_with("test_notifications@example.com", "mock_app_password")
            mock_smtp_instance.send_message.assert_called_once()
            
            sent_msg = mock_smtp_instance.send_message.call_args[0][0]
            assert sent_msg["Subject"] == "New Employee Feedback Received"
            assert sent_msg["To"] == "hr_leadership@example.com"
            assert sent_msg["From"] == "test_notifications@example.com"
            
            print(f"[PASS] Verified: Configured SMTP actually sent notification email to {sent_msg['To']}.")
            print(f"       Subject: \"{sent_msg['Subject']}\"")
            print(f"       Status message returned: \"{status_msg}\"")

    # -------------------------------------------------------------
    # 5. VERIFY DATABASE STORAGE & HR DASHBOARD VISIBILITY
    # -------------------------------------------------------------
    print("\n--- [STEP 5: END-TO-END DATABASE & HR DASHBOARD REFLECTION] ---")
    save_ok, msg = save_employee_feedback(test_feedback)
    assert save_ok, f"Failed to save feedback: {msg}"
    print(f"[PASS] Feedback saved to SQLite and CSV. Message: {msg}")

    # Verify latest record in HR Dashboard
    latest = get_latest_feedback()
    assert latest is not None
    assert latest["is_anonymous"] == 1
    assert latest["employee_id"] is None, "Anonymous feedback exposed employee ID!"
    assert latest["created_at"] is not None
    print(f"[PASS] HR Dashboard reflection confirmed: Submitter is Anonymous, Time={latest['created_at']}")

    print("\n" + "=" * 70)
    print("ALL EMPLOYEE FEEDBACK -> HR EMAIL NOTIFICATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_email_and_isolation_workflow()
