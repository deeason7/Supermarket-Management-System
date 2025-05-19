"""
Aisle Management Module

This module provides functionality for managing aisles in a supermarket system.
It supports checking aisle existence, adding new aisles, retrieving aisle names,
and fetching products within a specific aisle.

Dependencies:
- Database: Handles database interactions.
- Utils (generate_id): Generates unique identifiers for new aisles.
"""

from database import Database
from utils import generate_id, safe_input


class Aisle:
    """
    Aisle class for managing supermarket aisles.

    Attributes:
        db (Database): Instance of the Database class to interact with the database.
    """

    def __init__(self):
        """Initialize the Aisle class with a database connection."""
        self.db = Database()

    def aisle_exists(self, name):
        """
        Check if an aisle exists in the database.

        Args:
            name (str): The name of the aisle.

        Returns:
            bool: True if the aisle exists, False otherwise.
        """
        if not isinstance(name, str) or not name.strip():
            print(" Aisle name must be a non-empty string.")
            return False
        query = "SELECT id FROM aisles WHERE name = ?"
        try:
            result = self.db.fetch_query(query, (name,))
            return bool(result)
        except Exception as e:
            print(f"Error checking aisle existence: {e}")
            return False


    def add_aisle(self, name=None):
        """
        Add a new aisle to the database if it does not already exist.
        """
        if name is None:
            while True:
                name = safe_input("Enter Aisle Name (or 'exit' to cancel): ")
                if name is None:
                    print("Returning to Employee Menu.")
                    return
                if not isinstance(name, str) or not name.strip():
                    print("❌ Aisle name must be a non-empty string.")
                    continue
                name = name.strip()
                break

        if self.aisle_exists(name):
            print(f"✅ Aisle '{name}' already exists.")
            return

        # Create a new aisle.
        aisle_id = generate_id(name, "aisles", self.db)
        if not aisle_id:
            print("❌ Failed to generate a valid aisle ID.")
            return

        query = "INSERT INTO aisles (id, name, product_name) VALUES (?, ?, '')"
        try:
            self.db.execute_query(query, (aisle_id, name))
            print(f"✅ Aisle '{name}' added with ID: {aisle_id}.")
        except Exception as e:
            print(f"❌ Error adding aisle: {e}")

    def display_aisles_with_products(self):
        """Display aisles and their respective products with prices."""
        try:
            aisles = self.get_all_aisle_name()
            if not aisles:
                print("ℹ️ No aisle is set up. Store manager is working on it.")
            else:
                for aisle_name in aisles:
                    print("#---------------------------------------------------------#")
                    print(f"Aisle: {aisle_name}")
                    self.get_products_in_aisle(aisle_name)
        except Exception as e:
            print(f"❌ Error: {e}")

    def get_all_aisle_name(self):
        """
        Retrieve all aisle names from the database.

        Returns:
            list: A list of aisle names as strings.
        """
        query = "SELECT name FROM aisles"
        try:
            result = self.db.fetch_query(query)
            return [row[0] for row in result]
        except Exception as e:
            print(f"❌ Error retrieving aisle names: {e}")
            return []

    def get_products_in_aisle(self, aisle_name=None):
        """
        Retrieve all products in a specific aisle, and allow the user to input an aisle to view products.

        Args:
            aisle_name (str, optional): The name of the aisle. If None, prompts user for aisle input.

        Returns:
            list: A list of tuples containing product name and price.
        """

        if aisle_name is None:
            # Allow user to input aisle name if not provided
            while True:
                aisle_input = safe_input("Enter aisle you want to look (or 'exit' to cancel): ")
                if aisle_input is None or not aisle_input.strip():
                    print("Exiting aisle selection.")
                    return []  # If input is 'exit' or invalid, return empty list
                aisle_name = aisle_input.strip()  # Assign valid aisle name from input
                break  # Exit loop after getting a valid aisle

        # Check if aisle name is valid
        if not isinstance(aisle_name, str) or not aisle_name.strip():
            print("❌ Aisle name must be a non-empty string.")
            return []

        # Query to get products in the aisle
        query = "SELECT name, price FROM inventory WHERE aisle_name = ?"
        try:
            result = self.db.fetch_query(query, (aisle_name,))
        except Exception as e:
            print(f"❌ Error fetching products for aisle '{aisle_name}': {e}")
            return []

        # If no products found
        if not result:
            print(f"ℹ️ No products found in Aisle '{aisle_name}'.")
            return []

        # Display the products with their prices
        print(f"Products in Aisle '{aisle_name}':")
        for product in result:
            try:
                price = float(product[1])
            except ValueError:
                print(f"❌ Invalid price for product {product[0]}. Skipping.")
                continue
            print(f"{product[0]} - ${price:.2f}")

        return result
