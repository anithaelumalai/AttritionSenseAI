import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.chatbot import get_buddybot_response, save_chat_message, get_employee_chat_history, clear_employee_chat_history

def test_buddybot():
    emp_id = "1"
    clear_employee_chat_history(emp_id)
    history = []

    # Turn 1
    user_msg_1 = "I had a really tiring day at work."
    resp_1 = get_buddybot_response(user_msg_1, emp_id, history)
    print(f"Turn 1:\n  Employee: {user_msg_1}\n  BuddyBot: {resp_1}\n")
    assert len(resp_1) > 20, "Response 1 too short"
    history.append({"role": "user", "content": user_msg_1})
    history.append({"role": "assistant", "content": resp_1})

    # Turn 2: contextual follow-up on meetings
    user_msg_2 = "Mostly meetings."
    resp_2 = get_buddybot_response(user_msg_2, emp_id, history)
    print(f"Turn 2:\n  Employee: {user_msg_2}\n  BuddyBot: {resp_2}\n")
    assert "meeting" in resp_2.lower() or "calendar" in resp_2.lower() or "focus" in resp_2.lower(), "Contextual follow-up missed"
    history.append({"role": "user", "content": user_msg_2})
    history.append({"role": "assistant", "content": resp_2})

    # Test persistence
    save_chat_message(emp_id, "user", user_msg_1)
    save_chat_message(emp_id, "buddybot", resp_1)
    stored_history = get_employee_chat_history(emp_id)
    assert len(stored_history) == 2, f"Expected 2 stored messages, got {len(stored_history)}"
    print(f"[PASS] Stored private chat history verified ({len(stored_history)} messages)")

    print("\nALL BUDDYBOT TESTS PASSED!")

if __name__ == "__main__":
    test_buddybot()
