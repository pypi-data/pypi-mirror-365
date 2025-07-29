def add(a: float, b: float) -> float:
    """返回两个数的和"""
    return a + b

def subtract(a: float, b: float) -> float:
    """返回两个数的差"""
    return a - b

def multiply(a: float, b: float) -> float:
    """返回两个数的积"""
    return a * b

def divide(a: float, b: float) -> float:
    """
    返回两个数的商
    如果除数为0，返回无穷大
    """
    return a / b if b != 0 else float('inf')
