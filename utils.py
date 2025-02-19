import random

def generate_id(name, table_name, db):
    """
    Generate a unique 4-character ID using:
    - First letter of the name (uppercase).
    - 3 random digits.

    Ensures uniqueness by checking the database.

    Args:
    - name (str): The name from which to generate the ID.
    - table_name (str): The database table to check uniqueness.
    - db (Database): The database instance to execute queries.

    Returns:
    - str: A unique 4-character ID.
    """
    # Ensure the name is not empty
    if not name:
        raise ValueError("Name cannot be empty")

    first_letter = name[0].upper()

    while True:
        # Generate a 3-digit number
        unique_number = random.randint(100, 999)
        generated_id = f"{first_letter}{unique_number}"

        # Check if ID already exists in the given table
        query = f"SELECT COUNT(*) FROM {table_name} WHERE id = ?"
        result = db.fetch_query(query, (generated_id,))

        if result[0][0] == 0:  # If the ID is unique, return it
            return generated_id


def display_welcome():
    """Displays a welcome message with ASCII art, a quote, and emojis."""

    print("****************************************")
    print("*                                      *")
    print("*      Welcome to Our Supermarket!     *")
    print("*                                      *")
    print("****************************************")

    print("  ___________________________________")
    print(" |                                   |")
    print(" |   🍎   🥛   🍞   🥦   🧼    🍪   |")
    print(" |  ---- ---- ---- ----  ----  ----  |")
    print(" |$1.99 $3.49 $2.75 $0.99 $4.29 $2.50|")
    print(" |___________________________________|")
    print("     ||     ||     ||     ||     ||    ")
    print("     ||     ||     ||     ||     ||    ")
    print("    /__\\  /__\\  /__\\  /__\\  /__\\  ")

    print("\n\"The best place to find yourself is at the grocery store.\" 🛒")

    print("\nWe hope you have a pleasant shopping experience!")


def safe_input(prompt):
    """
    Get user input and allow the user to cancel the current operation by typing 'exit'.
    If the input is blank, continue prompting. Otherwise, return the input.

    Returns:
        None if the user types 'exit' (case-insensitive).
        The input string if it's not blank or 'exit'.
    """
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            continue  # If input is blank, keep asking
        if user_input.lower() == "exit":
            return None  # Exit condition
        return user_input  # Return valid input
