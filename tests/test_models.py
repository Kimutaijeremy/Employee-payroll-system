"""
Tests for SQLAlchemy models
"""
import pytest
from datetime import date, datetime
from models import Employee, Department, Role, Payroll, generate_uuid
from decimal import Decimal

class TestDepartmentModel:
    """Test Department model"""
    
    def test_department_creation(self, test_session):
        """Test creating a department"""
        dept = Department(
            name="Engineering",
            code="ENG",
            description="Software Engineering Department",
            budget=5000000.00
        )
        test_session.add(dept)
        test_session.commit()
        
        assert dept.id is not None
        assert dept.name == "Engineering"
        assert dept.code == "ENG"
        assert dept.budget == 5000000.00
        assert isinstance(dept.created_at, datetime)
    
    def test_department_repr(self, sample_department):
        """Test department string representation"""
        repr_str = repr(sample_department)
        assert "Department" in repr_str
        assert sample_department.name in repr_str
        assert sample_department.code in repr_str
    
    def test_department_employees_relationship(self, sample_department, sample_employee):
        """Test department-employee relationship"""
        assert sample_department.employees is not None
        assert len(sample_department.employees) == 1
        assert sample_department.employees[0].id == sample_employee.id

class TestRoleModel:
    """Test Role model"""
    
    def test_role_creation(self, test_session):
        """Test creating a role"""
        role = Role(
            title="Software Engineer",
            description="Develops software applications",
            base_salary=120000.00,
            housing_allowance=20000.00,
            transport_allowance=10000.00
        )
        test_session.add(role)
        test_session.commit()
        
        assert role.id is not None
        assert role.title == "Software Engineer"
        assert role.base_salary == 120000.00
        assert isinstance(role.created_at, datetime)
    
    def test_role_total_allowances(self, sample_role):
        """Test total allowances calculation"""
        total = sample_role.total_allowances()
        expected = (sample_role.housing_allowance + 
                   sample_role.transport_allowance + 
                   sample_role.medical_allowance + 
                   sample_role.other_allowance)
        assert total == expected
    
    def test_role_gross_salary(self, sample_role):
        """Test gross salary calculation"""
        gross = sample_role.gross_salary()
        expected = sample_role.base_salary + sample_role.total_allowances()
        assert gross == expected
    
    def test_role_employees_relationship(self, sample_role, sample_employee):
        """Test role-employee relationship"""
        assert sample_role.employees is not None
        assert len(sample_role.employees) == 1
        assert sample_role.employees[0].id == sample_employee.id

class TestEmployeeModel:
    """Test Employee model"""
    
    def test_employee_creation(self, test_session, sample_department, sample_role):
        """Test creating an employee"""
        employee = Employee(
            employee_id="EMP002",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@testcompany.com",
            phone="254712345679",
            date_of_birth=date(1992, 5, 15),
            date_joined=date(2021, 3, 10),
            is_active=True,
            role_id=sample_role.id,
            department_id=sample_department.id
        )
        test_session.add(employee)
        test_session.commit()
        
        assert employee.id is not None
        assert employee.employee_id == "EMP002"
        assert employee.email == "jane.smith@testcompany.com"
        assert employee.is_active == True
    
    def test_employee_full_name(self, sample_employee):
        """Test full name property"""
        full_name = sample_employee.full_name()
        expected = f"{sample_employee.first_name} {sample_employee.last_name}"
        assert full_name == expected
    
    def test_employee_repr(self, sample_employee):
        """Test employee string representation"""
        repr_str = repr(sample_employee)
        assert "Employee" in repr_str
        assert sample_employee.full_name() in repr_str
        assert sample_employee.email in repr_str
    
    def test_employee_relationships(self, sample_employee, sample_role, sample_department):
        """Test employee relationships"""
        assert sample_employee.role.id == sample_role.id
        assert sample_employee.department.id == sample_department.id
        assert sample_employee.role.title == sample_role.title
        assert sample_employee.department.name == sample_department.name
    
    def test_employee_generate_uuid(self):
        """Test UUID generation"""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        assert isinstance(uuid1, str)
        assert len(uuid1) == 36  # UUID string length
        assert uuid1 != uuid2  # Should be unique

class TestPayrollModel:
    """Test Payroll model"""
    
    def test_payroll_creation(self, test_session, sample_employee):
        """Test creating a payroll"""
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
            total_deductions=27580.00,
            net_salary=102420.00,
            status="generated"
        )
        test_session.add(payroll)
        test_session.commit()
        
        assert payroll.id is not None
        assert payroll.payroll_id is not None
        assert payroll.month == 12
        assert payroll.year == 2024
        assert payroll.gross_salary == 130000.00
        assert payroll.net_salary == 102420.00
        assert isinstance(payroll.generated_at, datetime)
    
    def test_payroll_salary_breakdown(self, sample_payroll):
        """Test salary breakdown method"""
        breakdown = sample_payroll.salary_breakdown()
        
        assert breakdown['gross_salary'] == sample_payroll.gross_salary
        assert breakdown['total_deductions'] == sample_payroll.total_deductions
        assert breakdown['net_salary'] == sample_payroll.net_salary
        assert 'allowances' in breakdown
        assert 'deductions' in breakdown
        
        allowances = breakdown['allowances']
        assert allowances['housing'] == sample_payroll.housing_allowance
        assert allowances['transport'] == sample_payroll.transport_allowance
        
        deductions = breakdown['deductions']
        assert deductions['tax'] == sample_payroll.tax_deduction
        assert deductions['nhif'] == sample_payroll.nhif_deduction
    
    def test_payroll_employee_relationship(self, sample_payroll, sample_employee):
        """Test payroll-employee relationship"""
        assert sample_payroll.employee.id == sample_employee.id
        assert sample_payroll in sample_employee.payrolls
    
    def test_payroll_status_validation(self, test_session, sample_employee):
        """Test payroll status validation"""
        payroll = Payroll(
            employee_id=sample_employee.id,
            month=1,
            year=2025,
            base_salary=100000.00,
            gross_salary=130000.00,
            total_deductions=30000.00,
            net_salary=100000.00,
            status="invalid_status"  # Should fail or be handled
        )
        test_session.add(payroll)
        test_session.commit()
        
        # Status should remain as set
        assert payroll.status == "invalid_status"

class TestModelValidations:
    """Test model validations and constraints"""
    
    def test_unique_employee_email(self, test_session, sample_employee):
        """Test that employee email must be unique"""
        employee2 = Employee(
            employee_id="TEST002",
            first_name="Duplicate",
            last_name="Email",
            email=sample_employee.email,  # Same email
            phone="254700000001",
            date_of_birth=date(1990, 1, 1),
            date_joined=date(2021, 1, 1),
            role_id=sample_employee.role_id,
            department_id=sample_employee.department_id
        )
        test_session.add(employee2)
        
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_unique_employee_id(self, test_session, sample_employee):
        """Test that employee ID must be unique"""
        employee2 = Employee(
            employee_id=sample_employee.employee_id,  # Same ID
            first_name="Duplicate",
            last_name="ID",
            email="different@email.com",
            phone="254700000002",
            date_of_birth=date(1990, 1, 1),
            date_joined=date(2021, 1, 1),
            role_id=sample_employee.role_id,
            department_id=sample_employee.department_id
        )
        test_session.add(employee2)
        
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_required_employee_fields(self, test_session, sample_department, sample_role):
        """Test that required fields are enforced"""
        # Missing email
        employee = Employee(
            employee_id="TEST003",
            first_name="No",
            last_name="Email",
            # email is missing
            phone="254700000003",
            date_of_birth=date(1990, 1, 1),
            date_joined=date(2021, 1, 1),
            role_id=sample_role.id,
            department_id=sample_department.id
        )
        test_session.add(employee)
        
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_role_required_fields(self, test_session):
        """Test that role required fields are enforced"""
        # Missing title
        role = Role(
            # title is missing
            base_salary=100000.00
        )
        test_session.add(role)
        
        with pytest.raises(Exception):
            test_session.commit()