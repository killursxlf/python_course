import re


def validate_full_name(full_name: str) -> tuple[str, str]:
    parts = re.findall(r'[A-Za-zА-Яа-яЁё]+', full_name)
    if len(parts) < 2:
        raise ValueError('Incorrect full name format')
    return parts[0], parts[1]


def validate_account_number(account_number: str) -> str:
    account_number = re.sub(r'[#%_?&]', '-', account_number)
    
    if len(account_number) != 18:
        raise ValueError('Wrong length for account_number (required 18 characters)')
    
    if not account_number.startswith('ID--'):
        raise ValueError('account_number must start with "ID--"')
    
    pattern = r'[A-Za-z]{1,3}-\d+-'
    if not re.search(pattern, account_number):
        raise ValueError('Invalid ID format!')
    
    return account_number


def validate_field_value(value, allowed_set, field_name):
    if value not in allowed_set:
        raise ValueError(f'Invalid value {value} for field {field_name}!')
    return value


def validate_amount(amount):
    if not isinstance(amount, (float, int)):
        raise ValueError("amount must be a number")
    
    if amount < 0:
        raise ValueError("amount cannot be negative")
    
    return float(amount)
