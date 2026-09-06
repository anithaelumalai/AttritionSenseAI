import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.chatbot import (
    get_buddybot_response,
    save_chat_message,
    get_employee_chat_history,
    clear_employee_chat_history,
    FORBIDDEN_PHRASES
)

def test_enhanced_buddybot():
    print("=" * 70)
    print("TESTING ENHANCED CONVERSATIONAL BUDDYBOT")
    print("=" * 70)

    emp_id = "test_user_42"
    clear_employee_chat_history(emp_id)
    history = []

    # Sequence of multi-turn conversation
    turns = [
        ("I had a very exhausting day at work today.", "Turn 1: Expressing exhaustion"),
        ("Mostly meetings from 9am to 4pm.", "Turn 2: Contextual follow-up on meetings"),
        ("How should I tell my manager that these syncs are eating all my focus time?", "Turn 3: Direct practical question"),
        ("What is a good 10-minute break activity I can do right now away from screens?", "Turn 4: Topic pivot to wellness breaks"),
        ("I also managed to deploy the new service before lunch!", "Turn 5: Sharing a win / celebration"),
        ("Thanks for the ideas, heading offline now.", "Turn 6: Casual sign-off")
    ]

    all_responses = []

    for user_text, turn_label in turns:
        print(f"\n--- [{turn_label}] ---")
        print(f"Employee: \"{user_text}\"")
        
        reply = get_buddybot_response(user_text, emp_id, history)
        print(f"BuddyBot: \"{reply}\"")
        
        # 1. Verify response is non-empty and conversational length
        assert len(reply) > 25, f"Response too short: '{reply}'"
        
        # 2. Verify strict absence of forbidden clichés
        reply_lower = reply.lower()
        for forbidden in FORBIDDEN_PHRASES:
            assert forbidden not in reply_lower, f"Forbidden phrase '{forbidden}' found in reply: {reply}"
            
        # 3. Verify no exact repetition with prior turns
        assert reply not in all_responses, f"Duplicate reply detected: {reply}"
        all_responses.append(reply)
        
        # Update history
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})
        save_chat_message(emp_id, "user", user_text)
        save_chat_message(emp_id, "buddybot", reply)

    # 4. Detailed turn assertions
    # Turn 2 must acknowledge meetings
    assert any(w in all_responses[1].lower() for w in ["meeting", "call", "screen", "calendar", "buffer", "fatigue"]), "Turn 2 missed meeting context!"
    # Turn 3 must answer the 'how' question directly
    assert any(w in all_responses[2].lower() for w in ["manager", "1-on-1", "outcome", "priority", "deliverable", "agenda"]), "Turn 3 failed to answer direct question on manager communication!"
    # Turn 4 must acknowledge break/wellness
    assert any(w in all_responses[3].lower() for w in ["monitor", "walk", "water", "shoulders", "break", "screen", "breathe"]), "Turn 4 failed to pivot to break activity!"
    # Turn 5 must celebrate
    assert any(w in all_responses[4].lower() for w in ["win", "congratulations", "milestone", "celebrat", "savor", "huge", "great"]), "Turn 5 failed to celebrate win!"

    print("\n" + "=" * 70)
    print("ALL 6 MULTI-TURN CONTEXT & VARIATION TESTS PASSED!")
    print(f"Verified {len(all_responses)} unique, non-cliché, context-aware responses.")
    print("=" * 70)

if __name__ == "__main__":
    test_enhanced_buddybot()
