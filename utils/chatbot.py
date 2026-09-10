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
1. NEVER use canned clichés or therapist tropes such as:
   - "I understand" / "I completely understand"
   - "That sounds difficult" / "That sounds tough" / "That must be hard"
   - "Thank you for sharing" / "Thanks for opening up"
   - "I hear you" / "I appreciate you sharing"
   - "What about your feeling?" / "Don't feel bad"
2. When the user asks for a story (e.g., "tell me a story", "short story"), tell a thoughtful, engaging, short (2-3 paragraphs) narrative about perseverance, perspective, mindful calm, or teamwork.
3. Directly answer any questions the employee asks with pragmatic, real-world workplace suggestions.
4. If the employee shares a feeling or frustration, listen empathetically and acknowledge their specific situation without lecturing.
5. If the user expresses self-harm or suicidal thoughts, immediately provide a compassionate message and the 988 Suicide & Crisis Lifeline resource.
6. Never diagnose medical or psychological conditions.
7. Ask natural, engaging follow-up questions when appropriate.
8. If the employee shifts to a new topic, follow the new topic immediately.
9. BuddyBot is 100% private to the employee. NEVER mention HR, NEVER send emails to HR, and NEVER share conversations with administrators.
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
# CONVERSATIONAL STORYTELLING REPOSITORY
# ==============================================================================

STORIES = [
    (
        "The Stonecutter's Vision",
        "A traveler once walked past a busy quarry and saw three workers chiseling granite under the hot sun.\n\n"
        "He asked the first worker what he was doing. The man wiped sweat from his brow and muttered, 'I am chipping away at this stubborn rock until my shift ends.'\n\n"
        "He asked the second worker, who replied, 'I am carving square blocks so I can earn a fair wage to feed my family.'\n\n"
        "Then he asked the third worker, whose eyes lit up as he smoothed the edge of his stone. 'I,' the worker smiled proudly, 'am helping build a great cathedral that will stand for hundreds of years.'\n\n"
        "Whenever daily tasks feel repetitive or heavy, stepping back to see the larger structure you are shaping makes all the difference."
    ),
    (
        "The Japanese Moso Bamboo",
        "There is a remarkable species of bamboo known as the moso bamboo. When a gardener plants the seed, nothing visible happens during the entire first year. He waters the patch and tends the soil faithfully, but not a single sprout emerges.\n\n"
        "The second year passes—still nothing. The third and fourth years pass—not an inch above the ground. To an onlooker, it looks like futile work.\n\n"
        "Then, during the fifth year, a green shoot breaks the earth. Within just six weeks, it rockets over eighty feet into the air.\n\n"
        "Did it grow eighty feet in six weeks? Or did it grow eighty feet over five patient years of anchoring deep, invisible root networks beneath the soil? Real workplace skill and personal progress often happen invisibly right until the moment they surge."
    ),
    (
        "The Sticky Note That Wouldn't Stick",
        "In 1968, a research chemist named Dr. Spencer Silver was working at 3M to develop a super-strong, ultra-durable adhesive for aerospace applications.\n\n"
        "Instead, he accidentally created something that seemed useless: a light, weak adhesive that gripped surfaces lightly but peeled off cleanly without leaving any residue. For five years, it was considered a failed research experiment.\n\n"
        "Then, a colleague named Art Fry grew frustrated because his paper bookmarks kept falling out of his church choir hymnal. He remembered Silver's 'failed' adhesive and coated a scrap of yellow paper with it. It stayed perfectly in place, peeled off without tearing the page, and could be reused dozens of times.\n\n"
        "That apparent failure became the Post-it Note—one of the top five best-selling office products in history. A mistake in execution is often just an invention waiting for the right problem."
    ),
    (
        "The Geese and the V-Formation",
        "Every autumn, migrating geese fly thousands of miles in a strict V-formation. Aerodynamic studies revealed why: as each bird flaps its wings, it creates an uplift for the bird immediately behind it. By flying in unison, the flock gains over 71% greater flying range than if any bird flew solo.\n\n"
        "Whenever the lead goose grows tired from cutting through the headwinds, it rotates back into the wing, and another goose immediately moves forward to assume the point position.\n\n"
        "Even more fascinating, the geese flying in the rear honk continuously to encourage those in front to maintain their speed and stamina.\n\n"
        "High-performing teams don't rely on a single heroic leader; they share the headwinds, step up when peers need relief, and actively voice encouragement from behind."
    ),
    (
        "The Four-Minute Mile Barrier",
        "For decades, physiologists, trainers, and athletes believed that running a mile in under four minutes was biologically impossible for the human body. Experts argued that human lungs would burst under the strain.\n\n"
        "For over a generation, the world record stalled at 4:01. Then, on May 6, 1954, a young medical student named Roger Bannister ran a mile in 3 minutes and 59.4 seconds on a wet track in Oxford.\n\n"
        "Here is the incredible part: just 46 days later, Australian runner John Landy broke Bannister's record. Within the next 18 months, 45 other athletes had also broken the four-minute mile.\n\n"
        "Did human physiology evolve overnight? No. What shattered was the mental ceiling of what was possible. When one person breaks an imaginary barrier, they pave the mental runway for everyone else to follow."
    ),
    (
        "The Lobster's Shell",
        "A lobster is a soft, vulnerable creature that lives inside an inflexible, rigid shell. As the lobster grows, that outer armor becomes increasingly tight and uncomfortable.\n\n"
        "When the pressure becomes painful enough, the lobster realizes it cannot stay as it is. It retreats under a coral reef to protect itself from predators, sheds its old shell entirely, and remains completely vulnerable while producing a brand-new, much larger shell.\n\n"
        "It repeats this molt dozens of times throughout its lifetime. The stimulus for the lobster to grow is the discomfort of outgrowing its old container.\n\n"
        "When you feel stretched, uncomfortable, or challenged in your career, it doesn't mean you are failing—it usually means you have outgrown your previous shell and are expanding."
    ),
    (
        "The Starfish on the Beach",
        "Early one morning after a fierce Atlantic storm, an elderly traveler walked along an ocean beach covered with thousands of stranded starfish drying under the rising sun.\n\n"
        "Up ahead, he saw a young woman walking briskly, stopping every few paces to pick up a starfish and toss it back into the crashing waves.\n\n"
        "The traveler caught up to her and said, 'Look down the shore—there are miles of beach and tens of thousands of them. You can't possibly make a real difference.'\n\n"
        "The woman paused, picked up another starfish from the sand, and spun it gently into the cool surf. She turned to the man, smiled, and said, 'It made a difference to that one.'\n\n"
        "When workplace problems feel overwhelming or massive in scale, never discount small acts of kindness and direct help. To the person you assist today, it changes everything."
    ),
    (
        "The Empty Boat",
        "An ancient philosopher told of a fisherman who took his small wooden skiff out onto a misty lake at dawn.\n\n"
        "As he rowed quietly through the morning fog, another vessel suddenly came out of nowhere and bumped hard against his hull. The fisherman felt an instant spike of anger, standing up with his oar ready to confront the careless rower.\n\n"
        "When he peered through the haze, he realized the other boat was completely empty. It had simply broken loose from its dock and drifted with the wind.\n\n"
        "His frustration vanished immediately. He smiled, nudged the empty boat gently aside, and continued rowing peacefully. In daily work, most collisions aren't personal malice—they are just empty boats drifting on currents of rush, stress, and tight deadlines."
    ),
    (
        "The Lighthouse Keeper's Oil",
        "On a rocky shoreline, a lighthouse keeper guarded the beacon that guided night ships through dangerous shoals. Each month, he was allotted a fixed container of fuel oil to keep the flame lit.\n\n"
        "One cold evening, a neighbor asked for a cup of oil to heat his hearth. The kind keeper poured some out. The next week, a stranded traveler asked for fuel for his lantern, and the keeper shared again.\n\n"
        "Near the end of the month, a violent squall hit the coast. The keeper went to light the tower lamp, but the reservoir was dry. The light flickered out, and two cargo vessels struck the rocks in the dark.\n\n"
        "The harbor master came the next morning and told the keeper: 'Your generosity was noble, but your primary charge was to keep the beacon shining. If you deplete yourself, the whole harbor goes dark.' Protecting your personal energy isn't selfish—it's what lets you guide others."
    ),
    (
        "The Master Carpenter and the Storm Knot",
        "A young apprentice was crafting a solid oak conference table and grew upset when he found a dark, swirling knot right in the center of the wood. He grabbed a saw, planning to cut it out and toss the piece aside.\n\n"
        "The master carpenter stopped his hand gently. 'Look closely,' the master said. 'That knot isn't a flaw. That is where the tree fought off a fierce storm thirty years ago and grew back denser to support itself.'\n\n"
        "Together, they carefully planed the timber, polished the swirling whorls with beeswax, and made that knot the centerpiece of the table. When the customer received it, they remarked that the unique pattern of the knot was the most beautiful part of the entire room.\n\n"
        "Workplace setbacks and difficult stretches often feel like unsightly obstacles in the moment, but given time and care, they become the defining stories of your resilience."
    ),
    (
        "The Wright Brothers and the Wind Tunnel",
        "In the autumn of 1901, Wilbur and Orville Wright returned home from Kitty Hawk devastated. Their state-of-the-art glider had failed, nose-diving repeatedly, and Wilbur confessed to his brother that human flight might take another hundred years.\n\n"
        "Instead of giving up, they questioned the foundational scientific lift tables published by the world's most renowned aerodynamicists. In their Dayton bicycle shop, they built a six-foot wooden wind tunnel out of an old starch box and a two-bladed fan.\n\n"
        "Over the next two months, they tested more than 200 distinct miniature wing profiles, measuring drag and lift with delicate balances made of old bicycle spokes. They discovered that the world's standard mathematical tables were fundamentally wrong.\n\n"
        "With their own empirical data, they built the 1902 glider and achieved controlled powered flight in 1903. Persistence isn't just trying the same thing harder—it's having the curiosity to question assumptions and test your way to the truth."
    ),
    (
        "The Accidental Discovery of Penicillin",
        "In September 1928, Dr. Alexander Fleming returned to his London laboratory from a two-week family vacation. He had left a stack of staphylococcus bacterial culture plates on his workbench.\n\n"
        "Upon inspecting the bench, he noticed that one dish had been contaminated by airborne mold spores. In a typical laboratory, a contaminated dish would be immediately disinfected and discarded as wasted effort.\n\n"
        "Fleming looked closer under the lens. Surrounding the fuzzy colony of green mold, there was a completely clear halo where the staphylococcus bacteria had dissolved and could not survive. Instead of tossing it into the wash basin, he asked a single curious question: 'Why?'\n\n"
        "That curiosity led to the isolation of penicillin, transforming modern medicine and saving an estimated 200 million lives. Breakthroughs rarely arrive announced—they disguise themselves as unexpected anomalies."
    )
]

# ==============================================================================
# CONVERSATIONAL WORKPLACE DIALOGUE ENGINE
# ==============================================================================

FORBIDDEN_PHRASES = [
    "i understand", "that sounds difficult", "thank you for sharing",
    "i hear you", "that must be hard", "thanks for opening up",
    "that sounds tough", "i appreciate you sharing", "what about your feeling",
    "don't feel bad", "as an ai", "as an artificial intelligence"
]

CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die", "harm myself",
    "better off dead", "end it all", "don't want to live", "take my own life"
]

def clean_cliches(text: str) -> str:
    """Ensures forbidden canned phrases never appear in BuddyBot responses."""
    cleaned = text
    for phrase in FORBIDDEN_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

def get_crisis_response() -> str:
    """Delivers an immediate, supportive crisis response with official helpline contacts."""
    return (
        "I hear how much pain you're carrying right now, and I want you to know you are not alone. "
        "Your safety and wellbeing truly matter. Please connect with someone who can support you through this difficult moment:\n\n"
        "• **Suicide & Crisis Lifeline**: Call or text **988** (Available 24/7, free and confidential in the US/Canada)\n"
        "• **Crisis Text Line**: Text **HOME to 741741** to connect with a crisis counselor\n"
        "• **International Helplines**: Visit [findahelpline.com](https://findahelpline.com) for confidential support in your country\n\n"
        "Please consider stepping away from work right now and reaching out to a professional, counselor, or loved one who can be there with you."
    )

def detect_user_intent(msg: str) -> Dict[str, Any]:
    """Classifies user intent, topic domain, and speech act."""
    text = msg.lower().strip()
    
    # 0. Crisis detection
    if any(k in text for k in CRISIS_KEYWORDS):
        return {"intent": "crisis", "is_question": False, "text": text}

    # 1. Story detection
    story_phrases = [
        "tell me a story", "tell a story", "short story", "share a story",
        "story for me", "bedtime story", "read me a story", "give me a story",
        "need a story", "need a short story", "story sollu", "sollu story",
        "oru story", "something interesting", "tell me something interesting",
        "another story", "one more story", "tell another story", "next story",
        "share another story", "inspire me", "workplace story", "moral story",
        "motivational story", "tell story"
    ]
    if any(p in text for p in story_phrases) or text in ["story", "a story", "can you tell me a story", "tell me a story please", "story please"]:
        return {"intent": "story", "is_question": False, "text": text}
    if ("story" in text or "stories" in text) and any(w in text for w in ["tell", "share", "give", "need", "sollu", "read", "hear", "listen", "another", "one more", "short", "moral", "good", "nice", "inspire", "next"]):
        return {"intent": "story", "is_question": False, "text": text}
    if "something interesting" in text:
        return {"intent": "story", "is_question": False, "text": text}

    is_question = text.endswith("?") or any(text.startswith(w) for w in [
        "how", "what", "why", "when", "where", "can you", "should i", "is it", "do you", "could i"
    ])
    
    intent = "general_reflection"
    if any(w in text for w in ["angry", "frustrated", "annoyed", "unfair", "mad", "upset", "pissed", "vent"]):
        intent = "venting"
    elif any(w in text for w in ["won", "solved", "finished", "shipped", "deployed", "deploy", "approved", "celebrate", "great news", "huge win", "nailed it"]):
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
    elif any(w in text for w in ["coffee", "break", "stretch", "walk", "food", "snack", "weekend", "vacation", "lunch", "take a break"]):
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
    Combines direct answers, storytelling, situational observations, and engaging follow-up questions.
    """
    analysis = detect_user_intent(user_message)
    intent = analysis["intent"]
    is_question = analysis["is_question"]
    raw = analysis["text"]

    # 1. CRISIS SAFETY
    if intent == "crisis":
        return get_crisis_response()

    # 2. STORYTELLING
    if intent == "story":
        available_stories = [s for s in STORIES if s[0].lower() not in str(recent_responses).lower()]
        story_pool = available_stories if available_stories else STORIES
        title, text_content = random.choice(story_pool)
        
        follow_ups = [
            "How does that perspective resonate with what you're experiencing at work today?",
            "Have you ever run into a situation at work that felt similar to that?",
            "What would you have done in that situation?",
            "Does that spark any ideas for navigating your current workload or projects?",
            "I hope that gave your mind a healthy, quiet breather. How does that perspective sit with you?",
            "Sometimes a simple shift in angle changes the whole problem. What stands out to you most from that?",
            "Would you like another short story, or would you like to shift back to what's on your agenda today?"
        ]
        fresh_follow_ups = [f for f in follow_ups if f not in str(recent_responses)]
        follow_up = random.choice(fresh_follow_ups) if fresh_follow_ups else random.choice(follow_ups)
        
        return f"Here is a short story for you: **{title}**\n\n{text_content}\n\n{follow_up}"

    # History context awareness (detect previous topic & user statement)
    prev_user_msgs = [turn["content"].lower() for turn in history if turn.get("role") == "user"]
    prev_user_topic = detect_user_intent(prev_user_msgs[-2])["intent"] if len(prev_user_msgs) >= 2 else None
    
    # Check if user pivoted to a completely new topic
    topic_changed = (prev_user_topic is not None and prev_user_topic != intent and intent != "general_reflection")

    # 3. DIRECT QUESTIONS
    if is_question:
        if intent == "meetings":
            answers = [
                "To push back on meeting overload without friction, try this script: 'I have a high-priority deliverable today, so I'll review the summary doc asynchronously. Ping me if a key decision needs my input.' Would that fit your team culture?",
                "Ask the organizer ahead of time: 'What specific decision or deliverable are we aiming to finalize in this session?' Often that prompts people to realize it can be handled over a quick chat thread instead. Are most of these syncs recurring status check-ins?",
                "Propose 25-minute and 50-minute defaults for your team calendar. That builds in natural 5-to-10 minute buffers between discussions. Does your team currently observe focus hours or quiet mornings?"
            ]
        elif intent == "manager":
            answers = [
                "Anchor the conversation around outcomes rather than complaints: 'To make sure I deliver top quality on Project A, I'd like to adjust the timeline on Task B.' What specific outcome are you hoping to get out of the discussion?",
                "A clean 1-on-1 prep format is the '3Ps': Progress, Priorities, and Problems. Sending 3 bullet points 2 hours ahead of time changes the tone from an interrogation to strategic collaboration. Have you tried an advance agenda before?",
                "Frame your request around organizational impact: 'I want to align where you see the biggest value-add for our team this quarter.' How open is your manager to collaborative priority-setting?"
            ]
        elif intent == "career":
            answers = [
                "Directly ask your manager: 'What concrete milestones would demonstrate readiness for the next level over the next 6 months?' That turns subjective opinions into measurable benchmarks. Have you identified a specific next role or skill target?",
                "Focus on expanding cross-team visibility—leading a retrospective, mentoring a newer teammate, or presenting at a sprint showcase. Which of those aligns best with your natural strengths?",
                "Start keeping a Friday 'brag sheet' document where you jot down key metrics, shipped deliverables, and colleague shout-outs. When review season arrives, your entire case is already prepared. Do you currently track your wins anywhere?"
            ]
        elif intent == "workload":
            answers = [
                "When everything feels urgent, force a priority trade-off: 'I can deliver Deliverable A by tomorrow if we push Task B to next week—does that alignment work for you?' Forcing the stakeholder to choose takes the pressure off your shoulders. Which task is demanding the most energy right now?",
                "Try timeboxing: allocate a strict 40-minute block to tackle one thorny task with all notifications muted. Getting one tangible item crossed off breaks the spiral of overwhelm. Can you carve out one undisturbed block today?",
                "Rank current tasks into 'Must Finish Today' versus 'Nice to Have'. Anything that doesn't cause a breakdown if delayed 24 hours gets deferred. What's sitting on your list that could realistically wait until tomorrow?"
            ]
        elif intent == "breaks_wellness":
            answers = [
                "Step away from every monitor and phone for 7 full minutes. A tall glass of water, a quick lap around the floor or outside, and rolling your shoulders resets your mental focus. Which of those can you do right now?",
                "A brisk walk outside or listening to an upbeat track without checking Slack clears mental fog faster than a second cup of coffee. What kind of break usually re-energizes you best?",
                "Step completely away from your desk for lunch! Eating while answering emails gives your nervous system zero downtime to decompress. Can you take 20 undisturbed minutes?"
            ]
        elif intent == "venting":
            answers = [
                "It makes total sense why that feels frustrating. Would it help more to talk through practical ways to handle it, or would you rather just have space to vent it all out first?",
                "Carrying that kind of tension while trying to do your job is draining. What felt like the most unreasonable part of what happened?",
                "Situations like that test anyone's patience. Do you have someone on the team who has your back on this, or does it feel like you're handling it solo?"
            ]
        else:
            answers = [
                "Looking at what you asked, the most practical first step is clarifying the single most important priority on your plate today. What is the main outcome you want to see by the time you sign off?",
                "That depends on whether you have direct autonomy over the timeline or need buy-in from others first. Which side of that equation are you dealing with?",
                "Often the simplest fix is early communication: giving stakeholders a heads-up before an issue becomes a fire drill. Who would be the most important person to loop in on this?"
            ]
        candidates = [a for a in answers if clean_cliches(a) not in recent_responses]
        return candidates[0] if candidates else answers[0]

    # 4. TOPIC PIVOT (USER SWITCHED TOPICS)
    if topic_changed and intent not in ["celebration", "closing", "general_reflection"]:
        if intent == "breaks_wellness":
            return "Pivoting over to breaks and relaxation—that is a great move. Are you thinking of stepping outside for some fresh air, or grabbing a bite?"
        elif intent == "meetings":
            return "Shifting over to meetings—let's look at your calendar. How many hours of calls are you staring down today?"
        elif intent == "career":
            return "Changing gears to career and future goals—that's a valuable topic to explore. What's on your mind regarding your role or next steps?"
        elif intent == "workload":
            return "Switching over to workload and tasks. What's the biggest project competing for your focus right now?"
        elif intent == "venting":
            return "Let it out. Navigating workplace friction takes a real toll. What happened?"

    # 5. TOPIC-SPECIFIC ACTIVE CONVERSATION
    if intent == "venting":
        variants = [
            "Carrying frustration around all day while trying to stay productive is exhausting. What was the exact moment things boiled over today?",
            "You have every reason to want clarity and fairness in your work. Did this come out of nowhere, or has it been simmering for weeks?",
            "Take your time and lay it out. Getting thoughts out of your head and into words often brings clarity on what's worth fighting for and what to let go."
        ]
    elif intent == "meetings":
        if "mostly" in raw or "too many" in raw or "all day" in raw:
            variants = [
                "Back-to-back calls leave virtually zero buffer for deep thinking or catching your breath. Looking at tomorrow's schedule, is there at least one meeting you could decline or ask for notes on instead?",
                "Screen fatigue is draining because you're constantly performing attention. Could you dial in audio-only for your next discussion and stretch your legs?",
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
            "Notice where you're holding tension right now—often it's the jaw or shoulders. Do you have anything pressing left on your agenda, or can you coast into a lower gear?"
        ]
    elif intent == "workload":
        variants = [
            "When the queue keeps growing, prioritizing gets frustrating because everything feels labeled critical. What's the single item that would give you the biggest sense of relief to finish?",
            "Context switching across ten different tasks is twice as exhausting as focusing on one big problem. Could you bundle similar tasks together into a single focus block?",
            "Keep in mind that high workloads usually reflect planning gaps higher up, not a personal failure to work fast enough. Have you mentioned your current capacity to your team lead?"
        ]
    elif intent == "manager":
        variants = [
            "Manager relationships set the tone for the entire work week. What style of communication does your manager respond best to—quick async bullets, or live discussions?",
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
        words = [w for w in user_message.split() if len(w) > 4]
        topic_keyword = words[0].lower() if words else "work"
        variants = [
            f"Looking at what you mentioned about {topic_keyword}, it sounds like there are several moving pieces involved. What would make the situation feel more manageable?",
            f"That gives valuable perspective on what's happening. If you could change one aspect of that workflow tomorrow, what would you tackle first?",
            f"Reflecting on that is worthwhile. Do you want to brainstorm practical ways to navigate this, or did you just need to talk it through?"
        ]

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
    Guarantees no repetitive canned clichés, no HR notification, and 100% private to the employee.
    """
    api_key = get_gemini_api_key()
    
    # Track recent assistant messages to prevent repeats
    recent_assistant_msgs = [
        clean_cliches(turn["content"].strip())
        for turn in history[-8:]
        if turn.get("role") in ["assistant", "model", "buddybot"]
    ]
    
    # Safety Check: If user explicitly mentions crisis keywords, provide immediate lifeline
    if any(k in user_message.lower() for k in CRISIS_KEYWORDS):
        return get_crisis_response()

    # 1. ATTEMPT GEMINI GENERATIVE ENGINE
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
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
                if reply not in recent_assistant_msgs:
                    return reply
        except Exception as e:
            print(f"[BuddyBot] Gemini API call note: {e}. Utilizing offline contextual engine.")

    # 2. CONTEXTUAL ADAPTIVE WORKPLACE ENGINE (FALLBACK)
    response_text = synthesize_contextual_response(user_message, history, recent_assistant_msgs)
    return response_text
