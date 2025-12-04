from datetime import datetime
from ..config import Config

def format_currency(amount):
    return f"{Config.CURRENCY} {amount:,.2f}"

def format_date(date_obj):
    if not date_obj:
        return "N/A"
    return date_obj.strftime("%Y-%m-%d")