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

def power(base: float, exponent: float) -> float:
    """计算幂次"""
    return base ** exponent

def square_root(x: float) -> float:
    """计算平方根"""
    if x < 0:
        raise ValueError("平方根输入不能为负数")
    return x ** 0.5
