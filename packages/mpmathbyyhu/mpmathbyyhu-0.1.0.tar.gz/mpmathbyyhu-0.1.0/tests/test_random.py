import unittest
from math_utils.random_generators import generate_random_numbers, random_choice

class TestRandomGenerators(unittest.TestCase):
    def test_generate_random_numbers(self):
        nums = generate_random_numbers(5, 1, 10)
        self.assertEqual(len(nums), 5)
        self.assertTrue(all(1 <= x <= 10 for x in nums))
    
    def test_random_choice(self):
        items = ['a', 'b', 'c']
        choice = random_choice(items)
        self.assertIn(choice, items)
