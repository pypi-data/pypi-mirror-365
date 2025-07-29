import unittest
from math_utils.statistics import mean, median

class TestStatistics(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3)
        self.assertEqual(mean([]), 0)
    
    def test_median(self):
        self.assertEqual(median([1, 3, 2]), 2)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)
