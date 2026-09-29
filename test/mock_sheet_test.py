import unittest
import sys
import os

# Append the parent project directory into Python's system search paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import formulas
import services

class TestGoogleSheetsIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a safe standalone scratchpad spreadsheet for integration testing."""
        print("\nConnecting to Google Cloud... provisioning temporary test asset...")
        try:
            # Create a completely fresh temp file in your Google Drive
            cls.test_spreadsheet = config.CLIENT.create("TEMP_FML_TEST_LEDGER")
            cls.log_sheet = cls.test_spreadsheet.get_worksheet(0)
            cls.log_sheet.update_title("Game_Logs")

            # Setup mandatory initial tracking headers matching your schema layout
            cls.log_sheet.append_row([
                "Timestamp", "Game_ID",
                "Player_1_ID", "P1_Raw", "P1_Change",
                "Player_2_ID", "P2_Raw", "P2_Change",
                "Player_3_ID", "P3_Raw", "P3_Change",
                "Player_4_ID", "P4_Raw", "P4_Change",
                "Season_Code"
            ])

            cls.leaderboard_sheet = cls.test_spreadsheet.add_worksheet(title="Leaderboard", rows="100", cols="20")
            cls.leaderboard_sheet.append_row(["Rank", "Discord ID", "Lifetime Games", "Lifetime Net Points", "Lifetime Adjusted Points"])

            cls.var_sheet = cls.test_spreadsheet.add_worksheet(title="Variables", rows="10", cols="5")
            cls.var_sheet.append_row(["Variable Name", "Value"])
            cls.var_sheet.append_row(["Attendance Bonus", "0.5"])

            # Temporarily redirect live app configs to target this scratchpad
            cls.original_logs = config.SHEET_LOGS
            cls.original_leaderboard = config.SHEET_LEADERBOARD

            config.SHEET_LOGS = cls.log_sheet
            config.SHEET_LEADERBOARD = cls.leaderboard_sheet

        except Exception as e:
            raise unittest.SkipTest(f"Google API Connection Refused: {e}. Check json key configuration files.")

    def test_schema_auto_expansion(self):
        """Verify that logging a new season triggers column appending on the spreadsheet."""
        headers_before = config.SHEET_LEADERBOARD.row_values(1)
        self.assertEqual(len(headers_before), 5) # Rank, ID, Games, Net, Adj

        # Fire our automatic macro database expander targeting a test season tag
        formulas.maintain_database_schema("T99")

        headers_after = config.SHEET_LEADERBOARD.row_values(1)
        self.assertEqual(len(headers_after), 8) # Expanded with 3 new columns
        self.assertEqual(headers_after[5], "T99 Games Played")
        self.assertEqual(headers_after[7], "T99 Adjusted Points")

    def test_register_new_player_row_injection(self):
        """Ensure unlisted players are written with active formulas into sheets."""
        formulas.register_new_player_if_needed("999888777", "T99")

        all_rows = config.SHEET_LEADERBOARD.get_all_values()
        self.assertEqual(len(all_rows), 2) # Header row + 1 player row
        self.assertEqual(all_rows[1][1], "999888777") # Verifies stored ID position

    @classmethod
    def tearDownClass(cls):
        """Clean up Drive storage by completely deleting the temp spreadsheet file."""
        print("\nCleaning ledger footprint... deleting temporary test assets from Google Drive...")
        # Restore configuration variables back to production paths
        config.SHEET_LOGS = cls.original_logs
        config.SHEET_LEADERBOARD = cls.original_leaderboard

        # Permanently purge the temp spreadsheet from your account
        config.CLIENT.del_spreadsheet(cls.test_spreadsheet.id)

if __name__ == "__main__":
    unittest.main()
