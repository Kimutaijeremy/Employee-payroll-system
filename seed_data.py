#!/usr/bin/env python3
"""
Sample data seeder for Employee Payroll System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from services.department_service import DepartmentService
from services.role_service import RoleService
from services.employee_service import EmployeeService
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with sample data"""
    session = db.get_session()
    
    try:
        print("🌱 Seeding database with sample data...")
        
        # Create departments
        dept_service = DepartmentService(session)
        departments = [
            {"name": "Engineering", "code": "ENG", "budget": 5000000},
            {"name": "Sales", "code": "SAL", "budget": 3000000},
            {"name": "Marketing", "code": "MKT", "budget": 2000000},
            {"name": "Human Resources", "code": "HR", "budget": 1500000},
            {"name": "Finance", "code": "FIN", "budget": 2500000},
        ]
        
        dept_objects = []
        for dept_data in departments:
            try:
                dept = dept_service.create_department(dept_data)
                dept_objects.append(dept)
                print(f"  Created department: {dept.name}")
            except:
                # Department might already exist
                dept = dept_service.get_department_by_code(dept_data['code'])
                if dept:
                    dept_objects.append(dept)
        
        # Create roles
        role_service = RoleService(session)
        roles = [
            {"title": "Software Engineer", "base_salary": 120000, "housing_allowance": 20000, "transport_allowance": 10000},
            {"title": "Senior Software Engineer", "base_salary": 180000, "housing_allowance": 30000, "transport_allowance": 15000},
            {"title": "Sales Executive", "base_salary": 80000, "housing_allowance": 15000, "transport_allowance": 10000},
            {"title": "Sales Manager", "base_salary": 150000, "housing_allowance": 25000, "transport_allowance": 15000},
            {"title": "Marketing Specialist", "base_salary": 90000, "housing_allowance": 15000, "transport_allowance": 10000},
            {"title": "HR Manager", "base_salary": 130000, "housing_allowance": 20000, "transport_allowance": 10000},
            {"title": "Finance Officer", "base_salary": 100000, "housing_allowance": 15000, "transport_allowance": 10000},
            {"title": "Finance Manager", "base_salary": 160000, "housing_allowance": 25000, "transport_allowance": 15000},
        ]
        
        role_objects = []
        for role_data in roles:
            try:
                role = role_service.create_role(role_data)
                role_objects.append(role)
                print(f"  Created role: {role.title}")
            except:
                # Role might already exist
                role = role_service.get_role_by_title(role_data['title'])
                if role:
                    role_objects.append(role)
        
        # Create employees
        employee_service = EmployeeService(session)
        
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily", "William", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
        
        for i in range(20):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@company.com"
            
            employee_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": f"2547{random.randint(10000000, 99999999)}",
                "date_of_birth": datetime(1990, 1, 1) + timedelta(days=random.randint(0, 3650)),
                "date_joined": datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460)),
                "role_id": random.choice(role_objects).id,
                "department_id": random.choice(dept_objects).id,
                "bank_account": f"ACC{random.randint(100000, 999999)}",
                "bank_name": random.choice(["Equity", "KCB", "Cooperative", "Standard Chartered"])
            }
            
            try:
                employee = employee_service.add_employee(employee_data)
                print(f"  Created employee: {employee.full_name()}")
            except Exception as e:
                print(f"  Error creating employee: {str(e)}")
        
        print("✅ Database seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        session.rollback()
    finally:
        db.close_session(session)

if __name__ == "__main__":
    # Initialize database first
    db.init_db()
    seed_database()