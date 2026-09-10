import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class TestGamesReplacement(unittest.TestCase):
    def setUp(self):
        games_file_path = os.path.join(PROJECT_ROOT, "views", "employee", "games_view.py")
        with open(games_file_path, "r", encoding="utf-8") as f:
            self.games_content = f.read()

    def test_01_old_games_completely_absent(self):
        """
        Verify the 3 old games:
        - Memory Match (or Memory Card Match)
        - Quick Tap Challenge
        - Breathing Circle (or Focus Breathing)
        are completely removed and do not appear anywhere in games_view.py.
        """
        old_game_terms = [
            "Memory Card Match",
            "Memory Match",
            "Quick Tap",
            "Focus Breathing",
            "Breathing Circle",
            "4-7-8 Focus Breathing",
            "Workplace Word Scramble",
            "Digital Zen Garden",
            "ColorFlow"
        ]
        for term in old_game_terms:
            self.assertNotIn(
                term.lower(),
                self.games_content.lower(),
                f"Old game term '{term}' was found in games_view.py!"
            )

    def test_02_new_mind_free_games_present(self):
        """
        Verify the 3 approved games:
        1. ZenCode – Coding Relaxation Puzzle
        2. Focus Flow
        3. Calm Puzzle Room
        are present in games_view.py.
        """
        self.assertIn("ZenCode", self.games_content)
        self.assertIn("Focus Flow", self.games_content)
        self.assertIn("Calm Puzzle Room", self.games_content)

    def test_03_games_do_not_import_or_affect_prediction(self):
        """
        Verify privacy and isolation:
        games_view.py must not import ML pipelines, prediction utilities,
        or write to prediction tables.
        """
        forbidden_imports = [
            "predict_employee_attrition",
            "save_prediction_record",
            "load_trained_model",
            "retention_alerts"
        ]
        for imp in forbidden_imports:
            self.assertNotIn(
                imp,
                self.games_content,
                f"Forbidden import '{imp}' detected in games_view.py!"
            )

if __name__ == "__main__":
    unittest.main()
