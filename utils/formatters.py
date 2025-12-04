from config import Config
from datetime import datetime

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{Config.CURRENCY} {amount:,.2f}"

def format_date(date: datetime) -> str:
    """Format date to readable string"""
    if not date:
        return "N/A"
    return date.strftime("%d %b %Y")

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.1f}%"

def format_phone(phone: str) -> str:
    """Format phone number"""
    if not phone:
        return "N/A"
    return f"{phone[:4]} {phone[4:7]} {phone[7:]}"