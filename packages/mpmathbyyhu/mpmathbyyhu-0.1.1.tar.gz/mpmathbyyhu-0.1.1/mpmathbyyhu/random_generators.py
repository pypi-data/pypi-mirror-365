import random
from typing import List, Any

def generate_random_numbers(count: int, min_val: float, max_val: float) -> List[float]:
    """生成指定范围内的随机数列表"""
    if count < 0:
        raise ValueError("数量不能为负数")
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return [random.uniform(min_val, max_val) for _ in range(count)]

def random_integer(min_val: int, max_val: int) -> int:
    """生成随机整数"""
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return random.randint(min_val, max_val)

def random_float(min_val: float, max_val: float) -> float:
    """生成随机浮点数"""
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return random.uniform(min_val, max_val)

def random_choice(items: List[Any]) -> Any:
    """从列表中随机选择一项"""
    if not items:
        raise ValueError("列表不能为空")
    return random.choice(items)

def shuffle_list(items: List[Any]) -> List[Any]:
    """随机打乱列表顺序"""
    shuffled = items.copy()
    random.shuffle(shuffled)
    return shuffled
