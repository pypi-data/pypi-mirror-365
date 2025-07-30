import unittest
from convert_time_to_text.convert_time_to_text import convert_time_to_text

class TestConvertTimeToText(unittest.TestCase):

    def test_oclock_double_zero(self):
        self.assertEqual(convert_time_to_text(5, 00), "five o' clock")

    def test_oclock_single_zero(self):
        self.assertEqual(convert_time_to_text(5, 0), "five o' clock")

    def test_one_minute_past(self):
        self.assertEqual(convert_time_to_text(5, 1), "one minute past five")

    def test_nine_minutes_past(self):
        self.assertEqual(convert_time_to_text(5, 9), "nine minutes past five")

    def test_ten_minutes_past(self):
        self.assertEqual(convert_time_to_text(5, 10), "ten minutes past five")

    def test_quarter_past(self):
        self.assertEqual(convert_time_to_text(5, 15), "quarter past five")

    def test_half_past(self):
        self.assertEqual(convert_time_to_text(5, 30), "half past five")

    def test_twenty_three_minutes_to_six(self):
        self.assertEqual(convert_time_to_text(5, 37), "twenty three minutes to six")

    def test_twenty_minutes_to_six(self):
        self.assertEqual(convert_time_to_text(5, 40), "twenty minutes to six")

    def test_quarter_to_six(self):
        self.assertEqual(convert_time_to_text(5, 45), "quarter to six")

    def test_thirteen_minutes_to_six(self):
        self.assertEqual(convert_time_to_text(5, 47), "thirteen minutes to six")

    def test_twenty_four_minutes_past_twelve(self):
        self.assertEqual(convert_time_to_text(12, 24), "twenty four minutes past twelve")

    def test_ten_minutes_to_twelve(self):
        self.assertEqual(convert_time_to_text(11, 50), "ten minutes to twelve")

    def test_ten_minutes_to_one(self):
        self.assertEqual(convert_time_to_text(12, 50), "ten minutes to one")

    def test_twenty_minutes_past_twelve(self):
        self.assertEqual(convert_time_to_text(12, 20), "twenty minutes past twelve")

    def test_invalid_hour(self):
        self.assertEqual(convert_time_to_text("x", 15), "Error : Please provide integer values.")

    def test_invalid_minute(self):
        self.assertEqual(convert_time_to_text(3, "y"), "Error : Please provide integer values.")

if __name__ == '__main__':
    unittest.main()