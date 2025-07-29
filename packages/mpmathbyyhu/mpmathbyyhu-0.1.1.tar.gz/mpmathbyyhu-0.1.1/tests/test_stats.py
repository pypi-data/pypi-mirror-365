import unittest
from mpmathbyyhu.statistics import mean, median, mode, variance, standard_deviation

class TestStatistics(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3)
        self.assertEqual(mean([]), 0)
    
    def test_median(self):
        self.assertEqual(median([1, 3, 2]), 2)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)
    
    def test_mode(self):
        self.assertEqual(mode([1, 2, 2, 3]), 2)
        self.assertEqual(mode([1, 1, 2, 2]), [1, 2])
    
    def test_variance(self):
        self.assertAlmostEqual(variance([1, 2, 3, 4, 5]), 2)
    
    def test_standard_deviation(self):
        self.assertAlmostEqual(standard_deviation([1, 2, 3, 4, 5]), 1.414213562, places=6)
