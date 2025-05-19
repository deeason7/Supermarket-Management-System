from inventory import Inventory
from aisle import Aisle
from xlsreader import *
from generate_report import SalesReportGenerator
from checkout import Checkout
from database import  Database
from employee import  Employee
from utils import  safe_input

def supermarket_employee():
    """Function for supermarket employees"""
    emp = Employee()
    inv = Inventory()
    aisle = Aisle()
    chk = Checkout()
    db = Database()

    # Ensure employee login validation is successful
    login_info = emp.employee_login_validation()
    if not login_info or login_info[0] is None:
        print(" Login failed. Exiting employee menu.")
        return
    role = login_info[1]

    while True:
        print("\n--- Employee Menu ---")
        if role == "Manager":
            print("1. Add Employee")
            print("2. Remove Employee")
            print("3. Add Aisle")
            print("4. Add Product")
            print("5. Refund")
            print("6. Read data from file")
            print("7. Update Stock")
            print("8. Generate Reports")
            choice = safe_input("Enter choice (or type 'exit' to return to main menu): ")

            if choice is None:
                print("Operation canceled. Returning to Employee Menu.")
                break

            if choice == "1":
                role = safe_input("Add Manager / Employee (or 'exit' to cancel): ")
                if role is None:
                    print("Returning to Employee Menu.")
                    return
                if not role.strip():
                    print(" Employee name must be a non-empty string.")
                    role = None

                emp.add_employee(role)

            elif choice == "2":
                emp.remove_employee()

            elif choice == "3":
                aisle.add_aisle()

            elif choice == "4":
                inv.add_product(role)

            elif choice == "5":
                chk.refund()

            elif choice == "6":
                try:
                    loader = XLSDatabaseLoader()
                    # Load data from an XLS file containing multiple sheets
                    loader.load_xls_to_db("supermarket_data.xlsx")
                    # Close connection
                    loader.close()
                except Exception as e:
                    print(e)

            elif choice == "7":
                inv.update_stock()

            elif choice == "8":
                try:
                    report_generator = SalesReportGenerator(db)
                    report_generator.generate_reports("sales_report.xlsx")
                except Exception as e:
                    print(e)
                finally:
                    db.close()
            else:
                print(" Invalid choice. Please try again.")

        elif role == "Employee":
            print("1. Refund")
            print("2. Add Product to Inventory")

            choice = safe_input("Enter choice (or type 'exit' to cancel): ")
            if choice is None:
                print("Operation canceled. Returning to Employee Menu.")
                break

            if choice == "1":
                chk.refund()

            elif choice == "2":
                inv.add_product(role)
            else:
                print(" Invalid choice. Please try again.")