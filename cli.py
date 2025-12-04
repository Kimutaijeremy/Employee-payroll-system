import click
from tabulate import tabulate
from datetime import datetime
from database import db
from services.employee_service import EmployeeService
from services.role_service import RoleService
from services.department_service import DepartmentService
from services.payroll_service import PayrollService
from models import Employee, Role, Department, Payroll
import csv
import sys

@click.group()
def cli():
    """Employee Payroll Management System"""
    pass

@cli.group()
def employee():
    """Employee management commands"""
    pass

@cli.group()
def role():
    """Role management commands"""
    pass

@cli.group()
def department():
    """Department management commands"""
    pass

@cli.group()
def payroll():
    """Payroll management commands"""
    pass

# Employee Commands
@employee.command()
@click.option('--first-name', prompt='First Name', help='Employee first name')
@click.option('--last-name', prompt='Last Name', help='Employee last name')
@click.option('--email', prompt='Email', help='Employee email')
@click.option('--phone', prompt='Phone', help='Employee phone number')
@click.option('--dob', prompt='Date of Birth (YYYY-MM-DD)', help='Date of birth')
@click.option('--join-date', prompt='Join Date (YYYY-MM-DD)', help='Date joined')
@click.option('--role-id', prompt='Role ID', type=int, help='Role ID')
@click.option('--dept-id', prompt='Department ID', type=int, help='Department ID')
def add(first_name, last_name, email, phone, dob, join_date, role_id, dept_id):
    """Add a new employee"""
    session = db.get_session()
    try:
        service = EmployeeService(session)
        
        employee_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'date_of_birth': datetime.strptime(dob, '%Y-%m-%d').date(),
            'date_joined': datetime.strptime(join_date, '%Y-%m-%d').date(),
            'role_id': role_id,
            'department_id': dept_id
        }
        
        employee = service.add_employee(employee_data)
        click.echo(click.style(f"✓ Employee added successfully!", fg='green'))
        click.echo(f"Employee ID: {employee.employee_id}")
        click.echo(f"Name: {employee.full_name()}")
        
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

@employee.command()
@click.option('--active-only/--all', default=True, help='Show only active employees')
def list(active_only):
    """List all employees"""
    session = db.get_session()
    try:
        service = EmployeeService(session)
        employees = service.list_employees(active_only=active_only)
        
        if not employees:
            click.echo("No employees found")
            return
        
        table_data = []
        for emp in employees:
            table_data.append([
                emp.employee_id,
                emp.full_name(),
                emp.email,
                emp.role.title if emp.role else 'N/A',
                emp.department.name if emp.department else 'N/A',
                'Active' if emp.is_active else 'Inactive'
            ])
        
        headers = ['ID', 'Name', 'Email', 'Role', 'Department', 'Status']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\nTotal employees: {len(employees)}")
        
    finally:
        db.close_session(session)

@employee.command()
@click.argument('employee_id')
def show(employee_id):
    """Show employee details"""
    session = db.get_session()
    try:
        service = EmployeeService(session)
        employee = service.get_employee(employee_id)
        
        if not employee:
            click.echo(click.style(f"✗ Employee not found", fg='red'))
            return
        
        click.echo(click.style("\n=== EMPLOYEE DETAILS ===", fg='blue', bold=True))
        click.echo(f"Employee ID: {employee.employee_id}")
        click.echo(f"Name: {employee.full_name()}")
        click.echo(f"Email: {employee.email}")
        click.echo(f"Phone: {employee.phone}")
        click.echo(f"Date of Birth: {employee.date_of_birth}")
        click.echo(f"Date Joined: {employee.date_joined}")
        click.echo(f"Status: {'Active' if employee.is_active else 'Inactive'}")
        
        if employee.role:
            click.echo(f"\nRole: {employee.role.title}")
            click.echo(f"Base Salary: {employee.role.base_salary}")
        
        if employee.department:
            click.echo(f"\nDepartment: {employee.department.name}")
            click.echo(f"Department Code: {employee.department.code}")
        
    finally:
        db.close_session(session)

@employee.command()
@click.argument('employee_id')
def deactivate(employee_id):
    """Deactivate an employee"""
    session = db.get_session()
    try:
        service = EmployeeService(session)
        if service.deactivate_employee(employee_id):
            click.echo(click.style(f"✓ Employee {employee_id} deactivated", fg='yellow'))
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

# Role Commands
@role.command()
@click.option('--title', prompt='Role Title', help='Role title')
@click.option('--base-salary', prompt='Base Salary', type=float, help='Base salary')
@click.option('--housing', default=0.0, help='Housing allowance')
@click.option('--transport', default=0.0, help='Transport allowance')
@click.option('--medical', default=0.0, help='Medical allowance')
@click.option('--other', default=0.0, help='Other allowance')
def add(title, base_salary, housing, transport, medical, other):
    """Add a new role"""
    session = db.get_session()
    try:
        service = RoleService(session)
        
        role_data = {
            'title': title,
            'base_salary': base_salary,
            'housing_allowance': housing,
            'transport_allowance': transport,
            'medical_allowance': medical,
            'other_allowance': other
        }
        
        role = service.create_role(role_data)
        click.echo(click.style(f"✓ Role added successfully!", fg='green'))
        click.echo(f"Role ID: {role.id}")
        click.echo(f"Title: {role.title}")
        click.echo(f"Gross Salary: {role.gross_salary()}")
        
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

@role.command()
def list():
    """List all roles"""
    session = db.get_session()
    try:
        service = RoleService(session)
        roles = service.list_roles()
        
        if not roles:
            click.echo("No roles found")
            return
        
        table_data = []
        for role in roles:
            table_data.append([
                role.id,
                role.title,
                role.base_salary,
                role.total_allowances(),
                role.gross_salary(),
                len(role.employees)
            ])
        
        headers = ['ID', 'Title', 'Base Salary', 'Allowances', 'Gross Salary', 'Employees']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    finally:
        db.close_session(session)

# Department Commands
@department.command()
@click.option('--name', prompt='Department Name', help='Department name')
@click.option('--code', prompt='Department Code', help='Department code')
@click.option('--budget', default=0.0, help='Department budget')
def add(name, code, budget):
    """Add a new department"""
    session = db.get_session()
    try:
        service = DepartmentService(session)
        
        dept_data = {
            'name': name,
            'code': code,
            'budget': budget
        }
        
        department = service.create_department(dept_data)
        click.echo(click.style(f"✓ Department added successfully!", fg='green'))
        click.echo(f"Department ID: {department.id}")
        click.echo(f"Name: {department.name}")
        click.echo(f"Code: {department.code}")
        
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

@department.command()
def list():
    """List all departments"""
    session = db.get_session()
    try:
        service = DepartmentService(session)
        departments = service.list_departments()
        
        if not departments:
            click.echo("No departments found")
            return
        
        table_data = []
        for dept in departments:
            employee_count = service.get_employee_count(dept.id)
            table_data.append([
                dept.id,
                dept.name,
                dept.code,
                employee_count,
                dept.budget
            ])
        
        headers = ['ID', 'Name', 'Code', 'Employees', 'Budget']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    finally:
        db.close_session(session)

# Payroll Commands
@payroll.command()
@click.option('--employee-id', prompt='Employee ID', help='Employee ID')
@click.option('--month', prompt='Month (1-12)', type=int, help='Month')
@click.option('--year', prompt='Year', type=int, help='Year')
@click.option('--additional-deductions', default=0.0, help='Additional deductions')
def generate(employee_id, month, year, additional_deductions):
    """Generate payroll for an employee"""
    session = db.get_session()
    try:
        service = PayrollService(session)
        payroll = service.generate_payroll(employee_id, month, year, additional_deductions)
        
        click.echo(click.style(f"\n✓ Payroll generated successfully!", fg='green'))
        click.echo(f"Payroll ID: {payroll.payroll_id}")
        click.echo(f"Employee: {payroll.employee.full_name()}")
        click.echo(f"Period: {month}/{year}")
        
        click.echo(click.style("\n=== SALARY BREAKDOWN ===", fg='blue'))
        click.echo(f"Gross Salary: {payroll.gross_salary:,.2f}")
        click.echo(f"Total Deductions: {payroll.total_deductions:,.2f}")
        click.echo(click.style(f"Net Salary: {payroll.net_salary:,.2f}", fg='green', bold=True))
        
        click.echo(click.style("\n=== DEDUCTIONS DETAIL ===", fg='yellow'))
        click.echo(f"Tax (PAYE): {payroll.tax_deduction:,.2f}")
        click.echo(f"NHIF: {payroll.nhif_deduction:,.2f}")
        click.echo(f"NSSF: {payroll.nssf_deduction:,.2f}")
        click.echo(f"Other: {payroll.other_deductions:,.2f}")
        
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

@payroll.command()
@click.option('--month', prompt='Month (1-12)', type=int, help='Month')
@click.option('--year', prompt='Year', type=int, help='Year')
def generate_all(month, year):
    """Generate payroll for all active employees"""
    session = db.get_session()
    try:
        click.confirm(f'Generate payroll for all active employees for {month}/{year}?', abort=True)
        
        service = PayrollService(session)
        payrolls = service.generate_bulk_payroll(month, year)
        
        click.echo(click.style(f"\n✓ Payroll generated for {len(payrolls)} employees", fg='green'))
        
        # Show summary
        summary = service.get_payroll_summary(month, year)
        if summary:
            click.echo(click.style("\n=== MONTHLY SUMMARY ===", fg='blue'))
            click.echo(f"Total Employees: {summary['total_employees']}")
            click.echo(f"Total Gross Salary: {summary['total_gross_salary']:,.2f}")
            click.echo(f"Total Deductions: {summary['total_deductions']:,.2f}")
            click.echo(f"Total Net Salary: {summary['total_net_salary']:,.2f}")
            click.echo(f"Average Net Salary: {summary['average_net_salary']:,.2f}")
        
    except click.Abort:
        click.echo("Operation cancelled")
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

@payroll.command()
@click.argument('employee_id')
def history(employee_id):
    """Show payroll history for an employee"""
    session = db.get_session()
    try:
        service = PayrollService(session)
        payrolls = service.get_employee_payroll_history(employee_id)
        
        if not payrolls:
            click.echo("No payroll history found")
            return
        
        table_data = []
        for payroll in payrolls:
            table_data.append([
                payroll.payroll_id,
                f"{payroll.month}/{payroll.year}",
                payroll.gross_salary,
                payroll.total_deductions,
                payroll.net_salary,
                payroll.status
            ])
        
        headers = ['Payroll ID', 'Period', 'Gross', 'Deductions', 'Net', 'Status']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    except ValueError as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))
    finally:
        db.close_session(session)

@payroll.command()
@click.option('--month', prompt='Month (1-12)', type=int, help='Month')
@click.option('--year', prompt='Year', type=int, help='Year')
def report(month, year):
    """Generate payroll report for a month"""
    session = db.get_session()
    try:
        service = PayrollService(session)
        
        # Monthly summary
        summary = service.get_payroll_summary(month, year)
        if not summary:
            click.echo(f"No payroll data for {month}/{year}")
            return
        
        click.echo(click.style(f"\n=== PAYROLL REPORT {month}/{year} ===", fg='blue', bold=True))
        click.echo(f"Total Employees: {summary['total_employees']}")
        click.echo(f"Total Gross Salary: {summary['total_gross_salary']:,.2f}")
        click.echo(f"Total Deductions: {summary['total_deductions']:,.2f}")
        click.echo(click.style(f"Total Net Salary: {summary['total_net_salary']:,.2f}", fg='green', bold=True))
        
        # Department summary
        dept_summary = service.get_department_summary(month, year)
        if dept_summary:
            click.echo(click.style("\n=== BY DEPARTMENT ===", fg='blue'))
            table_data = []
            for dept in dept_summary:
                table_data.append([
                    dept['department'],
                    dept['employee_count'],
                    f"{dept['total_gross']:,.2f}",
                    f"{dept['total_net']:,.2f}"
                ])
            
            headers = ['Department', 'Employees', 'Total Gross', 'Total Net']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Top earners
        top_earners = service.get_top_earners(month, year, 5)
        if top_earners:
            click.echo(click.style("\n=== TOP 5 EARNERS ===", fg='blue'))
            table_data = []
            for i, earner in enumerate(top_earners, 1):
                table_data.append([
                    i,
                    earner['name'],
                    earner['department'],
                    f"{earner['net_salary']:,.2f}"
                ])
            
            headers = ['Rank', 'Name', 'Department', 'Net Salary']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    finally:
        db.close_session(session)

@payroll.command()
@click.option('--month', prompt='Month (1-12)', type=int, help='Month')
@click.option('--year', prompt='Year', type=int, help='Year')
@click.option('--filename', default=None, help='CSV filename')
def export(month, year, filename):
    """Export payroll data to CSV"""
    session = db.get_session()
    try:
        service = PayrollService(session)
        payrolls = service.get_monthly_payrolls(month, year)
        
        if not payrolls:
            click.echo(f"No payroll data for {month}/{year}")
            return
        
        if not filename:
            filename = f"payroll_{month}_{year}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'Payroll ID', 'Employee ID', 'Employee Name', 'Department',
                'Month', 'Year', 'Base Salary', 'Housing Allowance',
                'Transport Allowance', 'Medical Allowance', 'Other Allowance',
                'Gross Salary', 'Tax', 'NHIF', 'NSSF', 'Other Deductions',
                'Total Deductions', 'Net Salary', 'Status'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for payroll in payrolls:
                writer.writerow({
                    'Payroll ID': payroll.payroll_id,
                    'Employee ID': payroll.employee.employee_id,
                    'Employee Name': payroll.employee.full_name(),
                    'Department': payroll.employee.department.name if payroll.employee.department else 'N/A',
                    'Month': payroll.month,
                    'Year': payroll.year,
                    'Base Salary': payroll.base_salary,
                    'Housing Allowance': payroll.housing_allowance,
                    'Transport Allowance': payroll.transport_allowance,
                    'Medical Allowance': payroll.medical_allowance,
                    'Other Allowance': payroll.other_allowance,
                    'Gross Salary': payroll.gross_salary,
                    'Tax': payroll.tax_deduction,
                    'NHIF': payroll.nhif_deduction,
                    'NSSF': payroll.nssf_deduction,
                    'Other Deductions': payroll.other_deductions,
                    'Total Deductions': payroll.total_deductions,
                    'Net Salary': payroll.net_salary,
                    'Status': payroll.status
                })
        
        click.echo(click.style(f"✓ Payroll data exported to {filename}", fg='green'))
        
    finally:
        db.close_session(session)

# Additional Utility Commands
@cli.command()
def init():
    """Initialize the database"""
    db.init_db()
    click.echo(click.style("✓ Database initialized successfully!", fg='green'))

@cli.command()
def dashboard():
    """Show system dashboard"""
    session = db.get_session()
    try:
        # Get counts
        employee_count = session.query(Employee).filter(Employee.is_active == True).count()
        role_count = session.query(Role).count()
        dept_count = session.query(Department).count()
        
        # Get latest payroll month
        latest_payroll = session.query(Payroll).order_by(
            Payroll.year.desc(), 
            Payroll.month.desc()
        ).first()
        
        click.echo(click.style("\n=== PAYROLL MANAGEMENT SYSTEM DASHBOARD ===", fg='cyan', bold=True))
        click.echo(f"\n📊 System Statistics:")
        click.echo(f"   • Active Employees: {employee_count}")
        click.echo(f"   • Roles: {role_count}")
        click.echo(f"   • Departments: {dept_count}")
        
        if latest_payroll:
            click.echo(f"   • Latest Payroll: {latest_payroll.month}/{latest_payroll.year}")
        
        # Quick actions
        click.echo(click.style("\n🚀 Quick Actions:", fg='green'))
        click.echo("   1. Add employee: python cli.py employee add")
        click.echo("   2. Generate payroll: python cli.py payroll generate")
        click.echo("   3. View report: python cli.py payroll report")
        click.echo("   4. Export data: python cli.py payroll export")
        
    finally:
        db.close_session(session)

if __name__ == '__main__':
    cli()