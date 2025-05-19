from database import Database
from aisle import Aisle
from utils import generate_id, safe_input


class Inventory:
    def __init__(self):
        self.db = Database()
        self.aisle_manager = Aisle()

    def add_product(self,role):
        """
        Add a product with aisle assignment, automatically creating aisles if necessary.

        Args:
            role (str): Role of the user (only 'Manager' can create new aisles).

        Returns:
            bool: True if the product is added successfully, False otherwise.
        """
        name, category, quantity, price, aisle_name =get_input_add_product()
        # Validate input types and values
        if not isinstance(name, str) or not name.strip():
            print(" Error: Product name must be a non-empty string.")
            return False
        if not isinstance(category, str) or not category.strip():
            print(" Error: Category must be a non-empty string.")
            return False
        if not isinstance(aisle_name, str) or not aisle_name.strip():
            print(" Error: Aisle name must be a non-empty string.")
            return False
        try:
            quantity = int(quantity)
            if quantity <= 0:
                print(" Error: Quantity must be a positive integer.")
                return False
        except (ValueError, TypeError):
            print(" Error: Quantity must be a valid integer.")
            return False
        try:
            price = float(price)
            if price <= 0:
                print(" Error: Price must be a positive number.")
                return False
        except (ValueError, TypeError):
            print(" Error: Price must be a valid number.")
            return False


        name = name.strip()
        category = category.strip()
        aisle_name = aisle_name.strip()

        # Check if aisle exists; if not, only a Manager can create it
        try:
            aisle_exists = self.aisle_manager.aisle_exists(aisle_name)
        except Exception as e:
            print(f" Error checking aisle existence: {e}")
            return False

        if not aisle_exists:
            if role != "Manager":
                print(" Error: Only managers can add products to a new aisle.")
                return False
            # Create aisle if it doesn't exist
            self.aisle_manager.add_aisle(aisle_name)

        # Add product to inventory
        try:
            product_id = generate_id(name, "inventory", self.db)
            if not product_id:
                print(" Error: Failed to generate a valid product ID.")
                return False

            query = (
                "INSERT INTO inventory (id, name, category, quantity, price, aisle_name) "
                "VALUES (?, ?, ?, ?, ?, ?)"
            )
            self.db.execute_query(query, (product_id, name, category, quantity, price, aisle_name))

            # Update the aisle's product list without leaving trailing commas
            update_aisle_query = (
                "UPDATE aisles "
                "SET product_name = TRIM(COALESCE(product_name, '') || "
                "CASE WHEN product_name IS NULL OR TRIM(product_name) = '' THEN '' ELSE ', ' END || ?) "
                "WHERE name = ?"
            )
            self.db.execute_query(update_aisle_query, (name, aisle_name))

            print(f" Product '{name}' added to Aisle '{aisle_name}' with ID: {product_id}.")
            return True
        except Exception as e:
            print(f" An error occurred while adding the product: {e}")
            return False

    def update_stock(self):
        """
        Update product stock.
        Args:
        """
        while True:
            product_id = safe_input("Enter Product ID (Press 'exit' to discard process): ")
            if product_id is None:
                print("Returning to Employee Menu.")
                return

            if not isinstance(product_id, str) or not product_id.strip():
                print(" Error: Product ID must be a non-empty string.")
                continue

            quantity = safe_input("Enter Product Quantity (Press 'exit' to discard process): ")
            if quantity is None:
                print("Returning to Employee Menu.")
                return

            try:
                quantity = int(quantity)
                if quantity < 0:
                    print(" Error: Quantity cannot be negative.")
                    continue
            except (ValueError, TypeError):
                print(" Error: Quantity must be a valid integer.")
                continue

            # If input is valid, update the database
            product_id = product_id.strip()
            try:
                query = "UPDATE inventory SET quantity = quantity + ? WHERE id=?"
                self.db.execute_query(query, (quantity, product_id))
                print(f" Stock updated for Product ID: {product_id}.")
                break  # Exit loop after successful update
            except Exception as e:
                print(f" Error updating stock: {e}")


def get_input_add_product():
    """Takes required input from user to add product to inventory"""
    while True:
        prod_name = safe_input("Enter Product Name (or 'exit' to cancel): ")
        if prod_name is None:
            print("Returning to Employee Menu.")
            return
        category = safe_input("Enter Category (or 'exit' to cancel): ")
        if category is None:
            print("Returning to Employee Menu.")
            return
        qty_input = safe_input("Enter Quantity (or 'exit' to cancel): ")
        if qty_input is None:
            print("Returning to Employee Menu.")
            return
        price_input = safe_input("Enter Price (or 'exit' to cancel): ")
        if price_input is None:
            print("Returning to Employee Menu.")
            return
        aisle_name = safe_input("Enter Aisle Name (or 'exit' to cancel): ")
        if aisle_name is None:
            print("Returning to Employee Menu.")
            return
        try:
            qty = int(qty_input)
            price = float(price_input)
        except ValueError:
            print(" Invalid input for quantity or price. Please enter numeric values.")
            continue
        return  prod_name, category, qty, price, aisle_name


