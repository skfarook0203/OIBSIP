"""
Unit tests for the Random Password Generator core logic.
Validates all Oasis Infobyte Task 3 requirements.
"""

import string
import secrets
import unittest

def generate_secure_password(length: int, use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool, exclude_ambiguous: bool = False):
    """
    Core password generator logic using secrets module.
    Guarantees at least one character from every selected category.
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")
    
    selected_categories = []
    
    # Ambiguous characters set: '0', 'O', 'l', 'I', '1'
    ambiguous_set = set("0OlI1")
    
    if use_upper:
        pool = string.ascii_uppercase
        if exclude_ambiguous:
            pool = "".join(c for c in pool if c not in ambiguous_set)
        if pool:
            selected_categories.append(pool)
            
    if use_lower:
        pool = string.ascii_lowercase
        if exclude_ambiguous:
            pool = "".join(c for c in pool if c not in ambiguous_set)
        if pool:
            selected_categories.append(pool)
            
    if use_digits:
        pool = string.digits
        if exclude_ambiguous:
            pool = "".join(c for c in pool if c not in ambiguous_set)
        if pool:
            selected_categories.append(pool)
            
    if use_symbols:
        pool = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if exclude_ambiguous:
            pool = "".join(c for c in pool if c not in ambiguous_set and c not in "|")
        if pool:
            selected_categories.append(pool)
            
    if len(selected_categories) < 2:
        raise ValueError("Please select at least 2 character types.")
        
    if length < len(selected_categories):
        raise ValueError(f"Password length ({length}) is smaller than number of selected types ({len(selected_categories)}).")
        
    # Guarantee at least one character from every selected category using secrets.choice
    password_chars = [secrets.choice(category) for category in selected_categories]
    
    # Fill remainder from combined character pool
    combined_pool = "".join(selected_categories)
    remainder_length = length - len(password_chars)
    for _ in range(remainder_length):
        password_chars.append(secrets.choice(combined_pool))
        
    # Cryptographically secure Fisher-Yates shuffle using secrets.randbelow
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
        
    return "".join(password_chars)


def evaluate_password_strength(password: str):
    """
    Calculates password strength considering length, diversity, and complexity.
    Returns: (score: int 0-4, label: str, color: str)
    """
    if not password:
        return 0, "None", "#888888"
        
    length = len(password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    type_count = sum([has_upper, has_lower, has_digit, has_symbol])
    
    # Calculate score based on length and types
    score = 0
    if length >= 8 and type_count >= 2:
        score = 1  # Weak
    if length >= 12 and type_count >= 3:
        score = 2  # Medium
    if length >= 16 and type_count >= 3:
        score = 3  # Strong
    if length >= 16 and type_count == 4:
        score = 4  # Very Strong
    elif length >= 20 and type_count >= 3:
        score = 4  # Very Strong
        
    labels = {
        0: ("Very Weak", "#ef4444"),
        1: ("Weak", "#f97316"),
        2: ("Medium", "#eab308"),
        3: ("Strong", "#22c55e"),
        4: ("Very Strong", "#10b981")
    }
    label, color = labels.get(score, ("Weak", "#f97316"))
    return score, label, color


class TestPasswordGenerator(unittest.TestCase):
    def test_minimum_length(self):
        with self.assertRaises(ValueError):
            generate_secure_password(7, True, True, False, False)
            
    def test_minimum_two_types(self):
        with self.assertRaises(ValueError):
            generate_secure_password(10, True, False, False, False)
            
    def test_all_selected_types_represented(self):
        for _ in range(50):
            pwd = generate_secure_password(8, True, True, True, True)
            self.assertEqual(len(pwd), 8)
            self.assertTrue(any(c in string.ascii_uppercase for c in pwd), "Upper missing")
            self.assertTrue(any(c in string.ascii_lowercase for c in pwd), "Lower missing")
            self.assertTrue(any(c in string.digits for c in pwd), "Digit missing")
            self.assertTrue(any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd), "Symbol missing")
            
    def test_exclude_ambiguous(self):
        ambiguous = set("0OlI1|")
        for _ in range(50):
            pwd = generate_secure_password(24, True, True, True, True, exclude_ambiguous=True)
            self.assertFalse(any(c in ambiguous for c in pwd), f"Found ambiguous char in {pwd}")

    def test_strength_indicator(self):
        _, label, _ = evaluate_password_strength("Ab1!cdef")
        self.assertIn(label, ["Weak", "Medium"])
        _, label_strong, _ = evaluate_password_strength("Ab1!cD2#eF3$gH4%")
        self.assertIn(label_strong, ["Strong", "Very Strong"])

if __name__ == '__main__':
    unittest.main()
