import unittest
import sys
import os

# Append the parent project directory into Python's system search paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import formulas
import config

class TestFloridaSyndicateFormulas(unittest.TestCase):

    def setUp(self):
        """Set up foundational parameters before each test runs."""
        config.STARTING_SCORE = 25000
        config.CURRENT_SEASON_CODE = "S26"
        config.SEASON_ADJ_COL = "H"

    def test_calculate_match_ladder_points_positive(self):
        """Test standard 2nd place win: 30,000 points with +5.0 Uma tier."""
        # ((30000 - 25000) / 1000) + 5.0 = 5.0 + 5.0 = +10.0
        result = formulas.calculate_match_ladder_points(30000, 5.0)
        self.assertEqual(result, 10.0)

    def test_calculate_match_ladder_points_negative_delta(self):
        """Test standard 4th place blowout: 15,000 points with -15.0 Uma tier."""
        # ((15000 - 25000) / 1000) - 15.0 = -10.0 - 15.0 = -25.0
        result = formulas.calculate_match_ladder_points(15000, -15.0)
        self.assertEqual(result, -25.0)

    def test_get_column_letter(self):
        """Ensure column integer indexing maps cleanly to Excel letters."""
        self.assertEqual(formulas.get_column_letter(1), "A")
        self.assertEqual(formulas.get_column_letter(6), "F")
        self.assertEqual(formulas.get_column_letter(26), "Z")
        self.assertEqual(formulas.get_column_letter(27), "AA")

    def test_format_season_code_readable(self):
        """Verify raw database seasonal keys match premium layout titles."""
        self.assertEqual(formulas.format_season_code_readable("E26"), "2026 - East Round")
        self.assertEqual(formulas.format_season_code_readable("S27"), "2027 - South Round")
        # Ensure fallbacks protect brief or broken strings gracefully
        self.assertEqual(formulas.format_season_code_readable("X"), "X")

    def test_build_initial_row_structure(self):
        """Verify the generated player initialization list contains expected formulas."""
        mock_headers = ["Rank", "Discord ID", "Lifetime Games", "Lifetime Net Points", "Lifetime Adjusted Points", "S26 Games Played", "S26 Net Points", "S26 Adjusted Points"]

        # Build a sample row profile for a user at Row 5 targeting Season S26
        generated_row = formulas.build_initial_row(5, "123456789", mock_headers, "S26")

        self.assertEqual(len(generated_row), 8)
        self.assertEqual(generated_row[1], "123456789")  # ID check
        self.assertIn("COUNTIF(Game_Logs!$C:$C", generated_row[2])  # Lifetime games check
        self.assertIn("Variables!$B$2", generated_row[4])  # Attendance check link variable
        self.assertIn("RANK(H5", generated_row[0])  # Rank maps relative to Column H (S26 Adj)

if __name__ == "__main__":
    unittest.main()
