#!/usr/bin/env python3
"""
Test file to verify your payroll app is working
Run: python test_app.py
"""

import os
import sqlite3
from datetime import datetime

def test_database():
    print("1. Testing database initialization...")
    if os.path.exists("payroll.db"):
        os.remove("payroll.db")
        print("   ✓ Removed old database")
    
    # Import your app's init function
    from app import init_db
    init_db()
    
    if os.path.exists("payroll.db"):
        print("   ✓ Database file created")
        
        # Check tables
        conn = sqlite3.connect("payroll.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['departments', 'roles', 'employees', 'payrolls']
        for table in required_tables:
            if table in tables:
                print(f"   ✓ Table '{table}' exists")
            else:
                print(f"   ✗ Table '{table}' missing")
        conn.close()
        return True
    return False

def test_basic_operations():
    print("\n2. Testing basic operations...")
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()
    
    try:
        # Insert department
        cursor.execute("INSERT INTO departments (name, code) VALUES ('Test Dept', 'TEST')")
        print("   ✓ Department added")
        
        # Insert role
        cursor.execute("INSERT INTO roles (title, base_salary) VALUES ('Test Role', 50000)")
        print("   ✓ Role added")
        
        # Insert employee
        emp_id = f"TEST{datetime.now().strftime('%y%m%d%H%M%S')}"
        cursor.execute("""
            INSERT INTO employees (employee_id, first_name, last_name, email, date_joined, role_id, department_id, is_active)
            VALUES (?, 'John', 'Doe', 'test@email.com', '2024-01-01', 1, 1, 1)
        """, (emp_id,))
        print(f"   ✓ Employee added (ID: {emp_id})")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    finally:
        conn.close()

def test_app_structure():
    print("\n3. Checking app structure...")
    if not os.path.exists("app.py"):
        print("   ✗ app.py not found")
        return False
    
    with open("app.py", "r") as f:
        content = f.read()
    
    checks = [
        ("DatabaseManager class", "class DatabaseManager"),
        ("PayrollCalculator class", "class PayrollCalculator"),
        ("PayrollCLI class", "class PayrollCLI"),
        ("def main()", "def main()"),
    ]
    
    all_good = True
    for check_name, pattern in checks:
        if pattern in content:
            print(f"   ✓ {check_name}")
        else:
            print(f"   ✗ {check_name}")
            all_good = False
    
    return all_good

def main():
    print("="*60)
    print("PAYROLL APP TEST")
    print("="*60)
    
    tests = [
        ("Database Setup", test_database),
        ("Basic Operations", test_basic_operations),
        ("App Structure", test_app_structure),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ Your app is working correctly!")
        print("\nTo use the app:")
        print("   python app.py")
    else:
        print("❌ Some tests failed. Check above for details.")
    print("="*60)

if __name__ == "__main__":
    main()