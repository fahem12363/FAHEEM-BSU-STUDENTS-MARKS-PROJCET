"""Small automated tests for the Student Marks Data Processor."""

import tempfile
import unittest
from pathlib import Path

from student_data_processor import classification_from_average, process_file


class ProcessorTests(unittest.TestCase):
    def test_classification_boundaries(self):
        self.assertEqual(classification_from_average(70), "First")
        self.assertEqual(classification_from_average(60), "2:1")
        self.assertEqual(classification_from_average(50), "2:2")
        self.assertEqual(classification_from_average(40), "Third")
        self.assertEqual(classification_from_average(39.99), "Fail")

    def test_invalid_row_is_skipped_and_reported(self):
        csv_text = (
            "student_id,student_name,assessment1,assessment2,assessment3\n"
            "S001,Valid Student,70,60,50\n"
            "S002,Invalid Student,110,60,50\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.csv"
            path.write_text(csv_text, encoding="utf-8")
            rows, warnings = process_file(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["average"], "60.00")
        self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
