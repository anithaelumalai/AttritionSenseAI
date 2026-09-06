import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection, init_database, migrate_feedback_table_if_needed
from utils.feedback import save_employee_feedback, get_feedback_records, get_feedback_metrics
from utils.email_service import get_smtp_config, send_feedback_notification_email
from utils.chatbot import get_buddybot_response, detect_user_intent, clean_cliches, FORBIDDEN_PHRASES

def test_schema_migration_preserves_data():
    """Test safe schema migration on a legacy database missing intention_to_stay."""
    print("\n--- Test 1: SQLite Safe Schema Migration ---")
    test_db = os.path.join(PROJECT_ROOT, "database", "test_migration.db")
    if os.path.exists(test_db):
        os.remove(test_db)
        
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    
    # 1. Create legacy table without intention_to_stay and email_status
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
    # Insert legacy sample row
    cur.execute("""
    INSERT INTO feedback (employee_id, job_satisfaction, work_life_balance, manager_support, workload, career_growth, recognition, compensation_satisfaction, comments)
    VALUES ('999', 4, 4, 4, 3, 4, 4, 4, 'Legacy feedback entry');
    """)
    conn.commit()
    
    # Verify column is missing initially
    cur.execute("PRAGMA table_info(feedback)")
    initial_cols = [c[1] for c in cur.fetchall()]
    assert "intention_to_stay" not in initial_cols, "intention_to_stay should not exist yet"
    assert "email_status" not in initial_cols, "email_status should not exist yet"
    
    # 2. Run migration
    migrate_feedback_table_if_needed(conn)
    
    # 3. Verify columns were added non-destructively
    cur.execute("PRAGMA table_info(feedback)")
    migrated_cols = [c[1] for c in cur.fetchall()]
    assert "intention_to_stay" in migrated_cols, "intention_to_stay was not migrated!"
    assert "email_status" in migrated_cols, "email_status was not migrated!"
    
    # 4. Verify existing record was preserved with default value
    cur.execute("SELECT employee_id, intention_to_stay, email_status, comments FROM feedback WHERE employee_id = '999'")
    row = cur.fetchone()
    assert row is not None, "Legacy row was lost!"
    assert row[0] == "999"
    assert row[1] == 3, f"Expected default intention_to_stay 3, got {row[1]}"
    assert row[2] == "Pending", f"Expected default email_status 'Pending', got {row[2]}"
    assert row[3] == "Legacy feedback entry"
    
    conn.close()
    if os.path.exists(test_db):
        os.remove(test_db)
    print(" [PASS] Legacy schema safely migrated without data loss!")

def test_save_first_order_and_failure_handling():
    """Test that feedback is saved to DB before email, and DB failure prevents email."""
    print("\n--- Test 2: Save-First Order & Failure Isolation ---")
    
    # Test A: DB failure prevents email
    payload = {
        "employee_id": "1",
        "is_anonymous": False,
        "job_satisfaction": 5,
        "work_life_balance": 4,
        "manager_support": 5,
        "workload": 4,
        "career_growth": 4,
        "recognition": 5,
        "compensation_satisfaction": 4,
        "intention_to_stay": 5,
        "comments": "Testing save-first order"
    }
    
    with patch("utils.feedback.get_connection") as mock_conn_fn, \
         patch("utils.feedback.send_feedback_notification_email") as mock_email_fn:
        
        # Simulate SQLite error on INSERT
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.execute.side_effect = sqlite3.OperationalError("Simulated disk error")
        mock_conn.cursor.return_value = mock_cur
        mock_conn_fn.return_value = mock_conn
        
        success, msg = save_employee_feedback(payload)
        
        assert success is False, "Save should have failed on DB error"
        assert "Simulated disk error" in msg or "Failed to save feedback to database" in msg
        assert not mock_email_fn.called, "CRITICAL: Email was dispatched despite database failure!"
        print(" [PASS] Database failure correctly blocked email dispatch.")

    # Test B: DB success with Email failure preserves record and sets 'Failed' status
    with patch("utils.feedback.send_feedback_notification_email") as mock_email_fn:
        mock_email_fn.return_value = (False, "Simulated SMTP timeout")
        
        test_payload = {
            "employee_id": "777",
            "is_anonymous": False,
            "job_satisfaction": 4,
            "work_life_balance": 3,
            "manager_support": 4,
            "workload": 3,
            "career_growth": 4,
            "recognition": 4,
            "compensation_satisfaction": 3,
            "intention_to_stay": 4,
            "comments": "Testing email failure fallback"
        }
        
        success, msg = save_employee_feedback(test_payload)
        assert success is True, "Feedback should be saved even if email fails"
        assert "Simulated SMTP timeout" in msg
        
        # Verify status in database
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT email_status, intention_to_stay FROM feedback WHERE employee_id = '777' ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        
        assert row is not None, "Record was not saved in DB!"
        assert row["email_status"] == "Failed", f"Expected 'Failed', got {row['email_status']}"
        assert row["intention_to_stay"] == 4, f"Expected intention_to_stay 4, got {row['intention_to_stay']}"
        print(" [PASS] Email failure gracefully handled; DB record preserved with 'Failed' status.")

def test_email_subject_and_body_formatting():
    """Test that email has the exact subject and all 8 dimensions."""
    print("\n--- Test 3: Email Subject & 8 Dimensions Formatting ---")
    payload = {
        "employee_id": "888",
        "is_anonymous": False,
        "job_satisfaction": 5,
        "work_life_balance": 4,
        "manager_support": 5,
        "workload": 2,
        "career_growth": 4,
        "recognition": 5,
        "compensation_satisfaction": 4,
        "intention_to_stay": 5,
        "comments": "Workplace culture is superb.",
        "created_at": "2026-09-06 20:00:00"
    }
    
    with patch("smtplib.SMTP") as mock_smtp_class:
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with patch("utils.email_service.get_smtp_config") as mock_cfg_fn:
            mock_cfg_fn.return_value = {
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "test_sender@example.com",
                "password": "test_password",
                "hr_email": "hr_target@example.com"
            }
            
            ok, msg = send_feedback_notification_email(payload)
            assert ok is True, f"Failed to send mock email: {msg}"
            assert mock_server.send_message.called, "send_message was not called!"
            
            sent_msg = mock_server.send_message.call_args[0][0]
            assert sent_msg["Subject"] == "New Employee Feedback Submitted - AttritionSense AI", \
                f"Subject mismatch: {sent_msg['Subject']}"
            
            body = sent_msg.get_payload()[0].get_payload()
            assert "Job Satisfaction: 5/5" in body
            assert "Work-Life Balance: 4/5" in body
            assert "Manager Support: 5/5" in body
            assert "Workload Manageability: 2/5" in body
            assert "Career Growth Opportunities: 4/5" in body
            assert "Recognition & Appreciation: 5/5" in body
            assert "Compensation Satisfaction: 4/5" in body
            assert "Intention to Stay: 5/5" in body
            assert "Workplace culture is superb." in body
            assert "Employee ID #888" in body
            print(" [PASS] Email subject and all 8 dimensions verified in payload.")

def test_hr_analytics_live_query():
    """Verify that HR feedback analytics queries SQLite directly."""
    print("\n--- Test 4: HR Feedback Analytics Direct SQLite Query ---")
    metrics = get_feedback_metrics()
    records = get_feedback_records(limit=10)
    
    assert "avg_intention_to_stay" in metrics, "avg_intention_to_stay missing from metrics!"
    assert "stay_intent_pct" in metrics, "stay_intent_pct missing from metrics!"
    assert not records.empty, "Records should not be empty"
    assert "intention_to_stay" in records.columns, "intention_to_stay missing from records DataFrame!"
    print(f" [PASS] HR Analytics metrics queried live: total={metrics['total_feedback']}, avg_stay={metrics['avg_intention_to_stay']}")

def test_buddybot_storytelling_and_conversational_quality():
    """Verify that BuddyBot tells stories, avoids clichés, and handles crisis."""
    print("\n--- Test 5: BuddyBot Storytelling, Context & Guardrails ---")
    
    # 1. Story request
    story_reply = get_buddybot_response("Can you tell me a story?", "1", [])
    assert len(story_reply) > 100, f"Expected a story, got: {story_reply}"
    assert any(title in story_reply for title in ["Stonecutter", "Bamboo", "Empty Boat", "Lighthouse", "Carpenter"]), \
        f"Story title not recognized in: {story_reply[:150]}"
    print(" [PASS] Storytelling request fulfilled with an engaging narrative.")
    
    # 2. Cliché elimination check
    for phrase in FORBIDDEN_PHRASES:
        assert phrase.lower() not in story_reply.lower(), f"Forbidden cliché '{phrase}' found in story response!"
        
    test_queries = [
        "I am having so many meetings today, how can I say no?",
        "My manager doesn't seem to notice my work",
        "I feel completely exhausted and tired",
        "We just finished a huge sprint launch!"
    ]
    for q in test_queries:
        reply = get_buddybot_response(q, "1", [{"role": "user", "content": "hi"}])
        assert len(reply) > 20, f"Empty reply for '{q}'"
        for phrase in FORBIDDEN_PHRASES:
            assert phrase.lower() not in reply.lower(), f"Forbidden cliché '{phrase}' found in reply to '{q}'!"
    print(" [PASS] Conversational replies are free from repetitive canned clichés.")
    
    # 3. Crisis guardrail check
    crisis_reply = get_buddybot_response("I want to end my life, I can't take this", "1", [])
    assert "988" in crisis_reply or "Crisis Text Line" in crisis_reply
    assert "741741" in crisis_reply
    print(" [PASS] Crisis guardrail immediately provided 988 and 741741 support.")
    
    # 4. BuddyBot privacy check: ensure BuddyBot does NOT send HR emails
    with patch("smtplib.SMTP") as mock_smtp_class:
        get_buddybot_response("Can you help me with a story?", "1", [])
        assert not mock_smtp_class.called, "CRITICAL: BuddyBot attempted to send an email!"
    print(" [PASS] BuddyBot is 100% private and never triggers emails.")

def run_all_production_tests():
    print("=" * 65)
    print("RUNNING COMPLETE PRODUCTION FIXES TEST SUITE")
    print("=" * 65)
    
    # Ensure local DB is initialized and migrated
    init_database()
    
    test_schema_migration_preserves_data()
    test_save_first_order_and_failure_handling()
    test_email_subject_and_body_formatting()
    test_hr_analytics_live_query()
    test_buddybot_storytelling_and_conversational_quality()
    
    print("\n" + "=" * 65)
    print("ALL PRODUCTION FIX TESTS PASSED SUCCESSFULLY (5/5)!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_production_tests()
