Supermarket Management System
Description
A full-fledged Supermarket Management System built using Python and SQLite, featuring a role-based employee management system, checkout and billing, inventory tracking, aisle management, sales reporting, and customer membership handling. The system supports self-checkout, employee-assisted checkout, refunds, data import from Excel, automated report generation in Excel format, and receipt generation. It follows an object-oriented programming (OOP) design.

Features
Employee Management: Role-based access for managers and employees.
Checkout System: Self-checkout and employee-assisted checkout.
Inventory Management: Manage aisles and products.
Sales Reporting: Automated generation of sales reports in Excel format.
Refund Handling: Process refunds.
Data Import: Import supermarket data from an Excel file.
Receipt Generation: Generate receipts after checkout.

Prerequisites
Python 3.x
SQLite (built-in with Python)

Required Python libraries (listed below)
certifi==2025.1.31
charset-normalizer==3.4.1
et_xmlfile==2.0.0
idna==3.10
numpy==2.2.3
openpyxl==3.1.5
pandas==2.2.3
python-dateutil==2.9.0.post0
pytz==2025.1
requests==2.32.3
setuptools==75.8.0
six==1.17.0
tzdata==2025.1
urllib3==2.3.0

Installation
Clone the repository:
git clone <repository-url>
pip install -r requirements.txt
Usage Instructions
Launch the Program to start the system.

Login as Manager:

If no manager exists, the system will prompt you to create one during the setup.
After logging in, the manager will have access to add/remove employees, add aisles/products, and more.
Manager Setup:

Go to the Employee Menu and select the option to set up the manager profile if one does not exist.
Create a manager profile with a username and password.
Importing Data:

Go to the Employee Menu and select the option to "Read data from file".
Upload the supermarket data (e.g., products, aisles) from an Excel file.
Employee Actions:

Employees can perform specific tasks such as handling refunds or adding products to the inventory.
Generate Reports:

Managers can generate sales reports in Excel format.
Checkout and Billing:

Use the self-checkout or employee-assisted checkout options to complete purchases and generate receipts.

Technologies Used
Python 3.x
SQLite for database management
Excel for data import and report generation

Feel free to fork the project, contribute, or report any issues you encounter.
