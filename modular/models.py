from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True)
    description = Column(String(500))
    budget = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="department")

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    base_salary = Column(Float, nullable=False)
    housing_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="role")
    
    def total_allowances(self):
        return self.housing_allowance + self.transport_allowance + self.medical_allowance + self.other_allowance
    
    def gross_salary(self):
        return self.base_salary + self.total_allowances()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    date_joined = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    bank_account = Column(String(50))
    bank_name = Column(String(50))
    
    role_id = Column(Integer, ForeignKey('roles.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    role = relationship("Role", back_populates="employees")
    department = relationship("Department", back_populates="employees")
    payrolls = relationship("Payroll", back_populates="employee")
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Payroll(Base):
    __tablename__ = 'payrolls'
    
    id = Column(Integer, primary_key=True)
    payroll_id = Column(String(50), unique=True, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    base_salary = Column(Float, nullable=False)
    housing_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowance = Column(Float, default=0.0)
    
    tax_deduction = Column(Float, default=0.0)
    nhif_deduction = Column(Float, default=0.0)
    nssf_deduction = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    
    gross_salary = Column(Float, nullable=False)
    total_deductions = Column(Float, nullable=False)
    net_salary = Column(Float, nullable=False)
    
    status = Column(String(20), default='generated')
    payment_date = Column(Date)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="payrolls")