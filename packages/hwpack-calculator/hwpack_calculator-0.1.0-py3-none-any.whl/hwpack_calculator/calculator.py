def add(a: float, b: float) -> float:
    """2つの数値を加算します。"""
    return a + b

def subtract(a: float, b: float) -> float:
    """2つの数値を減算します。"""
    return a - b

def multiply(a: float, b: float) -> float:
    """2つの数値を乗算します。"""
    return a * b

def divide(a: float, b: float) -> float:
    """2つの数値を除算します。ゼロ除算の場合はエラーを返します。"""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
