import unittest
from mpmathbyyhu.basic_operations import add, subtract, multiply, divide, power, square_root

class TestBasicOperations(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
    
    def test_multiply(self):
        self.assertEqual(multiply(4, 5), 20)
        self.assertEqual(multiply(-3, 4), -12)
    
    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)
        self.assertEqual(divide(5, 0), float('inf'))
    
    def test_power(self):
        self.assertEqual(power(2, 3), 8)
        self.assertEqual(power(5, 0), 1)
    
    def test_square_root(self):
        self.assertAlmostEqual(square_root(9), 3)
        with self.assertRaises(ValueError):
            square_root(-1)
