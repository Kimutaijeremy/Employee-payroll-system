import pytest
from modular.database import init_db, get_session
from modular.models import Department, Role, Employee
from modular.services.department_service import DepartmentService
from modular.services.role_service import RoleService
from modular.services.employee_service import EmployeeService

def test_database_connection():
    """Test database connection"""
    session = get_session()
    try:
        # Test that session works
        assert session is not None
    finally:
        session.close()

def test_create_department():
    """Test creating a department"""
    session = get_session()
    try:
        service = DepartmentService(session)
        dept = service.add_department({
            'name': 'Test Department',
            'code': 'TEST',
            'budget': 100000
        })
        assert dept.id is not None
        assert dept.name == 'Test Department'
    finally:
        session.rollback()
        session.close()

def test_create_role():
    """Test creating a role"""
    session = get_session()
    try:
        service = RoleService(session)
        role = service.add_role({
            'title': 'Test Role',
            'base_salary': 50000,
            'housing_allowance': 10000
        })
        assert role.id is not None
        assert role.title == 'Test Role'
        assert role.base_salary == 50000
    finally:
        session.rollback()
        session.close()