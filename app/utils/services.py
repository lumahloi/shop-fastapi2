import random

def unique_email():
    return f"{''.join([str(random.randint(0, 9)) for _ in range(6)])}@example.com"

def unique_cpf():
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def to_str_lower(value):
    if isinstance(value, str):
        return value.lower()
    elif hasattr(value, "value"):
        return str(value.value).lower()
    return str(value).lower()
