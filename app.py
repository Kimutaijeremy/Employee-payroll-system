#!/usr/bin/env python3
"""
Employee Payroll Management System - Complete Simplified Version
Main entry point with all features in one file.
"""
import sys
import sqlite3
from datetime import datetime, date
import csv
from typing import List, Dict, Optional

# Database setup
DB_FILE = "payroll.db"

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Departments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE,
            budget REAL DEFAULT 0,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            base_salary REAL NOT NULL,
            housing_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            medical_allowance REAL DEFAULT 0,
            other_allowance REAL DEFAULT 0,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            date_of_birth DATE,
            date_joined DATE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            role_id INTEGER,
            department_id INTEGER,
            bank_account TEXT,
            bank_name TEXT,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    ''')
    
    # Payroll table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payrolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_id TEXT UNIQUE NOT NULL,
            employee_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            base_salary REAL NOT NULL,
            housing_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            medical_allowance REAL DEFAULT 0,
            other_allowance REAL DEFAULT 0,
            gross_salary REAL NOT NULL,
            tax_deduction REAL NOT NULL,
            nhif_deduction REAL NOT NULL,
            nssf_deduction REAL NOT NULL,
            other_deductions REAL DEFAULT 0,
            total_deductions REAL NOT NULL,
            net_salary REAL NOT NULL,
            status TEXT DEFAULT 'generated',
            payment_date DATE,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

class PayrollCalculator:
    """Handle payroll calculations"""
    
    # Kenya tax brackets 2024
    TAX_BRACKETS = [
        (0, 24000, 0.10),
        (24001, 32333, 0.25),
        (32334, 500000, 0.30),
        (500001, 800000, 0.325),
        (800001, float('inf'), 0.35)
    ]
    
    # NHIF rates
    NHIF_RATES = [
        (0, 5999, 150),
        (6000, 7999, 300),
        (8000, 11999, 400),
        (12000, 14999, 500),
        (15000, 19999, 600),
        (20000, 24999, 750),
        (25000, 29999, 850),
        (30000, 34999, 900),
        (35000, 39999, 950),
        (40000, 44999, 1000),
        (45000, 49999, 1100),
        (50000, 59999, 1200),
        (60000, 69999, 1300),
        (70000, 79999, 1400),
        (80000, 89999, 1500),
        (90000, 99999, 1600),
        (100000, float('inf'), 1700)
    ]
    
    NSSF_RATE = 0.06
    NSSF_LIMIT = 18000
    
    @staticmethod
    def calculate_tax(gross_salary: float) -> float:
        """Calculate PAYE tax using progressive brackets"""
        tax = 0.0
        remaining = gross_salary
        
        for lower, upper, rate in PayrollCalculator.TAX_BRACKETS:
            if remaining <= 0:
                break
            
            if upper == float('inf'):
                bracket_amount = remaining
            else:
                bracket_amount = min(upper - lower + 1, remaining)
            
            if bracket_amount > 0:
                tax += bracket_amount * rate
                remaining -= bracket_amount
        
        return round(tax, 2)
    
    @staticmethod
    def calculate_nhif(gross_salary: float) -> float:
        """Calculate NHIF contribution"""
        for lower, upper, amount in PayrollCalculator.NHIF_RATES:
            if lower <= gross_salary <= upper:
                return float(amount)
        return 1700.0
    
    @staticmethod
    def calculate_nssf(gross_salary: float) -> float:
        """Calculate NSSF contribution"""
        pensionable = min(gross_salary, PayrollCalculator.NSSF_LIMIT)
        return round(pensionable * PayrollCalculator.NSSF_RATE, 2)

class DatabaseManager:
    """Handle all database operations"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def execute(self, query: str, params: tuple = ()):
        """Execute SQL query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch single row"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def insert_and_get_id(self, query: str, params: tuple = ()):
        """Insert and return last ID"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.lastrowid

class DepartmentService:
    """Department management"""
    
    @staticmethod
    def create(name: str, code: str = None, budget: float = 0, description: str = "") -> int:
        """Create new department"""
        with DatabaseManager() as db:
            if not code:
                code = name[:3].upper()
            
            try:
                db.execute(
                    "INSERT INTO departments (name, code, budget, description) VALUES (?, ?, ?, ?)",
                    (name, code, budget, description)
                )
                print(f"✓ Department '{name}' created")
                return db.fetch_one("SELECT last_insert_rowid()")[0]
            except sqlite3.IntegrityError as e:
                if "name" in str(e):
                    print(f"✗ Department name '{name}' already exists")
                elif "code" in str(e):
                    print(f"✗ Department code '{code}' already exists")
                else:
                    print(f"✗ Database error: {str(e)}")
                return None
    
    @staticmethod
    def list_all():
        """List all departments"""
        with DatabaseManager() as db:
            depts = db.fetch_all("""
                SELECT d.*, 
                       COUNT(CASE WHEN e.is_active = 1 THEN e.id END) as active_employees,
                       COUNT(e.id) as total_employees
                FROM departments d
                LEFT JOIN employees e ON d.id = e.department_id
                GROUP BY d.id
                ORDER BY d.name
            """)
            
            if not depts:
                print("No departments found")
                return
            
            print("\n" + "="*70)
            print("DEPARTMENTS")
            print("="*70)
            print(f"{'ID':<4} {'Code':<6} {'Name':<20} {'Active':<8} {'Total':<8} {'Budget':<12}")
            print("-"*70)
            for dept in depts:
                print(f"{dept['id']:<4} {dept['code']:<6} {dept['name']:<20} "
                      f"{dept['active_employees']:<8} {dept['total_employees']:<8} "
                      f"KES {dept['budget']:,.0f}")
            print(f"\nTotal: {len(depts)} departments")
    
    @staticmethod
    def update(dept_id: int, **kwargs):
        """Update department details"""
        with DatabaseManager() as db:
            if not kwargs:
                print("No updates provided")
                return False
            
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values())
            values.append(dept_id)
            
            result = db.execute(
                f"UPDATE departments SET {set_clause} WHERE id = ?",
                tuple(values)
            )
            
            if result.rowcount > 0:
                print(f"✓ Department {dept_id} updated")
                return True
            else:
                print(f"✗ Department {dept_id} not found")
                return False
    
    @staticmethod
    def delete(dept_id: int):
        """Delete department (only if no employees)"""
        with DatabaseManager() as db:
            # Check if department has employees
            emp_count = db.fetch_one(
                "SELECT COUNT(*) as count FROM employees WHERE department_id = ?",
                (dept_id,)
            )
            
            if emp_count['count'] > 0:
                print(f"✗ Cannot delete department with {emp_count['count']} employees")
                return False
            
            result = db.execute(
                "DELETE FROM departments WHERE id = ?",
                (dept_id,)
            )
            
            if result.rowcount > 0:
                print(f"✓ Department {dept_id} deleted")
                return True
            else:
                print(f"✗ Department {dept_id} not found")
                return False

class RoleService:
    """Role and pay structure management"""
    
    @staticmethod
    def create(title: str, base_salary: float, housing: float = 0, 
               transport: float = 0, medical: float = 0, other: float = 0,
               description: str = "") -> int:
        """Create new role"""
        with DatabaseManager() as db:
            try:
                db.execute(
                    """INSERT INTO roles (title, base_salary, housing_allowance, 
                       transport_allowance, medical_allowance, other_allowance, description) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (title, base_salary, housing, transport, medical, other, description)
                )
                
                # Calculate total allowances and gross salary
                allowances = housing + transport + medical + other
                gross_salary = base_salary + allowances
                
                print(f"✓ Role '{title}' created")
                print(f"  Base Salary: KES {base_salary:,.0f}")
                print(f"  Total Allowances: KES {allowances:,.0f}")
                print(f"  Gross Salary: KES {gross_salary:,.0f}")
                
                return db.fetch_one("SELECT last_insert_rowid()")[0]
            except sqlite3.IntegrityError:
                print(f"✗ Role '{title}' already exists")
                return None
    
    @staticmethod
    def list_all():
        """List all roles"""
        with DatabaseManager() as db:
            roles = db.fetch_all("""
                SELECT r.*, 
                       COUNT(CASE WHEN e.is_active = 1 THEN e.id END) as active_employees,
                       COUNT(e.id) as total_employees
                FROM roles r
                LEFT JOIN employees e ON r.id = e.role_id
                GROUP BY r.id
                ORDER BY r.title
            """)
            
            if not roles:
                print("No roles found")
                return
            
            print("\n" + "="*90)
            print("ROLES")
            print("="*90)
            print(f"{'ID':<4} {'Title':<25} {'Base Salary':<15} {'Allowances':<15} {'Employees':<10}")
            print("-"*90)
            for role in roles:
                allowances = (role['housing_allowance'] + role['transport_allowance'] + 
                            role['medical_allowance'] + role['other_allowance'])
                gross = role['base_salary'] + allowances
                print(f"{role['id']:<4} {role['title']:<25} "
                      f"KES {role['base_salary']:<13,.0f} "
                      f"KES {allowances:<13,.0f} "
                      f"{role['active_employees']:<10}")
            print(f"\nTotal: {len(roles)} roles")
    
    @staticmethod
    def update(role_id: int, **kwargs):
        """Update role details"""
        with DatabaseManager() as db:
            if not kwargs:
                print("No updates provided")
                return False
            
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values())
            values.append(role_id)
            
            result = db.execute(
                f"UPDATE roles SET {set_clause} WHERE id = ?",
                tuple(values)
            )
            
            if result.rowcount > 0:
                print(f"✓ Role {role_id} updated")
                return True
            else:
                print(f"✗ Role {role_id} not found")
                return False
    
    @staticmethod
    def delete(role_id: int):
        """Delete role (only if no employees)"""
        with DatabaseManager() as db:
            # Check if role has employees
            emp_count = db.fetch_one(
                "SELECT COUNT(*) as count FROM employees WHERE role_id = ?",
                (role_id,)
            )
            
            if emp_count['count'] > 0:
                print(f"✗ Cannot delete role with {emp_count['count']} employees")
                return False
            
            result = db.execute(
                "DELETE FROM roles WHERE id = ?",
                (role_id,)
            )
            
            if result.rowcount > 0:
                print(f"✓ Role {role_id} deleted")
                return True
            else:
                print(f"✗ Role {role_id} not found")
                return False

class EmployeeService:
    """Employee management"""
    
    @staticmethod
    def add(first_name: str, last_name: str, email: str, date_joined: str,
            role_id: int, department_id: int, phone: str = "", 
            dob: str = None, bank_account: str = "", bank_name: str = "") -> str:
        """Add new employee"""
        with DatabaseManager() as db:
            # Generate unique employee ID
            timestamp = datetime.now().strftime('%y%m%d%H%M%S')
            random_part = str(hash(email) % 10000).zfill(4)
            employee_id = f"EMP{timestamp}{random_part}"
            
            try:
                db.execute(
                    """INSERT INTO employees 
                       (employee_id, first_name, last_name, email, phone, date_of_birth, 
                       date_joined, role_id, department_id, bank_account, bank_name, is_active) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                    (employee_id, first_name, last_name, email, phone, dob, date_joined,
                     role_id, department_id, bank_account, bank_name)
                )
                print(f"✓ Employee {first_name} {last_name} added")
                print(f"  Employee ID: {employee_id}")
                print(f"  Email: {email}")
                return employee_id
            except sqlite3.IntegrityError as e:
                if "email" in str(e):
                    print(f"✗ Email '{email}' already exists")
                elif "employee_id" in str(e):
                    print(f"✗ Employee ID generation failed, try again")
                else:
                    print(f"✗ Database error: {str(e)}")
                return None
    
    @staticmethod
    def list_all(active_only: bool = True, department_id: int = None, role_id: int = None):
        """List all employees with filters"""
        with DatabaseManager() as db:
            where_clauses = []
            params = []
            
            if active_only:
                where_clauses.append("e.is_active = 1")
            
            if department_id:
                where_clauses.append("e.department_id = ?")
                params.append(department_id)
            
            if role_id:
                where_clauses.append("e.role_id = ?")
                params.append(role_id)
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            employees = db.fetch_all(f"""
                SELECT e.*, r.title as role_title, d.name as department_name,
                       d.code as department_code
                FROM employees e
                LEFT JOIN roles r ON e.role_id = r.id
                LEFT JOIN departments d ON e.department_id = d.id
                {where_clause}
                ORDER BY e.last_name, e.first_name
            """, tuple(params))
            
            if not employees:
                print("No employees found")
                return
            
            print("\n" + "="*110)
            print("EMPLOYEES")
            print("="*110)
            print(f"{'ID':<12} {'Name':<25} {'Email':<25} {'Role':<20} {'Department':<15} {'Status':<8}")
            print("-"*110)
            for emp in employees:
                status = "Active" if emp['is_active'] else "Inactive"
                print(f"{emp['employee_id']:<12} "
                      f"{emp['first_name']} {emp['last_name']:<20} "
                      f"{emp['email']:<25} "
                      f"{emp['role_title'] or 'N/A':<20} "
                      f"{emp['department_name'] or 'N/A':<15} "
                      f"{status:<8}")
            
            active_count = sum(1 for e in employees if e['is_active'])
            print(f"\nTotal: {len(employees)} employees ({active_count} active)")
    
    @staticmethod
    def get_details(employee_id: str):
        """Get employee details"""
        with DatabaseManager() as db:
            emp = db.fetch_one("""
                SELECT e.*, r.title as role_title, r.base_salary, 
                       r.housing_allowance, r.transport_allowance,
                       r.medical_allowance, r.other_allowance,
                       d.name as department_name, d.code as department_code
                FROM employees e
                LEFT JOIN roles r ON e.role_id = r.id
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE e.employee_id = ?
            """, (employee_id,))
            
            if not emp:
                print(f"✗ Employee {employee_id} not found")
                return
            
            print("\n" + "="*60)
            print("EMPLOYEE DETAILS")
            print("="*60)
            print(f"Employee ID: {emp['employee_id']}")
            print(f"Name: {emp['first_name']} {emp['last_name']}")
            print(f"Email: {emp['email']}")
            print(f"Phone: {emp['phone'] or 'Not provided'}")
            if emp['date_of_birth']:
                print(f"Date of Birth: {emp['date_of_birth']}")
            print(f"Date Joined: {emp['date_joined']}")
            print(f"Status: {'Active' if emp['is_active'] else 'Inactive'}")
            
            if emp['bank_account']:
                print(f"Bank: {emp['bank_name'] or ''} - {emp['bank_account']}")
            
            print(f"\nRole: {emp['role_title'] or 'Not assigned'}")
            if emp['role_title']:
                base = emp['base_salary']
                housing = emp['housing_allowance']
                transport = emp['transport_allowance']
                medical = emp['medical_allowance']
                other = emp['other_allowance']
                total_allowances = housing + transport + medical + other
                gross = base + total_allowances
                
                print(f"  Base Salary:     KES {base:,.0f}")
                print(f"  Allowances:      KES {total_allowances:,.0f}")
                print(f"    - Housing:     KES {housing:,.0f}")
                print(f"    - Transport:   KES {transport:,.0f}")
                print(f"    - Medical:     KES {medical:,.0f}")
                print(f"    - Other:       KES {other:,.0f}")
                print(f"  Gross Salary:    KES {gross:,.0f}")
            
            print(f"\nDepartment: {emp['department_name'] or 'Not assigned'} "
                  f"({emp['department_code'] or 'N/A'})")
    
    @staticmethod
    def update(employee_id: str, **kwargs):
        """Update employee details"""
        with DatabaseManager() as db:
            if not kwargs:
                print("No updates provided")
                return False
            
            # Don't allow updating employee_id or email (should be immutable)
            if 'employee_id' in kwargs or 'email' in kwargs:
                print("✗ Cannot update employee ID or email")
                return False
            
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values())
            values.append(employee_id)
            
            result = db.execute(
                f"UPDATE employees SET {set_clause} WHERE employee_id = ?",
                tuple(values)
            )
            
            if result.rowcount > 0:
                print(f"✓ Employee {employee_id} updated")
                return True
            else:
                print(f"✗ Employee {employee_id} not found")
                return False
    
    @staticmethod
    def deactivate(employee_id: str):
        """Deactivate employee"""
        with DatabaseManager() as db:
            result = db.execute(
                "UPDATE employees SET is_active = 0 WHERE employee_id = ?",
                (employee_id,)
            )
            if result.rowcount > 0:
                print(f"✓ Employee {employee_id} deactivated")
                return True
            else:
                print(f"✗ Employee {employee_id} not found")
                return False
    
    @staticmethod
    def activate(employee_id: str):
        """Activate employee"""
        with DatabaseManager() as db:
            result = db.execute(
                "UPDATE employees SET is_active = 1 WHERE employee_id = ?",
                (employee_id,)
            )
            if result.rowcount > 0:
                print(f"✓ Employee {employee_id} activated")
                return True
            else:
                print(f"✗ Employee {employee_id} not found")
                return False
    
    @staticmethod
    def search(search_term: str):
        """Search employees by name or email"""
        with DatabaseManager() as db:
            employees = db.fetch_all("""
                SELECT e.*, r.title as role_title, d.name as department_name
                FROM employees e
                LEFT JOIN roles r ON e.role_id = r.id
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE e.first_name LIKE ? OR e.last_name LIKE ? OR e.email LIKE ?
                ORDER BY e.last_name, e.first_name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            if not employees:
                print(f"No employees found matching '{search_term}'")
                return
            
            print(f"\nSearch results for '{search_term}':")
            print("-" * 80)
            for emp in employees:
                status = "Active" if emp['is_active'] else "Inactive"
                print(f"{emp['employee_id']} - {emp['first_name']} {emp['last_name']} "
                      f"({emp['email']}) - {emp['role_title']} - {status}")
            
            print(f"\nFound {len(employees)} employees")

class PayrollService:
    """Payroll generation and management"""
    
    @staticmethod
    def generate(employee_id: str, month: int, year: int, other_deductions: float = 0):
        """Generate payroll for employee"""
        with DatabaseManager() as db:
            # Get employee with role details
            emp = db.fetch_one("""
                SELECT e.*, r.base_salary, r.housing_allowance, 
                       r.transport_allowance, r.medical_allowance, r.other_allowance
                FROM employees e
                LEFT JOIN roles r ON e.role_id = r.id
                WHERE e.employee_id = ? AND e.is_active = 1
            """, (employee_id,))
            
            if not emp:
                print(f"✗ Employee {employee_id} not found or inactive")
                return None
            
            if not emp['role_id']:
                print(f"✗ Employee {employee_id} has no role assigned")
                return None
            
            # Check if payroll already exists for this period
            existing = db.fetch_one("""
                SELECT 1 FROM payrolls p
                JOIN employees e ON p.employee_id = e.id
                WHERE e.employee_id = ? AND p.month = ? AND p.year = ?
            """, (employee_id, month, year))
            
            if existing:
                print(f"✗ Payroll already generated for {employee_id} in {month}/{year}")
                return None
            
            # Calculate salary components
            base = emp['base_salary']
            housing = emp['housing_allowance']
            transport = emp['transport_allowance']
            medical = emp['medical_allowance']
            other = emp['other_allowance']
            gross = base + housing + transport + medical + other
            
            # Calculate deductions
            tax = PayrollCalculator.calculate_tax(gross)
            nhif = PayrollCalculator.calculate_nhif(gross)
            nssf = PayrollCalculator.calculate_nssf(gross)
            total_deductions = tax + nhif + nssf + other_deductions
            net = gross - total_deductions
            
            # Generate payroll ID
            payroll_id = f"PAY{year:04d}{month:02d}{emp['id']:06d}"
            
            try:
                db.execute("""
                    INSERT INTO payrolls 
                    (payroll_id, employee_id, month, year, base_salary, 
                     housing_allowance, transport_allowance, medical_allowance, other_allowance,
                     gross_salary, tax_deduction, nhif_deduction, nssf_deduction, 
                     other_deductions, total_deductions, net_salary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (payroll_id, emp['id'], month, year, base, housing, 
                      transport, medical, other, gross, tax, nhif, nssf, 
                      other_deductions, total_deductions, net))
                
                print(f"\n✓ Payroll generated for {emp['first_name']} {emp['last_name']}")
                print(f"  Payroll ID: {payroll_id}")
                print(f"  Period: {month}/{year}")
                
                PayrollService._print_payroll_summary(base, housing, transport, medical, other,
                                                     gross, tax, nhif, nssf, other_deductions,
                                                     total_deductions, net)
                
                return payroll_id
            except sqlite3.IntegrityError:
                print(f"✗ Error generating payroll")
                return None
    
    @staticmethod
    def _print_payroll_summary(base, housing, transport, medical, other,
                              gross, tax, nhif, nssf, other_deductions,
                              total_deductions, net):
        """Print payroll summary"""
        print(f"\n  Gross Salary:    KES {gross:,.2f}")
        print(f"  Total Deductions: KES {total_deductions:,.2f}")
        print(f"  Net Salary:       KES {net:,.2f}")
        print(f"\n  Salary Components:")
        print(f"    - Base Salary:    KES {base:,.2f}")
        if housing > 0: print(f"    - Housing:        KES {housing:,.2f}")
        if transport > 0: print(f"    - Transport:      KES {transport:,.2f}")
        if medical > 0: print(f"    - Medical:        KES {medical:,.2f}")
        if other > 0: print(f"    - Other:          KES {other:,.2f}")
        print(f"\n  Deductions:")
        print(f"    - Tax (PAYE):     KES {tax:,.2f}")
        print(f"    - NHIF:           KES {nhif:,.2f}")
        print(f"    - NSSF:           KES {nssf:,.2f}")
        if other_deductions > 0:
            print(f"    - Other:          KES {other_deductions:,.2f}")
    
    @staticmethod
    def generate_all(month: int, year: int):
        """Generate payroll for all active employees"""
        with DatabaseManager() as db:
            employees = db.fetch_all("""
                SELECT e.employee_id, e.first_name, e.last_name FROM employees e 
                WHERE e.is_active = 1 AND e.role_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM payrolls p 
                    WHERE p.employee_id = e.id AND p.month = ? AND p.year = ?
                )
            """, (month, year))
            
            if not employees:
                print(f"✗ No active employees or payroll already generated for {month}/{year}")
                return 0
            
            print(f"Generating payroll for {len(employees)} employees...\n")
            count = 0
            payroll_ids = []
            
            for emp in employees:
                print(f"Processing {emp['first_name']} {emp['last_name']}...")
                payroll_id = PayrollService.generate(emp['employee_id'], month, year)
                if payroll_id:
                    count += 1
                    payroll_ids.append(payroll_id)
                print("-" * 60)
            
            if count > 0:
                print(f"\n✓ Generated {count} payrolls successfully")
                PayrollService.monthly_summary(month, year)
            else:
                print("\n✗ No payrolls generated")
            
            return count
    
    @staticmethod
    def monthly_summary(month: int, year: int):
        """Show monthly payroll summary"""
        with DatabaseManager() as db:
            summary = db.fetch_one("""
                SELECT 
                    COUNT(*) as employee_count,
                    SUM(gross_salary) as total_gross,
                    SUM(total_deductions) as total_deductions,
                    SUM(net_salary) as total_net,
                    AVG(net_salary) as avg_net
                FROM payrolls 
                WHERE month = ? AND year = ?
            """, (month, year))
            
            if summary and summary['employee_count'] > 0:
                print(f"\n" + "="*60)
                print(f"MONTHLY SUMMARY {month}/{year}")
                print("="*60)
                print(f"Total Employees:     {summary['employee_count']}")
                print(f"Total Gross Salary:  KES {summary['total_gross']:,.2f}")
                print(f"Total Deductions:    KES {summary['total_deductions']:,.2f}")
                print(f"Total Net Salary:    KES {summary['total_net']:,.2f}")
                print(f"Average Net Salary:  KES {summary['avg_net']:,.2f}")
                
                # Department breakdown
                dept_summary = db.fetch_all("""
                    SELECT d.name, 
                           COUNT(p.id) as employee_count,
                           SUM(p.gross_salary) as total_gross,
                           SUM(p.net_salary) as total_net
                    FROM payrolls p
                    JOIN employees e ON p.employee_id = e.id
                    LEFT JOIN departments d ON e.department_id = d.id
                    WHERE p.month = ? AND p.year = ?
                    GROUP BY d.id
                    ORDER BY d.name
                """, (month, year))
                
                if dept_summary and len(dept_summary) > 0:
                    print(f"\nDepartment Breakdown:")
                    print("-" * 60)
                    for dept in dept_summary:
                        dept_name = dept['name'] or 'Unassigned'
                        print(f"{dept_name:<20} "
                              f"{dept['employee_count']:<8} "
                              f"KES {dept['total_net']:,.0f}")
            else:
                print(f"✗ No payroll data for {month}/{year}")
    
    @staticmethod
    def employee_history(employee_id: str):
        """Show payroll history for employee"""
        with DatabaseManager() as db:
            history = db.fetch_all("""
                SELECT p.* FROM payrolls p
                JOIN employees e ON p.employee_id = e.id
                WHERE e.employee_id = ?
                ORDER BY p.year DESC, p.month DESC
            """, (employee_id,))
            
            if not history:
                print(f"✗ No payroll history for {employee_id}")
                return
            
            emp = db.fetch_one(
                "SELECT first_name, last_name FROM employees WHERE employee_id = ?",
                (employee_id,)
            )
            
            print(f"\n" + "="*70)
            print(f"PAYROLL HISTORY for {emp['first_name']} {emp['last_name']}")
            print("="*70)
            print(f"{'Period':<10} {'Gross':<15} {'Deductions':<15} {'Net':<15} {'Status':<10}")
            print("-"*70)
            for pay in history:
                period = f"{pay['month']:02d}/{pay['year']}"
                print(f"{period:<10} "
                      f"KES {pay['gross_salary']:<13,.0f} "
                      f"KES {pay['total_deductions']:<13,.0f} "
                      f"KES {pay['net_salary']:<13,.0f} "
                      f"{pay['status']:<10}")
            
            total_gross = sum(p['gross_salary'] for p in history)
            total_net = sum(p['net_salary'] for p in history)
            print("-"*70)
            print(f"Total: {len(history)} payrolls | "
                  f"Total Gross: KES {total_gross:,.0f} | "
                  f"Total Net: KES {total_net:,.0f}")
    
    @staticmethod
    def approve_payroll(payroll_id: str):
        """Approve a payroll"""
        with DatabaseManager() as db:
            result = db.execute(
                "UPDATE payrolls SET status = 'approved' WHERE payroll_id = ?",
                (payroll_id,)
            )
            if result.rowcount > 0:
                print(f"✓ Payroll {payroll_id} approved")
                return True
            else:
                print(f"✗ Payroll {payroll_id} not found")
                return False
    
    @staticmethod
    def mark_as_paid(payroll_id: str, payment_date: str = None):
        """Mark payroll as paid"""
        with DatabaseManager() as db:
            if not payment_date:
                payment_date = date.today().isoformat()
            
            result = db.execute(
                "UPDATE payrolls SET status = 'paid', payment_date = ? WHERE payroll_id = ?",
                (payment_date, payroll_id)
            )
            if result.rowcount > 0:
                print(f"✓ Payroll {payroll_id} marked as paid on {payment_date}")
                return True
            else:
                print(f"✗ Payroll {payroll_id} not found")
                return False
    
    @staticmethod
    def export_csv(month: int, year: int, filename: str = None):
        """Export payroll data to CSV"""
        if not filename:
            filename = f"payroll_{year}_{month:02d}.csv"
        
        with DatabaseManager() as db:
            data = db.fetch_all("""
                SELECT 
                    p.payroll_id,
                    e.employee_id,
                    e.first_name || ' ' || e.last_name as employee_name,
                    d.name as department,
                    p.month,
                    p.year,
                    p.base_salary,
                    p.housing_allowance,
                    p.transport_allowance,
                    p.medical_allowance,
                    p.other_allowance,
                    p.gross_salary,
                    p.tax_deduction,
                    p.nhif_deduction,
                    p.nssf_deduction,
                    p.other_deductions,
                    p.total_deductions,
                    p.net_salary,
                    p.status,
                    p.payment_date
                FROM payrolls p
                JOIN employees e ON p.employee_id = e.id
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE p.month = ? AND p.year = ?
                ORDER BY e.last_name, e.first_name
            """, (month, year))
            
            if not data:
                print(f"✗ No payroll data for {month}/{year}")
                return
            
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['payroll_id', 'employee_id', 'employee_name', 'department',
                            'month', 'year', 'base_salary', 'housing_allowance',
                            'transport_allowance', 'medical_allowance', 'other_allowance',
                            'gross_salary', 'tax_deduction', 'nhif_deduction',
                            'nssf_deduction', 'other_deductions', 'total_deductions',
                            'net_salary', 'status', 'payment_date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    writer.writerow(dict(row))
            
            print(f"✓ Payroll data exported to {filename}")
            print(f"  Records exported: {len(data)}")

class PayrollCLI:
    """Command-line interface"""
    
    @staticmethod
    def show_menu():
        """Display main menu"""
        print("\n" + "="*60)
        print("EMPLOYEE PAYROLL MANAGEMENT SYSTEM")
        print("="*60)
        print("\nMain Menu:")
        print(" 1. Initialize Database")
        
        print("\nDepartment Management:")
        print(" 2. Add Department")
        print(" 3. List Departments")
        print(" 4. Update Department")
        print(" 5. Delete Department")
        
        print("\nRole Management:")
        print(" 6. Add Role")
        print(" 7. List Roles")
        print(" 8. Update Role")
        print(" 9. Delete Role")
        
        print("\nEmployee Management:")
        print("10. Add Employee")
        print("11. List Employees")
        print("12. View Employee Details")
        print("13. Search Employees")
        print("14. Update Employee")
        print("15. Deactivate Employee")
        print("16. Activate Employee")
        
        print("\nPayroll Operations:")
        print("17. Generate Payroll (Single Employee)")
        print("18. Generate Payroll (All Employees)")
        print("19. View Employee Payroll History")
        print("20. View Monthly Summary")
        print("21. Approve Payroll")
        print("22. Mark Payroll as Paid")
        print("23. Export Payroll to CSV")
        
        print("\nSystem:")
        print("24. Show Dashboard")
        print(" 0. Exit")
        print("-"*60)
    
    @staticmethod
    def get_input(prompt: str, required: bool = True, default: str = ""):
        """Get user input with validation"""
        while True:
            if default:
                value = input(f"{prompt} [{default}]: ").strip()
                if not value:
                    value = default
            else:
                value = input(prompt).strip()
                
            if required and not value:
                print("This field is required. Please try again.")
            else:
                return value
    
    @staticmethod
    def get_float(prompt: str, default: float = 0) -> float:
        """Get float input"""
        while True:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                return default
            try:
                return float(value)
            except ValueError:
                print("Please enter a valid number.")
    
    @staticmethod
    def get_int(prompt: str, default: int = 0) -> int:
        """Get integer input"""
        while True:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                return default
            try:
                return int(value)
            except ValueError:
                print("Please enter a valid number.")
    
    @staticmethod
    def get_date(prompt: str, required: bool = False) -> str:
        """Get date input in YYYY-MM-DD format"""
        while True:
            value = input(prompt).strip()
            if not value and not required:
                return ""
            
            try:
                # Validate date format
                datetime.strptime(value, '%Y-%m-%d')
                return value
            except ValueError:
                print("Please enter date in YYYY-MM-DD format (e.g., 2024-01-15).")
    
    @staticmethod
    def show_dashboard():
        """Show system dashboard"""
        with DatabaseManager() as db:
            # Get counts
            active_employees = db.fetch_one(
                "SELECT COUNT(*) as count FROM employees WHERE is_active = 1"
            )
            total_employees = db.fetch_one(
                "SELECT COUNT(*) as count FROM employees"
            )
            departments = db.fetch_one(
                "SELECT COUNT(*) as count FROM departments"
            )
            roles = db.fetch_one(
                "SELECT COUNT(*) as count FROM roles"
            )
            payrolls = db.fetch_one(
                "SELECT COUNT(*) as count FROM payrolls"
            )
            
            # Get latest payroll
            latest = db.fetch_one(
                "SELECT month, year FROM payrolls ORDER BY year DESC, month DESC LIMIT 1"
            )
            
            print("\n" + "="*60)
            print("SYSTEM DASHBOARD")
            print("="*60)
            print(f"\n📊 Statistics:")
            print(f"   • Active Employees: {active_employees['count']}")
            print(f"   • Total Employees: {total_employees['count']}")
            print(f"   • Departments: {departments['count']}")
            print(f"   • Roles: {roles['count']}")
            print(f"   • Payroll Records: {payrolls['count']}")
            
            if latest:
                print(f"   • Latest Payroll: {latest['month']}/{latest['year']}")
            
            # Department overview
            dept_stats = db.fetch_all("""
                SELECT d.name, COUNT(e.id) as emp_count
                FROM departments d
                LEFT JOIN employees e ON d.id = e.department_id AND e.is_active = 1
                GROUP BY d.id
                ORDER BY emp_count DESC
                LIMIT 5
            """)
            
            if dept_stats:
                print(f"\n🏢 Top Departments by Active Employees:")
                for dept in dept_stats:
                    print(f"   • {dept['name']}: {dept['emp_count']} employees")
            
            # Recent payrolls
            recent_payrolls = db.fetch_all("""
                SELECT p.month, p.year, COUNT(*) as count, 
                       SUM(p.net_salary) as total_net
                FROM payrolls p
                GROUP BY p.month, p.year
                ORDER BY p.year DESC, p.month DESC
                LIMIT 3
            """)
            
            if recent_payrolls:
                print(f"\n💰 Recent Payrolls:")
                for payroll in recent_payrolls:
                    print(f"   • {payroll['month']}/{payroll['year']}: "
                          f"{payroll['count']} employees, "
                          f"KES {payroll['total_net']:,.0f} total net")

    def run(self):
        """Run the CLI application"""
        init_db()  # Initialize database on startup
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (0-24): ").strip()
            
            if choice == "0":
                print("\nThank you for using Employee Payroll System. Goodbye!")
                break
            
            elif choice == "1":
                init_db()
            
            # Department Management
            elif choice == "2":  # Add Department
                print("\n" + "="*60)
                print("ADD NEW DEPARTMENT")
                print("="*60)
                name = self.get_input("Department Name: ")
                code = self.get_input("Department Code (optional): ", required=False)
                budget = self.get_float("Budget: ", 0)
                description = self.get_input("Description (optional): ", required=False)
                DepartmentService.create(name, code, budget, description)
            
            elif choice == "3":  # List Departments
                DepartmentService.list_all()
            
            elif choice == "4":  # Update Department
                dept_id = self.get_int("\nDepartment ID to update: ")
                print("\nEnter new values (press Enter to keep current):")
                name = self.get_input("Name: ", required=False)
                code = self.get_input("Code: ", required=False)
                budget = self.get_float("Budget: ")
                updates = {}
                if name: updates['name'] = name
                if code: updates['code'] = code
                updates['budget'] = budget
                DepartmentService.update(dept_id, **updates)
            
            elif choice == "5":  # Delete Department
                dept_id = self.get_int("\nDepartment ID to delete: ")
                confirm = input(f"Are you sure you want to delete department {dept_id}? (yes/no): ")
                if confirm.lower() == 'yes':
                    DepartmentService.delete(dept_id)
                else:
                    print("Deletion cancelled.")
            
            # Role Management
            elif choice == "6":  # Add Role
                print("\n" + "="*60)
                print("ADD NEW ROLE")
                print("="*60)
                title = self.get_input("Role Title: ")
                base_salary = self.get_float("Base Salary: ")
                housing = self.get_float("Housing Allowance: ", 0)
                transport = self.get_float("Transport Allowance: ", 0)
                medical = self.get_float("Medical Allowance: ", 0)
                other = self.get_float("Other Allowance: ", 0)
                description = self.get_input("Description (optional): ", required=False)
                RoleService.create(title, base_salary, housing, transport, medical, other, description)
            
            elif choice == "7":  # List Roles
                RoleService.list_all()
            
            elif choice == "8":  # Update Role
                role_id = self.get_int("\nRole ID to update: ")
                print("\nEnter new values (press Enter to keep current):")
                title = self.get_input("Title: ", required=False)
                base_salary = self.get_float("Base Salary: ")
                housing = self.get_float("Housing Allowance: ", 0)
                transport = self.get_float("Transport Allowance: ", 0)
                medical = self.get_float("Medical Allowance: ", 0)
                other = self.get_float("Other Allowance: ", 0)
                updates = {}
                if title: updates['title'] = title
                updates['base_salary'] = base_salary
                updates['housing_allowance'] = housing
                updates['transport_allowance'] = transport
                updates['medical_allowance'] = medical
                updates['other_allowance'] = other
                RoleService.update(role_id, **updates)
            
            elif choice == "9":  # Delete Role
                role_id = self.get_int("\nRole ID to delete: ")
                confirm = input(f"Are you sure you want to delete role {role_id}? (yes/no): ")
                if confirm.lower() == 'yes':
                    RoleService.delete(role_id)
                else:
                    print("Deletion cancelled.")
            
            # Employee Management
            elif choice == "10":  # Add Employee
                print("\n" + "="*60)
                print("ADD NEW EMPLOYEE")
                print("="*60)
                first_name = self.get_input("First Name: ")
                last_name = self.get_input("Last Name: ")
                email = self.get_input("Email: ")
                date_joined = self.get_date("Date Joined (YYYY-MM-DD): ", required=True)
                phone = self.get_input("Phone (optional): ", required=False)
                dob = self.get_date("Date of Birth (YYYY-MM-DD, optional): ", required=False)
                bank_account = self.get_input("Bank Account (optional): ", required=False)
                bank_name = self.get_input("Bank Name (optional): ", required=False)
                
                # Show available roles
                with DatabaseManager() as db:
                    roles = db.fetch_all("SELECT id, title FROM roles ORDER BY title")
                    if roles:
                        print("\nAvailable Roles:")
                        for role in roles:
                            print(f"  {role['id']}. {role['title']}")
                        role_id = self.get_int("Role ID: ")
                    else:
                        print("No roles available. Please create a role first.")
                        continue
                
                # Show available departments
                with DatabaseManager() as db:
                    depts = db.fetch_all("SELECT id, name FROM departments ORDER BY name")
                    if depts:
                        print("\nAvailable Departments:")
                        for dept in depts:
                            print(f"  {dept['id']}. {dept['name']}")
                        dept_id = self.get_int("Department ID: ")
                    else:
                        print("No departments available. Please create a department first.")
                        continue
                
                EmployeeService.add(first_name, last_name, email, date_joined,
                                   role_id, dept_id, phone, dob, bank_account, bank_name)
            
            elif choice == "11":  # List Employees
                print("\nList Options:")
                print("1. All employees")
                print("2. Active employees only")
                print("3. By department")
                print("4. By role")
                list_choice = input("\nChoose option (1-4): ").strip()
                
                if list_choice == "1":
                    EmployeeService.list_all(active_only=False)
                elif list_choice == "2":
                    EmployeeService.list_all(active_only=True)
                elif list_choice == "3":
                    dept_id = self.get_int("Department ID: ")
                    EmployeeService.list_all(department_id=dept_id)
                elif list_choice == "4":
                    role_id = self.get_int("Role ID: ")
                    EmployeeService.list_all(role_id=role_id)
                else:
                    EmployeeService.list_all()
            
            elif choice == "12":  # Employee Details
                emp_id = self.get_input("\nEnter Employee ID: ")
                EmployeeService.get_details(emp_id)
            
            elif choice == "13":  # Search Employees
                search_term = self.get_input("\nSearch (name or email): ")
                EmployeeService.search(search_term)
            
            elif choice == "14":  # Update Employee
                emp_id = self.get_input("\nEmployee ID to update: ")
                print("\nEnter new values (press Enter to keep current):")
                first_name = self.get_input("First Name: ", required=False)
                last_name = self.get_input("Last Name: ", required=False)
                phone = self.get_input("Phone: ", required=False)
                bank_account = self.get_input("Bank Account: ", required=False)
                bank_name = self.get_input("Bank Name: ", required=False)
                
                # Show roles for update
                with DatabaseManager() as db:
                    roles = db.fetch_all("SELECT id, title FROM roles ORDER BY title")
                    if roles:
                        print("\nAvailable Roles (press Enter to keep current):")
                        for role in roles:
                            print(f"  {role['id']}. {role['title']}")
                        role_input = input("Role ID: ").strip()
                        role_id = int(role_input) if role_input else None
                    else:
                        role_id = None
                
                # Show departments for update
                with DatabaseManager() as db:
                    depts = db.fetch_all("SELECT id, name FROM departments ORDER BY name")
                    if depts:
                        print("\nAvailable Departments (press Enter to keep current):")
                        for dept in depts:
                            print(f"  {dept['id']}. {dept['name']}")
                        dept_input = input("Department ID: ").strip()
                        dept_id = int(dept_input) if dept_input else None
                    else:
                        dept_id = None
                
                updates = {}
                if first_name: updates['first_name'] = first_name
                if last_name: updates['last_name'] = last_name
                if phone: updates['phone'] = phone
                if bank_account: updates['bank_account'] = bank_account
                if bank_name: updates['bank_name'] = bank_name
                if role_id: updates['role_id'] = role_id
                if dept_id: updates['department_id'] = dept_id
                
                if updates:
                    EmployeeService.update(emp_id, **updates)
                else:
                    print("No updates provided.")
            
            elif choice == "15":  # Deactivate Employee
                emp_id = self.get_input("\nEnter Employee ID to deactivate: ")
                EmployeeService.deactivate(emp_id)
            
            elif choice == "16":  # Activate Employee
                emp_id = self.get_input("\nEnter Employee ID to activate: ")
                EmployeeService.activate(emp_id)
            
            # Payroll Operations
            elif choice == "17":  # Generate Payroll (Single)
                print("\n" + "="*60)
                print("GENERATE PAYROLL")
                print("="*60)
                emp_id = self.get_input("Employee ID: ")
                month = self.get_int("Month (1-12): ")
                year = self.get_int("Year (e.g., 2024): ")
                other_deductions = self.get_float("Other Deductions (e.g., loans, advances): ", 0)
                PayrollService.generate(emp_id, month, year, other_deductions)
            
            elif choice == "18":  # Generate Payroll (All)
                print("\n" + "="*60)
                print("GENERATE PAYROLL FOR ALL EMPLOYEES")
                print("="*60)
                month = self.get_int("Month (1-12): ")
                year = self.get_int("Year (e.g., 2024): ")
                confirm = input(f"\nGenerate payroll for all active employees for {month}/{year}? (yes/no): ")
                if confirm.lower() == 'yes':
                    PayrollService.generate_all(month, year)
                else:
                    print("Operation cancelled.")
            
            elif choice == "19":  # Payroll History
                emp_id = self.get_input("\nEnter Employee ID: ")
                PayrollService.employee_history(emp_id)
            
            elif choice == "20":  # Monthly Summary
                month = self.get_int("\nMonth (1-12): ")
                year = self.get_int("Year (e.g., 2024): ")
                PayrollService.monthly_summary(month, year)
            
            elif choice == "21":  # Approve Payroll
                payroll_id = self.get_input("\nEnter Payroll ID to approve: ")
                PayrollService.approve_payroll(payroll_id)
            
            elif choice == "22":  # Mark Payroll as Paid
                payroll_id = self.get_input("\nEnter Payroll ID to mark as paid: ")
                payment_date = self.get_date("Payment Date (YYYY-MM-DD, optional): ", required=False)
                if not payment_date:
                    payment_date = date.today().isoformat()
                PayrollService.mark_as_paid(payroll_id, payment_date)
            
            elif choice == "23":  # Export CSV
                month = self.get_int("\nMonth (1-12): ")
                year = self.get_int("Year (e.g., 2024): ")
                default_filename = f"payroll_{year}_{month:02d}.csv"
                filename = self.get_input("Filename: ", required=False, default=default_filename)
                PayrollService.export_csv(month, year, filename)
            
            elif choice == "24":  # Dashboard
                self.show_dashboard()
            
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("EMPLOYEE PAYROLL MANAGEMENT SYSTEM v2.0")
    print("="*60)
    print("A complete payroll solution with automated calculations")
    print("and comprehensive reporting features.")
    print("\nFeatures:")
    print("• Employee management with role/department assignment")
    print("• Automated salary calculations with statutory deductions")
    print("• Progressive tax calculation (Kenya PAYE system)")
    print("• Payroll history and detailed reporting")
    print("• CSV export for accounting integration")
    print("="*60)
    
    try:
        cli = PayrollCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please check your input and try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()