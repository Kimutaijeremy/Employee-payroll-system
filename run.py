#!/usr/bin/env python3
"""
Unified runner for Employee Payroll System
"""
import sys
import os

def main():
    print("Employee Payroll System")
    print("=======================")
    print("\nChoose version to run:")
    print("1. Simplified Version (app.py) - Menu interface")
    print("2. Simple CLI (simple_cli.py) - Command line")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        os.system("python app.py")
    elif choice == "2":
        if len(sys.argv) > 2:
            os.system(f"python simple_cli.py {' '.join(sys.argv[2:])}")
        else:
            os.system("python simple_cli.py")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()