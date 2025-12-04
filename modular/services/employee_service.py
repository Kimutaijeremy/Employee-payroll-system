from sqlalchemy.exc import IntegrityError
from ..models import Employee
import re

class EmployeeService:
    def __init__(self, session):
        self.session = session
    
    def add_employee(self, data):
        # Generate employee ID
        import datetime
        timestamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        employee_id = f"EMP{timestamp}"
        
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get('email', '')):
            raise ValueError("Invalid email format")
        
        employee = Employee(
            employee_id=employee_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            date_joined=data['date_joined'],
            role_id=data['role_id'],
            department_id=data['department_id'],
            is_active=True
        )
        
        try:
            self.session.add(employee)
            self.session.commit()
            return employee
        except IntegrityError as e:
            self.session.rollback()
            if "email" in str(e):
                raise ValueError("Email already exists")
            raise ValueError(f"Database error: {str(e)}")
    
    def list_employees(self, active_only=True):
        query = self.session.query(Employee)
        if active_only:
            query = query.filter(Employee.is_active == True)
        return query.all()
    
    def get_employee(self, employee_id):
        return self.session.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()