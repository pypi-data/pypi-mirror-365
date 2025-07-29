import unittest
from math import pi
from math_utils.geometry import circle_area, triangle_area

class TestGeometry(unittest.TestCase):
    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(1), pi)
    
    def test_triangle_area(self):
        self.assertEqual(triangle_area(4, 5), 10)
