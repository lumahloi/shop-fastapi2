import random

def unique_email():
    return f"{''.join([str(random.randint(0, 9)) for _ in range(11)])}@example.com"

def unique_cpf():
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])