from ..models import Employee, Payroll
from ..config import Config
from datetime import datetime

class PayrollCalculator:
    @staticmethod
    def calculate_tax(gross_salary):
        tax = 0.0
        remaining = gross_salary
        
        for lower, upper, rate in Config.TAX_BRACKETS:
            if remaining <= 0:
                break
            
            if upper == float('inf'):
                bracket_amount = remaining
            else:
                bracket_amount = min(upper - lower + 1, remaining)
            
            if bracket_amount > 0:
                tax += bracket_amount * rate
                remaining -= bracket_amount
        
        return round(tax, 2)
    
    @staticmethod
    def calculate_nhif(gross_salary):
        for lower, upper, amount in Config.NHIF_RATES:
            if lower <= gross_salary <= upper:
                return float(amount)
        return 1700.0
    
    @staticmethod
    def calculate_nssf(gross_salary):
        pensionable = min(gross_salary, Config.NSSF_LIMIT)
        return round(pensionable * Config.NSSF_RATE, 2)

class PayrollService:
    def __init__(self, session):
        self.session = session
    
    def generate_payroll(self, employee_id, month, year):
        employee = self.session.query(Employee).filter(
            Employee.employee_id == employee_id,
            Employee.is_active == True
        ).first()
        
        if not employee:
            raise ValueError("Employee not found or inactive")
        
        if not employee.role:
            raise ValueError("Employee has no role assigned")
        
        role = employee.role
        
        # Calculate gross salary
        base = role.base_salary
        housing = role.housing_allowance
        transport = role.transport_allowance
        medical = role.medical_allowance
        other = role.other_allowance
        gross = base + housing + transport + medical + other
        
        # Calculate deductions
        tax = PayrollCalculator.calculate_tax(gross)
        nhif = PayrollCalculator.calculate_nhif(gross)
        nssf = PayrollCalculator.calculate_nssf(gross)
        total_deductions = tax + nhif + nssf
        net = gross - total_deductions
        
        # Create payroll record
        payroll = Payroll(
            payroll_id=f"PAY{year:04d}{month:02d}{employee.id:06d}",
            employee_id=employee.id,
            month=month,
            year=year,
            base_salary=base,
            housing_allowance=housing,
            transport_allowance=transport,
            medical_allowance=medical,
            other_allowance=other,
            gross_salary=gross,
            tax_deduction=tax,
            nhif_deduction=nhif,
            nssf_deduction=nssf,
            total_deductions=total_deductions,
            net_salary=net,
            status='generated'
        )
        
        self.session.add(payroll)
        self.session.commit()
        return payroll