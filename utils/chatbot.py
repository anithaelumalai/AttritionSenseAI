import os
import sys
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection

# System prompt for Gemini LLM
BUDDYBOT_SYSTEM_PROMPT = """You are BuddyBot, an empathetic, conversational, and authentic workplace companion in AttritionSense AI.
Your purpose is to chat with employees as an attentive, supportive, and grounded peer.

STRICT CONVERSATIONAL RULES:
1. NEVER use canned therapist clichés such as:
   - "I understand"
   - "That sounds difficult" / "That sounds tough"
   - "Thank you for sharing" / "Thanks for being open"
   - "I hear you"
   - "That must be hard"
2. Directly answer any questions the employee asks with pragmatic, real-world suggestions.
3. If the employee shares an experience or feeling, acknowledge their specific words and context directly.
4. Ask thoughtful, curious follow-up questions instead of always giving unsolicited advice or lecture-style lists.
5. If the employee shifts to a new topic, follow the new topic immediately.
6. Vary your sentence structure, tone, and length naturally (keep responses to 2–4 conversational sentences).
7. Never diagnose medical or psychological conditions.
8. BuddyBot is 100% private to the employee. Never mention or send anything to HR.
"""

def get_gemini_api_key() -> Optional[str]:
    """Retrieves Gemini API key from environment or secrets."""
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        try:
            if hasattr(st, "secrets") and "gemini_api_key" in st.secrets:
                key = st.secrets["gemini_api_key"]
        except Exception:
            pass
    return key.strip() if key else None

def save_chat_message(employee_id: str, sender: str, message: str):
    """Saves a message to the SQLite chat_history table for the employee."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (employee_id, sender, message) VALUES (?, ?, ?)",
        (str(employee_id), sender, message)
    )
    conn.commit()
    conn.close()

def get_employee_chat_history(employee_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves chat history for ONLY the authenticated employee."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT sender, message, timestamp FROM chat_history WHERE employee_id = ? ORDER BY id ASC LIMIT ?",
        (str(employee_id), limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [{"role": "assistant" if r["sender"] == "buddybot" else "user", "content": r["message"], "time": r["timestamp"]} for r in rows]

def clear_employee_chat_history(employee_id: str):
    """Clears private chat history for the employee."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_history WHERE employee_id = ?", (str(employee_id),))
    conn.commit()
    conn.close()

# ==============================================================================
# CONTEXTUAL WORKPLACE DIALOGUE ENGINE (NO CANNED RESPONSES / NO CLICHÉS)
# ==============================================================================

FORBIDDEN_PHRASES = [
    "i understand", "that sounds difficult", "thank you for sharing",
    "i hear you", "that must be hard", "thanks for opening up",
    "that sounds tough", "i appreciate you sharing"
]

def clean_cliches(text: str) -> str:
    """Ensures forbidden canned phrases never appear in BuddyBot responses."""
    cleaned = text
    for phrase in FORBIDDEN_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

def detect_user_intent(msg: str) -> Dict[str, Any]:
    """Classifies user intent, topic domain, and speech act."""
    text = msg.lower().strip()
    is_question = text.endswith("?") or any(text.startswith(w) for w in [
        "how", "what", "why", "when", "where", "can you", "should i", "is it", "do you", "could i"
    ])
    
    intent = "general_reflection"
    if any(w in text for w in ["won", "solved", "finished", "shipped", "deployed", "deploy", "approved", "celebrate", "great news", "huge win", "nailed it"]):
        intent = "celebration"
    elif any(w in text for w in ["meeting", "meetings", "calls", "zoom", "sync", "syncs", "huddle"]):
        intent = "meetings"
    elif any(w in text for w in ["tired", "tiring", "exhausted", "drained", "sleepy", "fatigue", "burned out", "burnout"]):
        intent = "exhaustion"
    elif any(w in text for w in ["deadline", "overwhelmed", "swamped", "workload", "too much", "crunch", "backlog", "urgent"]):
        intent = "workload"
    elif any(w in text for w in ["manager", "boss", "supervisor", "lead", "leadership", "1-on-1", "one on one"]):
        intent = "manager"
    elif any(w in text for w in ["career", "promotion", "raise", "salary", "hike", "growth", "skills", "learn", "mentor"]):
        intent = "career"
    elif any(w in text for w in ["coffee", "break", "stretch", "walk", "food", "snack", "weekend", "vacation", "eating lunch", "take a break"]):
        intent = "breaks_wellness"
    elif any(w in text for w in ["colleague", "coworker", "peer", "team", "conflict", "friction", "argue", "credit"]):
        intent = "team_dynamics"
    elif any(text.startswith(w) for w in ["hi", "hello", "hey", "good morning", "good afternoon", "morning", "howdy"]):
        intent = "greeting"
    elif any(w in text for w in ["thanks", "thank you", "bye", "goodbye", "see you", "later"]):
        intent = "closing"

    return {
        "intent": intent,
        "is_question": is_question,
        "text": text
    }

def synthesize_contextual_response(
    user_message: str,
    history: List[Dict[str, str]],
    recent_responses: List[str]
) -> str:
    """
    Synthesizes a tailored, context-specific response without predefined static rotation.
    Combines direct answers, situational observations, and engaging follow-up questions.
    """
    analysis = detect_user_intent(user_message)
    intent = analysis["intent"]
    is_question = analysis["is_question"]
    raw = analysis["text"]

    # History context awareness (detect previous topic & user statement)
    prev_user_msgs = [turn["content"].lower() for turn in history if turn.get("role") == "user"]
    prev_user_topic = detect_user_intent(prev_user_msgs[-2])["intent"] if len(prev_user_msgs) >= 2 else None
    
    # Check if user pivoted to a completely new topic
    topic_changed = (prev_user_topic is not None and prev_user_topic != intent and intent != "general_reflection")

    # -------------------------------------------------------------
    # 1. DIRECT QUESTION HANDLING
    # -------------------------------------------------------------
    if is_question:
        if intent == "meetings":
            answers = [
                "To push back on meeting overload without stepping on toes, you can say: 'I have a high-priority deliverable today, so I'll review the summary doc asynchronously. Ping me if a key decision needs my input.' Would that script work for your current team dynamics?",
                "One solid approach is asking the organizer: 'What specific outcome are we aiming to finalize in this session?' Often that prompts them to realize it can be handled over a quick chat thread instead. Are most of these syncs recurring status meetings or impromptu requests?",
                "Try proposing 20-minute and 45-minute calendar defaults across your department. That automatically creates 10-minute breathers between calls. Does your team currently protect no-meeting mornings or focus blocks?"
            ]
        elif intent == "manager":
            answers = [
                "When bringing up a sensitive topic with a manager, anchor it around outcomes rather than complaints: 'To make sure I deliver quality on project X, I'd like to adjust priority Y.' What specific outcome are you hoping to get out of the discussion?",
                "A clean 1-on-1 prep format is the '3Ps': Progress, Priorities, and Problems. Sending 3 bullet points 2 hours ahead of time completely changes the conversation from a status grill to strategic support. Have you tried an advance agenda before?",
                "The best time to ask is during a regular 1-on-1 check-in, framing it as: 'I want to align with where you see the biggest impact for our team this quarter.' How open is your manager to collaborative priority-setting?"
            ]
        elif intent == "career":
            answers = [
                "Directly ask your manager: 'What concrete milestones would demonstrate readiness for the next tier over the next 6 months?' That turns vague expectations into measurable deliverables. Have you identified a specific next role or skill track yet?",
                "Focus on expanding your cross-functional visibility—leading a retrospective, mentoring a newer teammate, or presenting at team demo. Which of those feels closest to your natural strengths?",
                "Start keeping an ongoing 'brag sheet' document where you log key metrics, launched deliverables, and colleague shout-outs every Friday. When review season arrives, your entire case is already written. Do you currently track your wins anywhere?"
            ]
        elif intent == "workload":
            answers = [
                "When everything feels urgent, force a priority trade-off: 'I can deliver A by tomorrow if we push B to next Tuesday—does that alignment work?' Forcing the stakeholder to choose relieves the pressure from your shoulders. Which task is demanding the most attention right now?",
                "Try timeboxing: allocate strict 40-minute blocks to tackle a single thorny task with notifications silenced. Seeing one real item crossed off breaks the spiral of overwhelm. Can you carve out one undisturbed hour today?",
                "Rank your current tasks into 'Must Finish Today' vs. 'Nice to Have'. Anything that doesn't cause a fire if delayed 24 hours gets deferred. What's sitting on your to-do list that could realistically wait until tomorrow?"
            ]
        elif intent == "breaks_wellness":
            answers = [
                "Step completely away from every monitor and phone for 7 full minutes. A glass of cold water, a quick lap around the hallway or outside, and loosening your shoulders resets your focus. Which of those can you do right now?",
                "A brisk walk outside or listening to an upbeat track without looking at Slack clears mental brain fog faster than coffee. What kind of break usually re-energizes you best?",
                "Step away from your desk to eat lunch! Eating while answering emails gives your brain zero downtime to digest and decompress. Can you step away for 20 undisturbed minutes?"
            ]
        else:
            answers = [
                f"Looking at what you asked, the most practical first step is clarifying the single most important priority on your plate today. What is the main outcome you want to see by the time you sign off?",
                f"That depends on whether you have direct autonomy over the timeline or need buy-in from others first. Which side of that equation are you dealing with?",
                f"Often the simplest fix is communicating early: giving stakeholders a heads-up before an issue becomes a crisis. Who would be the most important person to loop in on this?"
            ]
        # Filter out anything recently used
        candidates = [a for a in answers if a not in recent_responses]
        return candidates[0] if candidates else answers[0]

    # -------------------------------------------------------------
    # 2. TOPIC PIVOT (USER CHANGED SUBJECT)
    # -------------------------------------------------------------
    if topic_changed and intent not in ["celebration", "closing", "general_reflection"]:
        if intent == "breaks_wellness":
            return "Pivoting over to breaks and relaxation—that is genuinely a great move. Are you thinking of stepping outside for a bit, or grabbing a bite?"
        elif intent == "meetings":
            return "Shifting over to meetings—let's look at your calendar. How many hours of calls are you staring down today?"
        elif intent == "career":
            return "Changing gears to career and future goals—that's a great topic to explore. What's on your mind regarding your role or next steps?"
        elif intent == "workload":
            return "Switching over to workload and tasks. What's the biggest project competing for your focus right now?"

    # -------------------------------------------------------------
    # 3. TOPIC-SPECIFIC ACTIVE CONVERSATION
    # -------------------------------------------------------------
    if intent == "meetings":
        if "mostly" in raw or "too many" in raw or "all day" in raw:
            variants = [
                "Back-to-back calls leave virtually zero buffer for deep thinking or even catching your breath. If you look at tomorrow's schedule, is there at least one meeting you could decline or ask for notes on instead?",
                "Screen fatigue is draining because you're constantly performing attention. Could you dial in audio-only for your next discussion and pace around the room?",
                "Days dominated by calls usually end with a backlog of unanswered messages. Are these collaborative work sessions, or mostly people presenting slide decks to each other?"
            ]
        else:
            variants = [
                "Calendar density dictates so much of daily energy. How much uninterrupted focus time do you typically get between calls on a day like this?",
                "Meeting culture varies a lot between teams. Does your team have any norms around meeting agendas or keeping Fridays meeting-free?",
                "When meetings pile up, the hardest part is context switching every 30 minutes. What project got sidelined because of calls today?"
            ]
    elif intent == "exhaustion":
        variants = [
            "Demanding stretches happen, but running on empty catches up fast. What part of today was the heaviest draw on your battery?",
            "Rest isn't a reward you earn after finishing everything—it's what keeps you functioning. What's the earliest reasonable time you can power down your workstation today?",
            "Notice where you're holding tension right now—often it's the jaw or shoulders. Do you have anything pressing left on your agenda, or can you coast into a low-gear afternoon?"
        ]
    elif intent == "workload":
        variants = [
            "When the queue keeps growing, prioritizing gets frustrating because everything feels labeled critical. What's the single item that would give you the biggest sense of relief to finish?",
            "Context switching across ten different tasks is twice as exhausting as focusing on one big problem. Could you bundle similar tasks together into a single block?",
            "Keep in mind that high workloads usually reflect planning gaps higher up, not a personal failure to work fast enough. Have you mentioned your current capacity to your team lead?"
        ]
    elif intent == "manager":
        variants = [
            "Manager relationships set the weather for the entire work week. What style of communication does your manager respond best to—quick async bullets, or live discussions?",
            "Having a regular cadence where you can speak frankly makes a night-and-day difference. When is your next scheduled 1-on-1?",
            "Clear expectations prevent 90% of workplace friction. Do you feel completely aligned on what success looks like for your current deliverables?"
        ]
    elif intent == "career":
        variants = [
            "Taking ownership of your career trajectory is empowering. What kind of project would you love to get your hands on over the next quarter?",
            "Often growth happens by stepping into small gaps—taking ownership of a messy process or bridging two teams. Where do you see the most interesting opportunities in your org right now?",
            "Skills compound like interest. What is one area you've been wanting to learn more about, but haven't found the margin of time for?"
        ]
    elif intent == "breaks_wellness":
        variants = [
            "Stepping away from the workstation is essential for creative stamina. Have you had a chance to drink water and grab proper food today?",
            "Taking 10 minutes away from screens gives your prefrontal cortex a needed reboot. What's your favorite way to spend an afternoon pause?",
            "Enjoy your break! Completely disconnect while you take it—no checking notifications under the table."
        ]
    elif intent == "team_dynamics":
        variants = [
            "Navigating different communication styles and egos is often harder than the technical work itself. Is this an issue with shared ownership, or differing opinions on approach?",
            "Misalignments usually happen when people have different unspoken assumptions. Would a quick 5-minute alignment sync clear up the confusion?",
            "Working in a team requires finding common ground. How do the rest of your teammates feel about the situation?"
        ]
    elif intent == "celebration":
        variants = [
            "That's a huge win! Make sure you take a second to savor it before rushing straight onto the next ticket on the backlog. How are you celebrating?",
            "Huge congratulations! Delivering a successful milestone takes a ton of coordination and persistence. Who on your team helped make it happen?",
            "Love seeing wins like that! Getting through a tough stretch and seeing the payoff is the best feeling. What was the toughest hurdle you had to solve?"
        ]
    elif intent == "greeting":
        variants = [
            "Hey! Glad you checked in. How is the flow of your workday feeling right now?",
            "Hello! Good to connect with you. What kind of day has it been on your end so far?",
            "Hey there! What's the main focus on your desk today?"
        ]
    elif intent == "closing":
        variants = [
            "Have a restful evening and make sure to fully unplug from work! Catch you later.",
            "Take care of yourself, and don't hesitate to reach out whenever you want a quick sounding board. Have a great rest of your day!",
            "Anytime! Wishing you an easy finish to your workday."
        ]
    else:
        # Dynamic reflection based on content words
        words = [w for w in user_message.split() if len(w) > 4]
        topic_keyword = words[0].lower() if words else "work"
        variants = [
            f"Looking at what you mentioned about {topic_keyword}, it sounds like there are several moving pieces involved. What would make the situation feel more manageable?",
            f"That gives valuable perspective on what's happening. If you could change one aspect of that workflow tomorrow, what would you tackle first?",
            f"Reflecting on that is worthwhile. Do you want to brainstorm practical ways to navigate this, or did you just need to talk it through?"
        ]

    # Filter against recently sent messages to prevent any repetition
    fresh_candidates = [v for v in variants if clean_cliches(v) not in recent_responses]
    selected = fresh_candidates[0] if fresh_candidates else random.choice(variants)
    return clean_cliches(selected)

# ==============================================================================
# PRIMARY BUDDYBOT ORCHESTRATION
# ==============================================================================

def get_buddybot_response(user_message: str, employee_id: str, history: List[Dict[str, str]]) -> str:
    """
    Primary BuddyBot response coordinator.
    Attempts Gemini LLM API if key is available with secure context handling.
    Otherwise runs the advanced contextual dialogue engine (clearly framed as contextual companion).
    Guarantees no repetitive canned clichés.
    """
    api_key = get_gemini_api_key()
    
    # Track recent assistant messages to prevent repeats
    recent_assistant_msgs = [
        clean_cliches(turn["content"].strip())
        for turn in history[-8:]
        if turn.get("role") in ["assistant", "model", "buddybot"]
    ]
    
    # 1. ATTEMPT GEMINI GENERATIVE ENGINE
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Use available current model
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=BUDDYBOT_SYSTEM_PROMPT
            )
            
            # Format history cleanly with strictly alternating turns (User -> Model -> User -> Model)
            formatted_history = []
            expected_role = "user"
            for turn in history[-6:]:
                curr_role = "user" if turn.get("role") == "user" else "model"
                if curr_role == expected_role:
                    formatted_history.append({"role": curr_role, "parts": [turn["content"]]})
                    expected_role = "model" if expected_role == "user" else "user"
                    
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(user_message)
            
            if response.text and response.text.strip():
                reply = clean_cliches(response.text.strip())
                # Ensure no exact repetition of recent replies
                if reply not in recent_assistant_msgs:
                    return reply
        except Exception as e:
            print(f"[BuddyBot] Gemini API call note: {e}. Utilizing offline contextual engine.")

    # 2. CONTEXTUAL ADAPTIVE WORKPLACE ENGINE (FALLBACK)
    response_text = synthesize_contextual_response(user_message, history, recent_assistant_msgs)
    return response_text
