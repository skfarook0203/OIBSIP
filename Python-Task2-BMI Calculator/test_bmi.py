"""
OASIS INFOBYTE Python Programming Internship
Task 2: BMI Calculator (Advanced Version)
Automated Test Suite: test_bmi.py

Tests mathematical formulas, boundary categories, input validation, and SQLite CRUD operations.
"""

import os
import unittest
import sqlite3
from bmi_calculator import (
    calculate_bmi,
    classify_bmi,
    calculate_healthy_weight_range,
    validate_user_inputs,
)
from database import DatabaseManager


class TestBMICalculator(unittest.TestCase):
    """Unit tests for the core calculation and classification functions."""

    def test_bmi_formula_standard(self):
        """Tests standard BMI calculation: weight / height^2."""
        # 70 kg, 1.75 m -> 70 / 3.0625 = 22.8571... -> 22.86
        self.assertEqual(calculate_bmi(70.0, 1.75), 22.86)
        # 80 kg, 1.80 m -> 80 / 3.24 = 24.6913... -> 24.69
        self.assertEqual(calculate_bmi(80.0, 1.80), 24.69)
        # 50 kg, 1.60 m -> 50 / 2.56 = 19.5312... -> 19.53
        self.assertEqual(calculate_bmi(50.0, 1.60), 19.53)

    def test_bmi_rounding(self):
        """Verifies BMI is strictly rounded to 2 decimal places."""
        res = calculate_bmi(68.5, 1.72)
        # 68.5 / (1.72^2) = 23.1544...
        self.assertEqual(res, 23.15)
        self.assertEqual(len(str(res).split(".")[1]), 2)

    def test_bmi_zero_or_negative_error(self):
        """Verifies ValueError is raised for zero or negative measurements."""
        with self.assertRaises(ValueError):
            calculate_bmi(-70.0, 1.75)
        with self.assertRaises(ValueError):
            calculate_bmi(70.0, 0.0)
        with self.assertRaises(ValueError):
            calculate_bmi(70.0, -1.75)

    def test_who_category_classifications(self):
        """Tests standard WHO category boundaries."""
        # Underweight: BMI < 18.5
        self.assertEqual(classify_bmi(16.0), "Underweight")
        self.assertEqual(classify_bmi(18.49), "Underweight")

        # Normal weight: 18.5 <= BMI <= 24.9
        self.assertEqual(classify_bmi(18.5), "Normal weight")
        self.assertEqual(classify_bmi(22.0), "Normal weight")
        self.assertEqual(classify_bmi(24.9), "Normal weight")

        # Overweight: 25.0 <= BMI <= 29.9
        self.assertEqual(classify_bmi(25.0), "Overweight")
        self.assertEqual(classify_bmi(27.5), "Overweight")
        self.assertEqual(classify_bmi(29.9), "Overweight")

        # Obesity: BMI >= 30.0
        self.assertEqual(classify_bmi(30.0), "Obesity")
        self.assertEqual(classify_bmi(35.5), "Obesity")
        self.assertEqual(classify_bmi(42.0), "Obesity")

    def test_healthy_weight_range(self):
        """Tests healthy weight range boundaries for a given height."""
        # For 1.75 m: 18.5 * 3.0625 = 56.656... -> 56.7 kg, 24.9 * 3.0625 = 76.256... -> 76.3 kg
        min_w, max_w = calculate_healthy_weight_range(1.75)
        self.assertAlmostEqual(min_w, 56.7, places=1)
        self.assertAlmostEqual(max_w, 76.3, places=1)

    def test_input_validation_success(self):
        """Tests successful validation with clean numeric inputs."""
        valid, data, err = validate_user_inputs("Alice", "65.5", "1.68")
        self.assertTrue(valid)
        self.assertIsNone(err)
        name, weight, height = data
        self.assertEqual(name, "Alice")
        self.assertEqual(weight, 65.5)
        self.assertEqual(height, 1.68)

    def test_input_validation_empty_fields(self):
        """Tests validation failures on empty name, weight, or height."""
        valid, _, err = validate_user_inputs("", "70", "1.75")
        self.assertFalse(valid)
        self.assertIn("user name", err.lower())

        valid, _, err = validate_user_inputs("Bob", "", "1.75")
        self.assertFalse(valid)
        self.assertIn("weight", err.lower())

        valid, _, err = validate_user_inputs("Bob", "70", "")
        self.assertFalse(valid)
        self.assertIn("height", err.lower())

    def test_input_validation_non_numeric(self):
        """Tests validation failures on non-numeric strings."""
        valid, _, err = validate_user_inputs("Charlie", "seventy", "1.75")
        self.assertFalse(valid)
        self.assertIn("numeric", err.lower())

        valid, _, err = validate_user_inputs("Charlie", "70", "one_point_eight")
        self.assertFalse(valid)
        self.assertIn("numeric", err.lower())

    def test_input_validation_out_of_bounds(self):
        """Tests validation failures on zero, negative, or unrealistic numbers."""
        # Negative weight
        valid, _, err = validate_user_inputs("David", "-70", "1.75")
        self.assertFalse(valid)
        self.assertIn("greater than zero", err.lower())

        # Zero height
        valid, _, err = validate_user_inputs("David", "70", "0")
        self.assertFalse(valid)
        self.assertIn("greater than zero", err.lower())

        # Height entered in cm by mistake (e.g., 175 instead of 1.75)
        valid, _, err = validate_user_inputs("David", "70", "175")
        self.assertFalse(valid)
        self.assertIn("in meters", err.lower())


class TestDatabaseManager(unittest.TestCase):
    """Unit tests for SQLite database operations and error handling."""

    TEST_DB = "test_bmi_suite.db"

    def setUp(self):
        """Creates a fresh test database for each test."""
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)
        self.db = DatabaseManager(self.TEST_DB)

    def tearDown(self):
        """Cleans up the test database file."""
        for ext in ["", "-wal", "-shm"]:
            path = self.TEST_DB + ext
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    def test_insert_and_retrieve_record(self):
        """Verifies inserting a record and retrieving it by user name."""
        rec_id = self.db.insert_record("John", 70.0, 1.75, 22.86, "Normal weight", "2026-05-10 10:00:00")
        self.assertGreater(rec_id, 0)

        user_records = self.db.get_user_records("John")
        self.assertEqual(len(user_records), 1)
        r = user_records[0]
        self.assertEqual(r["user_name"], "John")
        self.assertEqual(r["weight"], 70.0)
        self.assertEqual(r["height"], 1.75)
        self.assertEqual(r["bmi"], 22.86)
        self.assertEqual(r["category"], "Normal weight")
        self.assertEqual(r["date_time"], "2026-05-10 10:00:00")

    def test_multi_user_isolation(self):
        """Verifies that records are correctly separated by user name."""
        self.db.insert_record("Alice", 55.0, 1.65, 20.20, "Normal weight")
        self.db.insert_record("Alice", 56.0, 1.65, 20.57, "Normal weight")
        self.db.insert_record("Bob", 85.0, 1.80, 26.23, "Overweight")

        alice_records = self.db.get_user_records("Alice")
        bob_records = self.db.get_user_records("Bob")
        all_users = self.db.get_all_users()

        self.assertEqual(len(alice_records), 2)
        self.assertEqual(len(bob_records), 1)
        self.assertEqual(all_users, ["Alice", "Bob"])

    def test_delete_record(self):
        """Verifies deleting an individual record by ID."""
        id1 = self.db.insert_record("User1", 60.0, 1.70, 20.76, "Normal weight")
        id2 = self.db.insert_record("User1", 62.0, 1.70, 21.45, "Normal weight")

        self.assertEqual(len(self.db.get_user_records("User1")), 2)
        self.assertTrue(self.db.delete_record(id1))
        self.assertEqual(len(self.db.get_user_records("User1")), 1)
        self.assertEqual(self.db.get_user_records("User1")[0]["id"], id2)

    def test_clear_user_history(self):
        """Verifies clearing all records for a specific named user."""
        self.db.insert_record("UserA", 70.0, 1.75, 22.86, "Normal weight")
        self.db.insert_record("UserA", 71.0, 1.75, 23.18, "Normal weight")
        self.db.insert_record("UserB", 80.0, 1.80, 24.69, "Normal weight")

        self.assertTrue(self.db.clear_user_history("UserA"))
        self.assertEqual(len(self.db.get_user_records("UserA")), 0)
        self.assertEqual(len(self.db.get_user_records("UserB")), 1)


if __name__ == "__main__":
    unittest.main()
