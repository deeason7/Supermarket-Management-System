import hashlib
from utils import generate_id
from database import Database
from utils import  safe_input


class Employee:
    def __init__(self):
        self.db = Database()

    @staticmethod
    def hash_password(password):
        """Hash a password using SHA‑256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def setup_manager_data(self):
        """Set up Manager details if none exist in the database."""
        try:
            result = self.db.fetch_query("SELECT COUNT(*) FROM employees WHERE role ='Manager'")
            employees_exist = result[0][0] if result else 0
        except Exception as e:
            print(f" Error checking for manager existence: {e}")
            return

        if employees_exist == 0:
            print("No managers found! Please add a manager to start the system.")
            name = safe_input("Enter Manager Name (or 'exit' to cancel): ")
            password = safe_input("Enter Password (or 'exit' to cancel): ")
            if not name or not password:
                print("Operation canceled.")
                return
            self.add_employee(name=name, role="Manager", password=password)
        # Close the database to end the connection here.
        # self.db.close()

    def add_employee(self, role, name=None, password=None):
        """Add an employee (Manager or Employee) with a hashed password."""

        if role not in ["Manager", "Employee"]:
            print(" Role must be either 'Manager' or 'Employee'.")
            return

        while name is None:
            name = safe_input("Enter Name (or 'exit' to cancel): ")
            if name is None:
                print("Returning to Employee Menu.")
                return
            if not name.strip():
                print(" Employee name must be a non-empty string.")
                name = None

        while password is None:
            password = safe_input("Enter Password (or 'exit' to cancel): ")
            if password is None:
                print("Returning to Employee Menu.")
                return
            if not password.strip():
                print(" Password must be a non-empty string.")
                password = None

        # Sanitize inputs
        name = name.strip()
        password = password.strip()
        hashed_password = self.hash_password(password)

        # Generate a unique employee ID
        emp_id = generate_id(name, "employees", self.db)
        if not emp_id:
            print(" Failed to generate a valid employee ID.")
            return

        query = "INSERT INTO employees (id, name, role, password) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute_query(query, (emp_id, name, role, hashed_password))
            print(f" Employee '{name}' ({role}) added successfully with ID: {emp_id}.")
        except Exception as e:
            print(f" Error adding employee: {e}")

    def verify_credentials(self, emp_id, password):
        """
        Verify employee credentials.
        Returns a tuple (status, role) where:
          - status is 'success', 'wrong_password', or 'not_found'
          - role is the employee's role (or None if not found)
        """
        if not (isinstance(emp_id, str) and emp_id.strip()):
            return "not_found", None

        emp_id = emp_id.strip()
        query = "SELECT role, password FROM employees WHERE id=?"
        try:
            result = self.db.fetch_query(query, (emp_id,))
        except Exception as e:
            print(f" Error fetching employee data: {e}")
            return "not_found", None

        if not result:
            return "not_found", None

        role, stored_hashed_password = result[0]
        if self.hash_password(password) == stored_hashed_password:
            return "success", role
        else:
            return "wrong_password", role

    def remove_employee(self):
        """Remove an employee only if they exist in the database."""
        emp_id = safe_input("Enter Employee ID to remove (or 'exit' to cancel): ")
        if emp_id is None:
            print("Returning to Employee Menu.")
            return

        # Validate Employee ID
        if not isinstance(emp_id, str) or not emp_id.strip():
            print(" Employee ID must be a non‑empty string.")
            return
        emp_id = emp_id.strip()

        # Check if the employee exists
        check_query = "SELECT * FROM employees WHERE id=?"
        employee = self.db.fetch_query(check_query, (emp_id,))

        if not employee:
            print(f" Employee {emp_id} not found in the database.")
            return

        # Proceed with deletion
        delete_query = "DELETE FROM employees WHERE id=?"
        try:
            self.db.execute_query(delete_query, (emp_id,))
            print(f" Employee {emp_id} removed successfully.")
        except Exception as e:
            print(f" Error removing employee {emp_id}: {e}")

    def unlock_system(self):
        """Prompt for manager credentials to unlock the system."""
        print(" System is locked due to multiple failed login attempts.")
        print("Manager override required to unlock the system.")
        manager_id = input("Enter Manager ID: ").strip()
        manager_password = input("Enter Manager Password: ").strip()
        status, role = self.verify_credentials(manager_id, manager_password)
        return status == "success" and role == "Manager"

    def employee_login_validation(self):
        """
        Handle employee login authentication.
        For non-managers: after three failed attempts, require a manager override.
        For managers: exit immediately on failure.
        """
        print("\n🔹 Supermarket Management System 🔹")
        login_attempts = 0
        while True:
            emp_id = input("Enter Employee ID: ").strip()
            password = input("Enter Password: ").strip()
            status, role = self.verify_credentials(emp_id, password)
            if status == "success":
                print(f" Logged in as {role}.")
                return emp_id, role
            else:
                login_attempts += 1
                print(f" Invalid credentials. Attempt {login_attempts}/3.")
                if login_attempts >= 3:
                    if self.unlock_system():
                        login_attempts = 0
                        print(" System unlocked. Please try logging in again.")
                    else:
                        print(" Unlock failed. Please contact tech support.")
                        exit(1)


