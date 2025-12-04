#!/usr/bin/env python3
"""
Simple CLI wrapper for the payroll system
Usage: python simple_cli.py [command] [args]
"""
import sys
import sqlite3
from datetime import datetime

DB_FILE = "payroll.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE,
            budget REAL DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            base_salary REAL NOT NULL,
            housing_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            medical_allowance REAL DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            date_joined DATE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            role_id INTEGER,
            department_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payrolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_id TEXT UNIQUE NOT NULL,
            employee_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            gross_salary REAL NOT NULL,
            tax REAL NOT NULL,
            nhif REAL NOT NULL,
            nssf REAL NOT NULL,
            net_salary REAL NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized")

def show_usage():
    print("""
Simple Payroll CLI
==================

Commands:
  init                    Initialize database
  
  dept list              List departments
  dept add <name> <code> Add department
  
  role list              List roles
  role add <title> <salary> Add role
  
  emp list               List employees
  emp show <id>          Show employee
  
  payroll gen <emp_id> <month> <year>  Generate payroll
  payroll history <emp_id>             Show payroll history
  
Example:
  python simple_cli.py init
  python simple_cli.py dept add "Engineering" ENG
  python simple_cli.py role add "Engineer" 100000
  python simple_cli.py emp list
""")

def main():
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_db()
    elif command == "dept" and sys.argv[2] == "list":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM departments")
        for row in cursor.fetchall():
            print(f"{row[0]}: {row[1]} ({row[2]})")
        conn.close()
    else:
        print(f"Unknown command: {command}")
        show_usage()

if __name__ == "__main__":
    main()