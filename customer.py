from database import Database
from utils import generate_id


class Customer:
    def __init__(self):
        self.db = Database()

    def add_customer(self, name="Unknown", phone="00000", membership="Regular"):
        """Add a new customer with an optional membership level and unique ID."""
        # Validate input parameters
        if not isinstance(name, str) or not name.strip():
            print("❌ Customer name must be a non-empty string.")
            return
        if not isinstance(phone, str) or not phone.strip():
            print("❌ Phone must be a valid non-empty string.")
            return

        # Normalize inputs
        name = name.strip()
        phone = phone.strip()
        membership = membership.strip() if isinstance(membership, str) else "Regular"

        # Generate a unique customer ID
        customer_id = generate_id(name, "customers", self.db)
        if not customer_id:
            print("❌ Failed to generate a valid customer ID.")
            return

        # Insert the customer into the database
        query = "INSERT INTO customers (id, name, phone, membership) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute_query(query, (customer_id, name, phone, membership))
            print(f"✅ Customer '{name}' (ID: {customer_id}) added as {membership} member.")
        except Exception as e:
            print(f"❌ Error adding customer: {e}")


    def check_customer_details(self, name):
        """Check if customer details exist in the database and return ID and membership."""
        if not isinstance(name, str) or not name.strip():
            print("❌ Customer name must be a non-empty string.")
            return None, None

        name = name.strip()
        query = "SELECT id, membership FROM customers WHERE name = ?"
        try:
            result = self.db.fetch_query(query, (name,))
            if result:
                customer_id, membership = result[0]
                return customer_id, membership
            else:
                print("ℹ️ Customer not found. Please provide your details to register.")
                return None, None
        except Exception as e:
            print(f"❌ Error checking customer details: {e}")
            return None, None
