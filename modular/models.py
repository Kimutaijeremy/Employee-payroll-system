from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), unique=True)
    description = Column(Text)
    budget = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="department")
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    base_salary = Column(Float, nullable=False)
    housing_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="role")
    
    def total_allowances(self):
        return (self.housing_allowance + self.transport_allowance + 
                self.medical_allowance + self.other_allowance)
    
    def gross_salary(self):
        return self.base_salary + self.total_allowances()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), unique=True, nullable=False, default=generate_uuid)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    date_joined = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    bank_account = Column(String(50))
    bank_name = Column(String(50))
    
    # Foreign keys
    role_id = Column(Integer, ForeignKey('roles.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Relationships
    role = relationship("Role", back_populates="employees")
    department = relationship("Department", back_populates="employees")
    payrolls = relationship("Payroll", back_populates="employee")
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.full_name()}', email='{self.email}')>"

class Payroll(Base):
    __tablename__ = 'payrolls'
    
    id = Column(Integer, primary_key=True)
    payroll_id = Column(String(50), unique=True, nullable=False, default=generate_uuid)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    
    # Salary components
    base_salary = Column(Float, nullable=False)
    housing_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowance = Column(Float, default=0.0)
    
    # Deductions
    tax_deduction = Column(Float, default=0.0)
    nhif_deduction = Column(Float, default=0.0)
    nssf_deduction = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    
    # Totals
    gross_salary = Column(Float, nullable=False)
    total_deductions = Column(Float, nullable=False)
    net_salary = Column(Float, nullable=False)
    
    # Status
    status = Column(String(20), default='pending')  # pending, approved, paid
    payment_date = Column(Date)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="payrolls")
    
    def salary_breakdown(self):
        return {
            'gross_salary': self.gross_salary,
            'total_deductions': self.total_deductions,
            'net_salary': self.net_salary,
            'allowances': {
                'housing': self.housing_allowance,
                'transport': self.transport_allowance,
                'medical': self.medical_allowance,
                'other': self.other_allowance
            },
            'deductions': {
                'tax': self.tax_deduction,
                'nhif': self.nhif_deduction,
                'nssf': self.nssf_deduction,
                'other': self.other_deductions
            }
        }
