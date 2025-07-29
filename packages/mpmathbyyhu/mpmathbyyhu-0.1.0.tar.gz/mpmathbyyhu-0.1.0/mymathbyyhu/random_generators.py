import random
from typing import List, Any

def generate_random_numbers(count: int, min_val: float, max_val: float) -> List[float]:
    """生成指定范围内的随机数列表"""
    return [random.uniform(min_val, max_val) for _ in range(count)]

def random_choice(items: List[Any]) -> Any:
    """从列表中随机选择一个元素"""
    return random.choice(items)
