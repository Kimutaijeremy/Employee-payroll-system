import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///payroll.db")
    CURRENCY = "KES"
    
    # Tax brackets for Kenya
    TAX_BRACKETS = [
        (0, 24000, 0.10),
        (24001, 32333, 0.25),
        (32334, 500000, 0.30),
        (500001, 800000, 0.325),
        (800001, float('inf'), 0.35)
    ]
    
    # NHIF rates
    NHIF_RATES = [
        (0, 5999, 150),
        (6000, 7999, 300),
        (8000, 11999, 400),
        (12000, 14999, 500),
        (15000, 19999, 600),
        (20000, 24999, 750),
        (25000, 29999, 850),
        (30000, 34999, 900),
        (35000, 39999, 950),
        (40000, 44999, 1000),
        (45000, 49999, 1100),
        (50000, 59999, 1200),
        (60000, 69999, 1300),
        (70000, 79999, 1400),
        (80000, 89999, 1500),
        (90000, 99999, 1600),
        (100000, float('inf'), 1700)
    ]
    
    NSSF_RATE = 0.06
    NSSF_LIMIT = 18000
