from typing import List, Union

def mean(numbers: List[float]) -> float:
    """计算列表的平均值"""
    return sum(numbers) / len(numbers) if numbers else 0

def median(numbers: List[float]) -> float:
    """计算列表的中位数"""
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    return (sorted_numbers[mid] + sorted_numbers[mid - 1]) / 2 if n % 2 == 0 else sorted_numbers[mid]
