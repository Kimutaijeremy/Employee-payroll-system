import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Simple validation for international numbers
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))

def validate_date(date_str: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date format"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

def validate_salary(salary: float) -> bool:
    """Validate salary amount"""
    return salary >= 0

def validate_percentage(percentage: float) -> bool:
    """Validate percentage value"""
    return 0 <= percentage <= 100