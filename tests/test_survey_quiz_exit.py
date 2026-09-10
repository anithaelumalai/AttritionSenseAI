import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.database import init_database, get_connection
from utils.survey import save_survey, get_latest_survey
from utils.quiz import get_weekend_quiz_questions, save_quiz_score, get_employee_quiz_scores
from utils.exit_feedback import save_exit_feedback, get_exit_feedback_for_employee

class TestSurveyQuizExit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()

    def test_01_survey_unanswered_fields_remain_null_never_zero(self):
        """
        CRITICAL DATA INTEGRITY TEST:
        Unanswered optional survey questions MUST remain NULL (None) in database.
        They must NEVER be converted to 0.
        """
        test_emp = "TEST_SURVEY_EMP_1"
        payload = {
            "work_environment": 4,
            "team_collaboration": None,     # Unanswered
            "culture_alignment": 5,
            "growth_opportunities": None,   # Unanswered
            "tools_resources": 3,
            "suggestions": None             # Unanswered
        }
        res = save_survey(test_emp, payload, is_skipped=False)
        self.assertTrue(res)

        saved = get_latest_survey(test_emp)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["work_environment"], 4)
        self.assertEqual(saved["culture_alignment"], 5)
        self.assertEqual(saved["tools_resources"], 3)
        
        # Strictly verify None / NULL, NEVER 0!
        self.assertIsNone(saved["team_collaboration"], "Omitted question must be None/NULL, NOT 0!")
        self.assertNotEqual(saved["team_collaboration"], 0, "Omitted question must NOT be 0!")
        self.assertIsNone(saved["growth_opportunities"], "Omitted question must be None/NULL, NOT 0!")
        self.assertNotEqual(saved["growth_opportunities"], 0, "Omitted question must NOT be 0!")
        self.assertIsNone(saved["suggestions"], "Omitted text must be None/NULL!")
        self.assertEqual(saved["is_skipped"], 0)

    def test_02_survey_skip_records_skipped_flag(self):
        """Verify Skip Survey sets is_skipped=1 and leaves ratings NULL."""
        test_emp = "TEST_SURVEY_EMP_SKIP"
        res = save_survey(test_emp, {}, is_skipped=True)
        self.assertTrue(res)

        saved = get_latest_survey(test_emp)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["is_skipped"], 1)
        self.assertIsNone(saved["work_environment"])
        self.assertIsNone(saved["team_collaboration"])

    def test_03_weekend_quiz_structure_and_scoring(self):
        """Verify 10-question weekly quiz structure, clues, and score recording."""
        questions = get_weekend_quiz_questions()
        self.assertEqual(len(questions), 10, "Each week must contain 10 high-quality scenario questions")
        for q in questions:
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn("answer_index", q)
            self.assertIn("clue", q, "Each question must include a non-spoiler thinking clue")
            self.assertTrue(len(q["clue"]) > 10, "Clue must be substantive")
            self.assertIn("explanation", q)

        # Test score recording (both backwards-compatible and weekly formats)
        test_emp = "TEST_QUIZ_EMP_1"
        save_res = save_quiz_score(test_emp, score=8, total_questions=10)
        self.assertTrue(save_res)

        history = get_employee_quiz_scores(test_emp)
        self.assertTrue(len(history) >= 1)
        latest = history[0]
        self.assertEqual(latest["score"], 8)
        self.assertEqual(latest["total_questions"], 10)

    def test_04_exit_feedback_null_preservation(self):
        """
        CRITICAL DATA INTEGRITY TEST:
        Unanswered exit feedback fields MUST remain NULL (None), never 0.
        """
        test_emp = "TEST_EXIT_EMP_1"
        payload = {
            "primary_reason": "Career Opportunity & Professional Growth",
            "experience_rating": 4,
            "recommend_company": None,     # Unanswered
            "handover_status": None,       # Unanswered
            "detailed_feedback": "Thank you for the opportunity."
        }
        res = save_exit_feedback(test_emp, payload, is_skipped=False)
        self.assertTrue(res)

        saved = get_exit_feedback_for_employee(test_emp)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["experience_rating"], 4)
        self.assertIsNone(saved["recommend_company"], "Omitted rating must remain None/NULL, NOT 0!")
        self.assertNotEqual(saved["recommend_company"], 0, "Omitted rating must NOT be 0!")
        self.assertIsNone(saved["handover_status"])
        self.assertEqual(saved["is_skipped"], 0)

    def test_05_exit_feedback_skip(self):
        """Verify Skip Exit Feedback sets is_skipped=1."""
        test_emp = "TEST_EXIT_EMP_SKIP"
        res = save_exit_feedback(test_emp, {}, is_skipped=True)
        self.assertTrue(res)

        saved = get_exit_feedback_for_employee(test_emp)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["is_skipped"], 1)

if __name__ == "__main__":
    unittest.main()
