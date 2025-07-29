import unittest
from math import pi
from mpmathbyyhu.geometry import circle_area, triangle_area, rectangle_area, pythagorean

class TestGeometry(unittest.TestCase):
    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(3), 28.274333882, places=6)
        with self.assertRaises(ValueError):
            circle_area(-1)
    
    def test_triangle_area(self):
        self.assertEqual(triangle_area(4, 5), 10)
        self.assertEqual(triangle_area(0, 5), 0)
    
    def test_rectangle_area(self):
        self.assertEqual(rectangle_area(4, 5), 20)
        with self.assertRaises(ValueError):
            rectangle_area(-1, 5)
    
    def test_pythagorean(self):
        self.assertEqual(pythagorean(3, 4), 5)
        with self.assertRaises(ValueError):
            pythagorean(-3, 4)
