#!/usr/bin/env python3
"""
Generate sample data for testing
"""
import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = "payroll.db"

def create_sample_data():
    """Create sample departments, roles, and employees"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("Creating sample data...")
    
    # Create departments
    departments = [
        ('Engineering', 'ENG', 5000000),
        ('Sales', 'SAL', 3000000),
        ('Marketing', 'MKT', 2000000),
        ('Human Resources', 'HR', 1500000),
        ('Finance', 'FIN', 2500000)
    ]
    
    for name, code, budget in departments:
        cursor.execute(
            "INSERT OR IGNORE INTO departments (name, code, budget) VALUES (?, ?, ?)",
            (name, code, budget)
        )
    
    # Create roles
    roles = [
        ('Software Engineer', 120000, 20000, 10000),
        ('Senior Software Engineer', 180000, 30000, 15000),
        ('Sales Executive', 80000, 15000, 5000),
        ('Marketing Specialist', 90000, 15000, 5000),
        ('HR Manager', 130000, 20000, 10000),
        ('Finance Officer', 100000, 15000, 5000)
    ]
    
    for title, base, housing, transport in roles:
        cursor.execute(
            """INSERT OR IGNORE INTO roles 
               (title, base_salary, housing_allowance, transport_allowance)
               VALUES (?, ?, ?, ?)""",
            (title, base, housing, transport)
        )
    
    # Create sample employees
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Wilson']
    
    cursor.execute("SELECT id FROM departments")
    dept_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM roles")
    role_ids = [row[0] for row in cursor.fetchall()]
    
    for i in range(10):
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}{i}@company.com"
        employee_id = f"EMP{datetime.now().strftime('%y%m%d')}{i:03d}"
        date_joined = (datetime.now() - timedelta(days=random.randint(1, 365*3))).strftime('%Y-%m-%d')
        dept_id = random.choice(dept_ids)
        role_id = random.choice(role_ids)
        
        cursor.execute(
            """INSERT OR IGNORE INTO employees 
               (employee_id, first_name, last_name, email, date_joined, 
                department_id, role_id, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (employee_id, first, last, email, date_joined, dept_id, role_id)
        )
    
    conn.commit()
    conn.close()
    print("Sample data created successfully!")
    print(f"Created: 5 departments, {len(roles)} roles, 10 employees")

if __name__ == "__main__":
    create_sample_data()