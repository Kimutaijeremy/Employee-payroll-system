import click
from tabulate import tabulate
from .database import init_db, get_session
from .services.employee_service import EmployeeService
from .services.role_service import RoleService
from .services.department_service import DepartmentService
from .services.payroll_service import PayrollService

@click.group()
def cli():
    """Employee Payroll Management System - Modular Version"""
    pass

@cli.command()
def init():
    """Initialize database"""
    init_db()

@cli.group()
def employee():
    """Manage employees"""
    pass

@employee.command()
@click.option('--first-name', prompt=True)
@click.option('--last-name', prompt=True)
@click.option('--email', prompt=True)
@click.option('--date-joined', prompt=True)
@click.option('--role-id', prompt=True, type=int)
@click.option('--dept-id', prompt=True, type=int)
def add(first_name, last_name, email, date_joined, role_id, dept_id):
    """Add new employee"""
    session = get_session()
    try:
        service = EmployeeService(session)
        employee = service.add_employee({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'date_joined': date_joined,
            'role_id': role_id,
            'department_id': dept_id
        })
        click.echo(f"Employee added: {employee.employee_id}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")
    finally:
        session.close()

@employee.command()
def list():
    """List employees"""
    session = get_session()
    try:
        service = EmployeeService(session)
        employees = service.list_employees()
        
        data = []
        for emp in employees:
            data.append([
                emp.employee_id,
                emp.full_name(),
                emp.email,
                emp.role.title if emp.role else 'N/A',
                'Active' if emp.is_active else 'Inactive'
            ])
        
        click.echo(tabulate(data, headers=['ID', 'Name', 'Email', 'Role', 'Status']))
    finally:
        session.close()

# Similar commands for role, department, and payroll...

if __name__ == '__main__':
    cli()