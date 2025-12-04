from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Department, Employee
from typing import Optional, List, Dict

class DepartmentService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_department(self, data: Dict) -> Department:
        """Create a new department"""
        try:
            department = Department(**data)
            self.session.add(department)
            self.session.commit()
            return department
        except IntegrityError as e:
            self.session.rollback()
            if "name" in str(e):
                raise ValueError("Department name already exists")
            elif "code" in str(e):
                raise ValueError("Department code already exists")
            raise ValueError(f"Database error: {str(e)}")
    
    def update_department(self, dept_id: int, data: Dict) -> Optional[Department]:
        """Update department details"""
        department = self.session.query(Department).get(dept_id)
        
        if not department:
            raise ValueError("Department not found")
        
        for key, value in data.items():
            if hasattr(department, key):
                setattr(department, key, value)
        
        self.session.commit()
        return department
    
    def delete_department(self, dept_id: int) -> bool:
        """Delete a department (if empty)"""
        department = self.session.query(Department).get(dept_id)
        
        if not department:
            raise ValueError("Department not found")
        
        # Check if department has employees
        employee_count = self.session.query(Employee).filter(
            Employee.department_id == dept_id
        ).count()
        
        if employee_count > 0:
            raise ValueError(f"Cannot delete department. {employee_count} employees are assigned to it.")
        
        self.session.delete(department)
        self.session.commit()
        return True
    
    def get_department(self, dept_id: int) -> Optional[Department]:
        """Get department by ID"""
        return self.session.query(Department).get(dept_id)
    
    def list_departments(self) -> List[Department]:
        """List all departments"""
        return self.session.query(Department).order_by(Department.name).all()
    
    def get_department_by_code(self, code: str) -> Optional[Department]:
        """Get department by code"""
        return self.session.query(Department).filter(
            Department.code == code
        ).first()
    
    def get_employee_count(self, dept_id: int) -> int:
        """Get number of employees in department"""
        return self.session.query(Employee).filter(
            Employee.department_id == dept_id,
            Employee.is_active == True
        ).count()