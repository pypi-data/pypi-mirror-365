from typing import List, Union
from collections import Counter

def mean(numbers: List[float]) -> float:
    """计算列表的平均值"""
    return sum(numbers) / len(numbers) if numbers else 0.0

def median(numbers: List[float]) -> float:
    """计算列表的中位数"""
    if not numbers:
        return 0.0
    
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    
    if n % 2 == 1:
        return sorted_numbers[mid]
    else:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2

def mode(numbers: List[float]) -> Union[float, List[float]]:
    """计算列表的众数"""
    if not numbers:
        return 0.0
    
    counts = Counter(numbers)
    max_count = max(counts.values())
    modes = [num for num, count in counts.items() if count == max_count]
    
    return modes[0] if len(modes) == 1 else modes

def variance(numbers: List[float]) -> float:
    """计算方差"""
    if not numbers:
        return 0.0
    
    avg = mean(numbers)
    return sum((x - avg) ** 2 for x in numbers) / len(numbers)

def standard_deviation(numbers: List[float]) -> float:
    """计算标准差"""
    return variance(numbers) ** 0.5
