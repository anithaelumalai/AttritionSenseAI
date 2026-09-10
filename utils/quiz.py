import os
import sys
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import get_connection

WEEKEND_QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the scientifically recommended duration for the '20-20-20 rule' to prevent digital screen eye strain?",
        "options": [
            "Every 20 minutes, look at something 20 feet away for 20 seconds",
            "Every 20 hours, take a 20-minute nap in 20-degree weather",
            "Every 20 minutes, blink 20 times with eyes closed for 20 seconds",
            "Work 20 hours a week with 20-minute daily breaks"
        ],
        "answer_index": 0,
        "explanation": "The 20-20-20 rule advises looking at an object 20 feet away for at least 20 seconds every 20 minutes to relax optical muscles."
    },
    {
        "id": 2,
        "question": "In cognitive ergonomics, which practice most effectively prevents workplace cognitive fatigue during deep work?",
        "options": [
            "Multi-tasking across 4 different projects simultaneously",
            "Ultradian rhythm sprints: 60–90 min focused work followed by a 10 min disengaged pause",
            "Consuming caffeine every 30 minutes continuously",
            "Never leaving the desk during working hours"
        ],
        "answer_index": 1,
        "explanation": "Human ultradian rhythms cycle every 90 minutes. Taking a true cognitive disconnect break restores executive function and creativity."
    },
    {
        "id": 3,
        "question": "What does the physiological sigh (two quick nasal inhales followed by one long slow exhale) trigger in the autonomic nervous system?",
        "options": [
            "Rapid adrenaline secretion and fight-or-flight activation",
            "Immediate parasympathetic activation, slowing heart rate and lowering acute stress",
            "Hyperventilation and decreased blood oxygen",
            "Loss of short-term focus"
        ],
        "answer_index": 1,
        "explanation": "Two rapid inhales re-inflate collapsed pulmonary alveoli, and the prolonged exhale stimulates the vagus nerve to swiftly downregulate stress."
    },
    {
        "id": 4,
        "question": "When setting healthy workplace psychological boundaries, what is the best strategy when disconnected on weekends?",
        "options": [
            "Keep work notifications vibrating on your bedside table",
            "Turn off work notifications and set an asynchronous response expectation",
            "Apologize profusely whenever you don't reply within 5 minutes on Saturday",
            "Secretly complete entire quarterly backlogs during weekend nights"
        ],
        "answer_index": 1,
        "explanation": "Establishing clear asynchronous expectations allows authentic cognitive recovery, which drastically reduces long-term burnout."
    },
    {
        "id": 5,
        "question": "Which workplace practice has the highest documented correlation with sustained team psychological safety?",
        "options": [
            "Penalizing failed experiments immediately",
            "Treating mistakes as blameless learning opportunities and encouraging open inquiries",
            "Mandatory daily 3-hour meetings",
            "Rank-and-yank monthly performance reviews"
        ],
        "answer_index": 1,
        "explanation": "Amy Edmondson's research proves psychological safety flourishes when failure is treated as collaborative learning rather than culpability."
    }
]

def get_weekend_quiz_questions() -> List[Dict[str, Any]]:
    """Returns the weekend mindfulness & workplace trivia question set."""
    return WEEKEND_QUIZ_QUESTIONS

def save_quiz_score(
    employee_id: str,
    score: int,
    total_questions: int,
    category: str = "Mindfulness & Workplace"
) -> bool:
    """
    Saves weekend quiz completion score.
    
    PRIVACY GUARANTEE:
    This score is strictly personal and private to the employee.
    It is NEVER shared with HR and NEVER influences AI attrition risk or growth status.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO quiz_scores (
            employee_id, score, total_questions, category, quiz_date
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        str(employee_id),
        int(score),
        int(total_questions),
        category,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return True

def get_employee_quiz_scores(employee_id: str) -> List[Dict[str, Any]]:
    """Returns quiz history for the authenticated employee only."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM quiz_scores 
        WHERE employee_id = ? 
        ORDER BY quiz_date DESC
    """, (str(employee_id),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
