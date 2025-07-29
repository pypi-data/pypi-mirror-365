import unittest
from mpmathbyyhu.random_generators import generate_random_numbers, random_integer, random_float, random_choice, shuffle_list

class TestRandomGenerators(unittest.TestCase):
    def test_generate_random_numbers(self):
        nums = generate_random_numbers(5, 1, 10)
        self.assertEqual(len(nums), 5)
        self.assertTrue(all(1 <= x <= 10 for x in nums))
        with self.assertRaises(ValueError):
            generate_random_numbers(-1, 1, 10)
    
    def test_random_integer(self):
        for _ in range(100):
            num = random_integer(1, 10)
            self.assertTrue(1 <= num <= 10)
            self.assertIsInstance(num, int)
    
    def test_random_float(self):
        num = random_float(1.0, 10.0)
        self.assertTrue(1.0 <= num <= 10.0)
    
    def test_random_choice(self):
        items = ['a', 'b', 'c']
        choice = random_choice(items)
        self.assertIn(choice, items)
        with self.assertRaises(ValueError):
            random_choice([])
    
    def test_shuffle_list(self):
        original = [1, 2, 3, 4, 5]
        shuffled = shuffle_list(original.copy())
        self.assertEqual(sorted(original), sorted(shuffled))
        self.assertNotEqual(original, shuffled)
