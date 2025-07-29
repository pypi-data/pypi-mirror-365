import math

def circle_area(radius: float) -> float:
    """计算圆的面积"""
    if radius < 0:
        raise ValueError("半径不能为负数")
    return math.pi * radius ** 2

def triangle_area(base: float, height: float) -> float:
    """计算三角形的面积"""
    if base < 0 or height < 0:
        raise ValueError("底边和高度不能为负数")
    return 0.5 * base * height

def rectangle_area(length: float, width: float) -> float:
    """计算矩形面积"""
    if length < 0 or width < 0:
        raise ValueError("长度和宽度不能为负数")
    return length * width

def pythagorean(a: float, b: float) -> float:
    """计算直角三角形斜边"""
    if a < 0 or b < 0:
        raise ValueError("直角边长度不能为负数")
    return (a ** 2 + b ** 2) ** 0.5
