from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Payroll, Employee, Role, Department
from config import Config
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import calendar

class PayrollService:
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_tax(self, taxable_income: float) -> float:
        """Calculate PAYE tax based on income brackets"""
        tax = 0.0
        remaining_income = taxable_income
        
        for lower, upper, rate in Config.TAX_BRACKETS:
            if remaining_income <= 0:
                break
            
            bracket_amount = min(upper - lower + 1, remaining_income) if upper != float('inf') else remaining_income
            if bracket_amount > 0:
                tax += bracket_amount * rate
                remaining_income -= bracket_amount
        
        return round(tax, 2)
    
    def calculate_nhif(self, gross_salary: float) -> float:
        """Calculate NHIF contribution"""
        for lower, upper, amount in Config.NHIF_RATES:
            if lower <= gross_salary <= upper:
                return float(amount)
        return 0.0
    
    def calculate_nssf(self, gross_salary: float) -> float:
        """Calculate NSSF contribution (simplified)"""
        pensionable_amount = min(gross_salary, 18000)  # Upper limit for NSSF in Kenya
        return round(pensionable_amount * Config.NSSF_RATE, 2)
    
    def generate_payroll(self, employee_id: str, month: int, year: int, 
                        additional_deductions: float = 0.0) -> Payroll:
        """Generate payroll for a single employee"""
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
        base_salary = role.base_salary
        housing_allowance = role.housing_allowance
        transport_allowance = role.transport_allowance
        medical_allowance = role.medical_allowance
        other_allowance = role.other_allowance
        
        gross_salary = (base_salary + housing_allowance + transport_allowance + 
                       medical_allowance + other_allowance)
        
        # Calculate deductions
        tax_deduction = self.calculate_tax(gross_salary)
        nhif_deduction = self.calculate_nhif(gross_salary)
        nssf_deduction = self.calculate_nssf(gross_salary)
        other_deductions = additional_deductions
        
        total_deductions = tax_deduction + nhif_deduction + nssf_deduction + other_deductions
        net_salary = gross_salary - total_deductions
        
        # Create payroll record
        payroll = Payroll(
            employee_id=employee.id,
            month=month,
            year=year,
            base_salary=base_salary,
            housing_allowance=housing_allowance,
            transport_allowance=transport_allowance,
            medical_allowance=medical_allowance,
            other_allowance=other_allowance,
            tax_deduction=tax_deduction,
            nhif_deduction=nhif_deduction,
            nssf_deduction=nssf_deduction,
            other_deductions=other_deductions,
            gross_salary=gross_salary,
            total_deductions=total_deductions,
            net_salary=net_salary,
            status='generated'
        )
        
        self.session.add(payroll)
        self.session.commit()
        return payroll
    
    def generate_bulk_payroll(self, month: int, year: int) -> List[Payroll]:
        """Generate payroll for all active employees"""
        active_employees = self.session.query(Employee).filter(
            Employee.is_active == True
        ).all()
        
        payrolls = []
        for employee in active_employees:
            try:
                payroll = self.generate_payroll(employee.employee_id, month, year)
                payrolls.append(payroll)
            except Exception as e:
                print(f"Error generating payroll for {employee.full_name()}: {str(e)}")
        
        return payrolls
    
    def get_payroll(self, payroll_id: str) -> Optional[Payroll]:
        """Get payroll by ID"""
        return self.session.query(Payroll).filter(
            Payroll.payroll_id == payroll_id
        ).first()
    
    def get_employee_payroll_history(self, employee_id: str) -> List[Payroll]:
        """Get payroll history for an employee"""
        employee = self.session.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        
        if not employee:
            raise ValueError("Employee not found")
        
        return self.session.query(Payroll).filter(
            Payroll.employee_id == employee.id
        ).order_by(Payroll.year.desc(), Payroll.month.desc()).all()
    
    def get_monthly_payrolls(self, month: int, year: int) -> List[Payroll]:
        """Get all payrolls for a specific month"""
        return self.session.query(Payroll).filter(
            Payroll.month == month,
            Payroll.year == year
        ).order_by(Payroll.employee_id).all()
    
    def approve_payroll(self, payroll_id: str) -> Payroll:
        """Approve a payroll"""
        payroll = self.get_payroll(payroll_id)
        
        if not payroll:
            raise ValueError("Payroll not found")
        
        payroll.status = 'approved'
        self.session.commit()
        return payroll
    
    def mark_as_paid(self, payroll_id: str, payment_date: datetime = None) -> Payroll:
        """Mark payroll as paid"""
        payroll = self.get_payroll(payroll_id)
        
        if not payroll:
            raise ValueError("Payroll not found")
        
        payroll.status = 'paid'
        payroll.payment_date = payment_date or datetime.utcnow().date()
        self.session.commit()
        return payroll
    
    def get_payroll_summary(self, month: int, year: int) -> Dict:
        """Get summary statistics for monthly payroll"""
        payrolls = self.get_monthly_payrolls(month, year)
        
        if not payrolls:
            return {}
        
        total_gross = sum(p.gross_salary for p in payrolls)
        total_deductions = sum(p.total_deductions for p in payrolls)
        total_net = sum(p.net_salary for p in payrolls)
        
        return {
            'total_employees': len(payrolls),
            'total_gross_salary': total_gross,
            'total_deductions': total_deductions,
            'total_net_salary': total_net,
            'average_net_salary': total_net / len(payrolls) if payrolls else 0,
            'month': month,
            'year': year,
            'currency': Config.CURRENCY
        }
    
    def get_department_summary(self, month: int, year: int) -> List[Dict]:
        """Get payroll summary by department"""
        result = self.session.query(
            Department.name,
            func.count(Payroll.id).label('employee_count'),
            func.sum(Payroll.gross_salary).label('total_gross'),
            func.sum(Payroll.total_deductions).label('total_deductions'),
            func.sum(Payroll.net_salary).label('total_net')
        ).join(
            Employee, Employee.id == Payroll.employee_id
        ).join(
            Department, Department.id == Employee.department_id
        ).filter(
            Payroll.month == month,
            Payroll.year == year
        ).group_by(
            Department.id
        ).order_by(
            Department.name
        ).all()
        
        return [
            {
                'department': row[0],
                'employee_count': row[1],
                'total_gross': row[2] or 0,
                'total_deductions': row[3] or 0,
                'total_net': row[4] or 0
            }
            for row in result
        ]
    
    def get_top_earners(self, month: int, year: int, limit: int = 10) -> List[Dict]:
        """Get top earning employees for a month"""
        payrolls = self.session.query(
            Payroll,
            Employee
        ).join(
            Employee, Employee.id == Payroll.employee_id
        ).filter(
            Payroll.month == month,
            Payroll.year == year
        ).order_by(
            Payroll.net_salary.desc()
        ).limit(limit).all()
        
        return [
            {
                'employee_id': employee.employee_id,
                'name': employee.full_name(),
                'department': employee.department.name if employee.department else 'N/A',
                'net_salary': payroll.net_salary,
                'gross_salary': payroll.gross_salary
            }
            for payroll, employee in payrolls
        ]