"""
Pytest configuration and fixtures for Employee Payroll System tests
"""
import pytest
import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from models import Base, Employee, Department, Role, Payroll
from services.employee_service import EmployeeService
from services.role_service import RoleService
from services.department_service import DepartmentService
from services.payroll_service import PayrollService
from config import Config

@pytest.fixture(scope="session")
def test_database():
    """Create test database instance"""
    # Use in-memory SQLite for testing
    test_db = Database()
    test_db.engine = test_db.engine.execution_options(isolation_level="AUTOCOMMIT")
    
    # Create all tables
    Base.metadata.create_all(bind=test_db.engine)
    
    yield test_db
    
    # Clean up
    Base.metadata.drop_all(bind=test_db.engine)
    test_db.engine.dispose()

@pytest.fixture
def test_session(test_database):
    """Create a fresh database session for each test"""
    session = test_database.get_session()
    try:
        yield session
    finally:
        session.rollback()
        test_database.close_session(session)

@pytest.fixture
def sample_department(test_session):
    """Create a sample department"""
    dept = Department(
        name="Test Department",
        code="TEST",
        description="Test department for unit tests",
        budget=1000000.00
    )
    test_session.add(dept)
    test_session.commit()
    return dept

@pytest.fixture
def sample_role(test_session):
    """Create a sample role"""
    role = Role(
        title="Test Engineer",
        description="Test role for unit tests",
        base_salary=100000.00,
        housing_allowance=20000.00,
        transport_allowance=10000.00
    )
    test_session.add(role)
    test_session.commit()
    return role

@pytest.fixture
def sample_employee(test_session, sample_department, sample_role):
    """Create a sample employee"""
    employee = Employee(
        employee_id="TEST001",
        first_name="John",
        last_name="Doe",
        email="john.doe@testcompany.com",
        phone="254712345678",
        date_of_birth=date(1990, 1, 1),
        date_joined=date(2020, 1, 1),
        is_active=True,
        role_id=sample_role.id,
        department_id=sample_department.id,
        bank_account="ACC123456",
        bank_name="Test Bank"
    )
    test_session.add(employee)
    test_session.commit()
    return employee

@pytest.fixture
def sample_payroll(test_session, sample_employee):
    """Create a sample payroll"""
    payroll = Payroll(
        employee_id=sample_employee.id,
        month=12,
        year=2024,
        base_salary=100000.00,
        housing_allowance=20000.00,
        transport_allowance=10000.00,
        gross_salary=130000.00,
        tax_deduction=25000.00,
        nhif_deduction=1500.00,
        nssf_deduction=1080.00,
        other_deductions=500.00,
        total_deductions=28080.00,
        net_salary=101920.00,
        status="generated"
    )
    test_session.add(payroll)
    test_session.commit()
    return payroll

@pytest.fixture
def employee_service(test_session):
    """Create employee service instance"""
    return EmployeeService(test_session)

@pytest.fixture
def role_service(test_session):
    """Create role service instance"""
    return RoleService(test_session)

@pytest.fixture
def department_service(test_session):
    """Create department service instance"""
    return DepartmentService(test_session)

@pytest.fixture
def payroll_service(test_session):
    """Create payroll service instance"""
    return PayrollService(test_session)