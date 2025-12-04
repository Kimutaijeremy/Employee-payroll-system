Employee Payroll Management System
Overview
A complete, automated payroll solution for small to medium-sized organizations that replaces error-prone manual calculations with a reliable, efficient system. This application handles employee management, role-based salary structures, statutory deductions (Kenya PAYE, NHIF, NSSF), payroll generation, comprehensive reporting, and data export—all through an intuitive menu-driven interface.

✨ Key Features
Automated Payroll Calculation: Computes gross salary, taxes, and statutory deductions automatically

Employee Management: Add, update, list, and deactivate employees with role/department assignment

Role-Based Salary Structure: Define positions with base salary and allowances

Department Organization: Group employees by department with budget tracking

Comprehensive Reporting: Monthly summaries, department breakdowns, and employee payroll history

CSV Export: Export payroll data for accounting and audit purposes

Statutory Compliance: Built-in calculations for Kenya's PAYE tax, NHIF, and NSSF contributions

📁 Project Structure
text
employee-payroll-system/
├── app.py                 # Main application (simplified version - run this)
├── simple_cli.py          # Command-line interface for quick operations
├── test_app.py            # Test script to verify the system works
├── requirements.txt       # Python dependencies (optional, for modular version)
├── README.md              # This documentation
├── payroll.db             # SQLite database (auto-created)
└── modular/               # Modular version with professional structure
    ├── models.py          # Database models
    ├── services/          # Business logic layer
    ├── cli.py            # Advanced CLI with Click framework
    └── utils/            # Utility functions
🚀 Quick Start
Option 1: Simple Version (Recommended for most users)
bash
# 1. Download and extract the project
# 2. Open terminal/command prompt in the project folder
# 3. Run the application:
python app.py

# 4. Follow the menu prompts:
#    a) Option 1: Initialize database
#    b) Option 2: Add departments (e.g., Engineering, Sales)
#    c) Option 6: Add roles (e.g., Software Engineer, Sales Executive)
#    d) Option 10: Add employees
#    e) Option 17/18: Generate payroll
#    f) Option 20/23: View reports and export data
Option 2: Modular Version (For developers/advanced users)
bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run modular version
cd modular
python cli.py --help

# 3. Example commands:
python cli.py init
python cli.py employee add
python cli.py payroll generate
📊 How It Works
1. Database Setup
The system uses SQLite (no separate database installation required). Tables are automatically created:

Departments: Company divisions with budgets

Roles: Job positions with salary structures

Employees: Staff details with role/department assignments

Payrolls: Monthly salary records with complete breakdown

2. Salary Calculation Logic
text
Gross Salary = Base Salary + Allowances (Housing + Transport + Medical + Other)

Deductions:
- PAYE Tax: Progressive tax based on Kenya tax brackets
- NHIF: Tiered contributions based on gross salary
- NSSF: 6% of pensionable earnings (capped at KES 18,000)

Net Salary = Gross Salary - Total Deductions
3. Sample Workflow
text
1. Initialize Database → Add Department → Add Role → Add Employee
2. Generate Monthly Payroll (individual or bulk)
3. View Reports → Export to CSV → Archive Records
🔧 System Requirements
Python 3.6 or higher (Download from python.org)

No additional software required (Uses built-in SQLite)

Any operating system (Windows, macOS, Linux)

💡 Usage Examples
Interactive Menu (app.py)
bash
python app.py
Then follow the numbered menu system.

Quick Commands (simple_cli.py)
bash
# Initialize database
python simple_cli.py init

# Add department
python simple_cli.py dept add "Engineering" ENG

# List employees
python simple_cli.py emp list

# Generate payroll
python simple_cli.py payroll gen EMP001 12 2024
✅ Testing the Application
bash
# Run the comprehensive test
python test_app.py

# Expected output shows all tests passing:
# ✓ Database initialization
# ✓ Basic operations
# ✓ Payroll calculations
# ✓ Report generation
📈 Sample Payroll Output
text
PAYROLL FOR: John Doe (EMP2024120001)
========================================
Gross Salary:     KES 150,000.00
Total Deductions: KES 42,550.00
Net Salary:       KES 107,450.00

BREAKDOWN:
• Base Salary:    KES 120,000.00
• Housing:        KES 20,000.00
• Transport:      KES 10,000.00

DEDUCTIONS:
• PAYE Tax:       KES 39,400.00
• NHIF:           KES 1,700.00
• NSSF:           KES 1,080.00
🔍 Key Benefits for Organizations
For HR Teams
Reduce payroll processing time from days to minutes

Eliminate calculation errors and compliance issues

Maintain complete audit trails for all salary payments

For Management
Real-time visibility into payroll costs by department

Historical data for budgeting and planning

Export capabilities for accounting integration

For Employees
Transparent salary breakdowns

Access to complete payroll history

Consistent, timely payments

🛠️ Troubleshooting
Common Issues & Solutions
"Module not found" error: Ensure you're running python app.py from the correct folder

Database issues: Use Option 1 in the menu to reinitialize the database

Calculation questions: The system uses Kenya Revenue Authority tax brackets (2024)

Verification Steps
Run python test_app.py to verify all components work

Check that payroll.db is created in the project folder

Test adding a sample employee and generating payroll

📄 License & Support
This project is open-source and free to use. For support or issues:

Check this README for solutions

Run the test script to diagnose problems

Ensure you have Python 3.6+ installed

🎯 Quick Reference Guide
Essential Commands
bash
# Start the application
python app.py

# Quick database setup
python simple_cli.py init

# Test everything works
python test_app.py
First-Time Setup (2 minutes)
Download the project files

Open terminal in the project folder

Run: python app.py

Choose Option 1 (Initialize Database)

Follow the menu to set up your organization

Monthly Payroll Process (5 minutes)
Add/update employees if needed

Choose "Generate Payroll for All Employees"

Select the month and year

Review the summary report

Export to CSV for accounting

Mark payroll as paid when processed

# License

This project is not licensed

# Author

[Kimutaijeremy]