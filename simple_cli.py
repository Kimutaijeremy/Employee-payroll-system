#!/usr/bin/env python3
"""
Simple CLI wrapper for the payroll system
Usage: python simple_cli.py [command] [args]
"""
import sys
from app import *

def show_usage():
    """Show usage instructions"""
    print("""
Employee Payroll System - Simple CLI
====================================

Usage:
  python simple_cli.py [command] [arguments]

Commands:
  init                    Initialize database
  dashboard               Show system dashboard
  
  dept list              List all departments
  dept add [name] [code] Add department
  dept show [id]         Show department details
  
  role list              List all roles
  role add [title] [salary] Add role
  
  emp list               List all employees
  emp add [first] [last] [email] [role_id] [dept_id] Add employee
  emp show [id]          Show employee details
  
  payroll gen [emp_id] [month] [year]  Generate payroll
  payroll bulk [month] [year]          Generate payroll for all
  payroll history [emp_id]             Show payroll history
  payroll report [month] [year]        Show monthly report
  payroll export [month] [year]        Export to CSV

Examples:
  python simple_cli.py init
  python simple_cli.py dept add "Engineering" "ENG"
  python simple_cli.py emp list
  python simple_cli.py payroll gen EMP001 12 2024
""")

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_db()
    
    elif command == "dashboard":
        PayrollCLI().show_dashboard()
    
    elif command == "dept":
        if len(sys.argv) < 3:
            print("Usage: python simple_cli.py dept [list|add|show]")
            return
        
        subcommand = sys.argv[2]
        
        if subcommand == "list":
            DepartmentService.list_all()
        elif subcommand == "add":
            if len(sys.argv) < 5:
                print("Usage: python simple_cli.py dept add [name] [code]")
                return
            DepartmentService.create(sys.argv[3], sys.argv[4])
        elif subcommand == "show":
            if len(sys.argv) < 4:
                print("Usage: python simple_cli.py dept show [id]")
                return
            # Implement department show
            pass
    
    elif command == "role":
        if len(sys.argv) < 3:
            print("Usage: python simple_cli.py role [list|add]")
            return
        
        subcommand = sys.argv[2]
        
        if subcommand == "list":
            RoleService.list_all()
        elif subcommand == "add":
            if len(sys.argv) < 5:
                print("Usage: python simple_cli.py role add [title] [salary]")
                return
            RoleService.create(sys.argv[3], float(sys.argv[4]))
    
    elif command == "emp":
        if len(sys.argv) < 3:
            print("Usage: python simple_cli.py emp [list|show]")
            return
        
        subcommand = sys.argv[2]
        
        if subcommand == "list":
            EmployeeService.list_all()
        elif subcommand == "show":
            if len(sys.argv) < 4:
                print("Usage: python simple_cli.py emp show [id]")
                return
            EmployeeService.get_details(sys.argv[3])
    
    elif command == "payroll":
        if len(sys.argv) < 3:
            print("Usage: python simple_cli.py payroll [gen|bulk|history|report|export]")
            return
        
        subcommand = sys.argv[2]
        
        if subcommand == "gen":
            if len(sys.argv) < 6:
                print("Usage: python simple_cli.py payroll gen [emp_id] [month] [year]")
                return
            PayrollService.generate(sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
        elif subcommand == "bulk":
            if len(sys.argv) < 5:
                print("Usage: python simple_cli.py payroll bulk [month] [year]")
                return
            PayrollService.generate_all(int(sys.argv[3]), int(sys.argv[4]))
        elif subcommand == "history":
            if len(sys.argv) < 4:
                print("Usage: python simple_cli.py payroll history [emp_id]")
                return
            PayrollService.employee_history(sys.argv[3])
        elif subcommand == "report":
            if len(sys.argv) < 5:
                print("Usage: python simple_cli.py payroll report [month] [year]")
                return
            PayrollService.monthly_summary(int(sys.argv[3]), int(sys.argv[4]))
        elif subcommand == "export":
            if len(sys.argv) < 5:
                print("Usage: python simple_cli.py payroll export [month] [year]")
                return
            PayrollService.export_csv(int(sys.argv[3]), int(sys.argv[4]))
    
    else:
        print(f"Unknown command: {command}")
        show_usage()

if __name__ == "__main__":
    main()