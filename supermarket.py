from employee import Employee
from checkout import Checkout
from employee_functions import supermarket_employee
from aisle import Aisle
from utils import display_welcome, safe_input

def supermarket_program():
    """Main function that keeps all other functions connected"""
    emp =Employee()
    aisle = Aisle()
    chk = Checkout()
    display_welcome()

    default_menu_choices = [
        "Display All Product",
        "Display aisle items",
        "Self-Check Out",
        "Employee Check Out",
        "Employee Menu",
        "Exit program"
    ]
    while True:
        print("\n#--------------------------------------------------------------------------------#")
        print("--- Main Menu ---")
        for i, choice_text in enumerate(default_menu_choices, start=1):
            print(f"{i}. {choice_text}")
        print()

        main_choice = safe_input("Enter your choice (or 'exit' to quit): ")
        if main_choice is None:
            print("Exiting program.")
            break
        try:
            choice = int(main_choice)
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
            continue

        if 1 <= choice <= len(default_menu_choices):
            if choice == len(default_menu_choices):
                print("Exiting Program.")
                break
            else:
                print(f"You chose: {default_menu_choices[choice - 1]}")
                if choice == 1:
                    aisle.display_aisles_with_products()

                elif choice == 2:
                    aisle.get_products_in_aisle()

                elif choice == 3:
                   chk.process_self_checkout()

                elif choice == 4:
                    chk.employee_checkout_flow()

                elif choice == 5:
                    emp.setup_manager_data()
                    supermarket_employee()

                else:
                    print("❌ Invalid choice. Please try again.")
        else:
            print("❌ Invalid choice. Please try again.")

