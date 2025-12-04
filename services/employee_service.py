from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Employee, Department, Role
from datetime import datetime
from typing import Optional, List, Dict
import re

class EmployeeService:
    def __init__(self, session: Session):
        self.session = session
    
    def add_employee(self, data: Dict) -> Optional[Employee]:
        """Add a new employee"""
        try:
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get('email', '')):
                raise ValueError("Invalid email format")
            
            employee = Employee(**data)
            self.session.add(employee)
            self.session.commit()
            return employee
        except IntegrityError as e:
            self.session.rollback()
            if "email" in str(e):
                raise ValueError("Email already exists")
            elif "employee_id" in str(e):
                raise ValueError("Employee ID already exists")
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error adding employee: {str(e)}")
    
    def update_employee(self, employee_id: str, data: Dict) -> Optional[Employee]:
        """Update employee details"""
        employee = self.session.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        
        if not employee:
            raise ValueError("Employee not found")
        
        for key, value in data.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        
        self.session.commit()
        return employee
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return self.session.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
    
    def list_employees(self, active_only: bool = True, 
                      department_id: Optional[int] = None,
                      role_id: Optional[int] = None) -> List[Employee]:
        """List employees with optional filters"""
        query = self.session.query(Employee)
        
        if active_only:
            query = query.filter(Employee.is_active == True)
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if role_id:
            query = query.filter(Employee.role_id == role_id)
        
        return query.order_by(Employee.last_name, Employee.first_name).all()
    
    def deactivate_employee(self, employee_id: str) -> bool:
        """Deactivate an employee"""
        employee = self.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")
        
        employee.is_active = False
        self.session.commit()
        return True
    
    def activate_employee(self, employee_id: str) -> bool:
        """Activate an employee"""
        employee = self.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")
        
        employee.is_active = True
        self.session.commit()
        return True
    
    def search_employees(self, search_term: str) -> List[Employee]:
        """Search employees by name or email"""
        return self.session.query(Employee).filter(
            (Employee.first_name.ilike(f"%{search_term}%")) |
            (Employee.last_name.ilike(f"%{search_term}%")) |
            (Employee.email.ilike(f"%{search_term}%"))
        ).all()