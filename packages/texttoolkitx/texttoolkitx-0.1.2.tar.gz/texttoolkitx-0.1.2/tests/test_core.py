import unittest
from texttoolkitx import slugify, truncate, is_palindrome, random_string

class TestStringUtils(unittest.TestCase):

    # --- slugify ---
    def test_slugify_basic(self):
        self.assertEqual(slugify("Hello World!"), "hello-world")

    def test_slugify_extra_symbols(self):
        self.assertEqual(slugify(" Python 3.10 @ 2024 "), "python-310-2024")

    def test_slugify_empty(self):
        self.assertEqual(slugify(""), "")

    # --- truncate ---
    def test_truncate_short_text(self):
        self.assertEqual(truncate("Short", 10), "Short")

    def test_truncate_long_text(self):
        self.assertEqual(truncate("This is a long sentence.", 10), "This is a...")

    def test_truncate_exact_length(self):
        self.assertEqual(truncate("1234567890", 10), "1234567890")

    def test_truncate_zero_length(self):
        self.assertEqual(truncate("Test", 0), "...")

    # --- is_palindrome ---
    def test_is_palindrome_true_simple(self):
        self.assertTrue(is_palindrome("madam"))

    def test_is_palindrome_true_phrase(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))

    def test_is_palindrome_false(self):
        self.assertFalse(is_palindrome("openai"))

    def test_is_palindrome_empty_string(self):
        self.assertTrue(is_palindrome(""))

    def test_is_palindrome_single_char(self):
        self.assertTrue(is_palindrome("x"))

    # --- random_string ---
    def test_random_string_length(self):
        for i in range(1, 20):
            self.assertEqual(len(random_string(i)), i)

    def test_random_string_is_alnum(self):
        for _ in range(5):
            s = random_string(12)
            self.assertTrue(s.isalnum())

if __name__ == "__main__":
    unittest.main()
