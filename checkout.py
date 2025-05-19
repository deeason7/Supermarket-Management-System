import random
import string
from datetime import datetime, timedelta
from database import Database
from utils import safe_input
from customer import Customer
from employee import Employee
emp  = Employee()


class Checkout:
    def __init__(self):
        self.db = Database()

    def calculate_cart_total(self, cart):
        """Calculates total cost before discounts and tax.
           For the special 'membership' item, we use a fixed fee of $50.
        """
        cart_total = 0
        for item in cart:
            name, quantity = item["name"], item["quantity"]

            if name.lower() == "membership":
                # fixed fee for membership; no stock check
                sold_price = 50.0
                item["sold_price"] = sold_price
                cart_total += sold_price * quantity
            else:
                product = self.db.fetch_query("SELECT price, quantity FROM inventory WHERE name=?", (name,))
                if product:
                    price, stock = product[0]
                    if quantity > stock:
                        print(f" Not enough stock for '{name}'! Available: {stock}")
                        return None
                    sold_price = price  # record the current price as the sold price
                    item["sold_price"] = sold_price
                    cart_total += sold_price * quantity
                else:
                    print(f" Product '{name}' not found!")
                    return None
        return cart_total

    def calculate_discount(self, customer_id, cart_total, processing_employee_id=None):
        """
        Applies discounts based on the following rules:
         - If processed through employee checkout (processing_employee_id is provided)
           and the customer is an employee (exists in the employees table) and is not the
           same as the processing employee, apply a 20% discount.
         - Otherwise, if the customer is a premium member, apply a 3% discount.
        """
        discount = 0
        discount_percentage = 0

        # Check for employee discount only if processing_employee_id is provided
        if processing_employee_id is not None:
            # Cross validate: check if customer exists in employees table
            employee_check = self.db.fetch_query("SELECT id FROM employees WHERE id=?", (customer_id,))
            if employee_check:
                if processing_employee_id != customer_id:
                    discount = 0.20  # 20% discount
                    discount_percentage = 20
                else:
                    print(" Self-checkout discount is not allowed. No employee discount applied.")

        # if no employee discount, check for premium membership discount
        if discount == 0:
            member = self.db.fetch_query("SELECT membership FROM customers WHERE id=?", (customer_id,))
            if member and member[0][0] == "Premium":
                discount = 0.03  # 3% discount for premium members
                discount_percentage = 3

        discount_amount = cart_total * discount
        total_after_discount = cart_total - discount_amount
        return total_after_discount, discount_percentage, discount_amount

    @staticmethod
    def calculate_total_after_tax(total_after_discount, tax_rate=0.08):
        """Applies tax after discount."""
        tax_amount = total_after_discount * tax_rate
        return total_after_discount + tax_amount, tax_amount

    @staticmethod
    def generate_reference_number():
        """Generates a unique 8-character alphanumeric reference number."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def process_self_checkout(self):
        """
        Handles self-checkout where customers can browse and select products.
        (No processing employee is involved, so no employee discount can be applied.)
        """
        cust = Customer()
        print("Press 1 to proceed to member checkout")
        print("Press 2 to proceed to anonymous checkout")
        user_choice_input = safe_input("Enter your choice (or 'exit' to cancel): ")
        if user_choice_input is None:
            print("Checkout canceled.")
            return

        try:
            user_choice = int(user_choice_input)
        except ValueError:
            print(" Invalid input. Please enter a valid number.")
            return

        if user_choice == 1:
            cust_name = safe_input("Please enter your name (or 'exit' to cancel): ")
            if cust_name is None:
                return
            customer_id, membership = cust.check_customer_details(cust_name)
            new_member = False
            if not customer_id:
                # Customer not found; create a new customer
                name = cust_name
                phone = safe_input("Enter phone number (or 'exit' to cancel): ")
                if phone is None:
                    return
                mem_input = safe_input("Enter 'Yes' if you want to be a premium member (or 'exit' to cancel): ")
                if mem_input is None:
                    return
                if mem_input.lower() == "yes":
                    cust.add_customer(name, phone, "Premium")
                    new_member = True
                else:
                    cust.add_customer(name, phone, "Regular")
                customer_id, membership = cust.check_customer_details(name)
            print(f"Welcome, {cust_name}! Proceeding with member checkout...")
            self._self_checkout_process(customer_id, membership=membership,new_member = new_member)
        elif user_choice == 2:
            # Generate a reference number for anonymous checkout.
            customer_id = self.generate_reference_number()
            print("Proceeding with anonymous checkout...")
            self._self_checkout_process(customer_id, membership="Anonymous")
        else:
            print(f" {user_choice} is not a valid option. Please choose again.")
            return

    def _self_checkout_process(self, customer_id, membership="None",new_member=None):
        """
        Internal method to process the self-checkout (either member or anonymous).
        Handles cart, product selection, and payment.
        """
        cart = []
        while True:
            product_name = input("Enter product name to add to cart (or -1 to finish): ").strip()
            if product_name == "-1":
                break
            if not product_name:
                print("Product name cannot be empty.")
                continue

            try:
                quantity = int(input("Enter quantity: "))
                if quantity <= 0:
                    print("Quantity must be greater than 0.")
                    continue
                cart.append({"name": product_name, "quantity": quantity})
            except ValueError:
                print("Invalid quantity. Please enter a valid number.")

        if new_member:
            cart.append({"name": "membership", "quantity": 1, "sold_price": 50.0})

        if not cart:
            print("No items in cart. Checkout canceled.")
            return

        payment_method = input("Choose payment method (Cash/Card): ").strip()
        self.process_payment(
            customer_id=customer_id,
            employee_id=None,
            cart=cart,
            payment_method=payment_method,
            membership=membership,
        )

    def employee_checkout_flow(self):
        """
        Handles the employee checkout flow:
        - Validates the employee login.
        - Prompts the employee to choose member or anonymous checkout.
        - For member checkout, validates or creates the customer.
        - Proceeds to process the employee checkout.
        """
        cust = Customer()
        try:
            # Validate employee login
            employee_info = emp.employee_login_validation()  # Assumes emp is defined/imported elsewhere
            if not employee_info or employee_info[0] is None:
                return  # Login failed; exit the flow

            employee_id = employee_info[0]

            # Prompt for checkout type
            print("Press 1 to proceed to member checkout")
            print("Press 2 to proceed to anonymous checkout")
            user_choice_input = safe_input("Enter your choice (or 'exit' to cancel): ")
            if user_choice_input is None:
                return

            try:
                user_choice = int(user_choice_input)
            except ValueError:
                print(" Invalid input. Please enter a valid number.")
                return

            if user_choice == 1:
                # Member checkout: validate customer details
                cust_name = safe_input("Please enter customer name (or 'exit' to cancel): ")
                if cust_name is None:
                    return

                customer_id, membership = cust.check_customer_details(cust_name)
                new_member = False
                if customer_id:
                    self.process_employee_checkout(employee_id, customer_id, membership)
                else:
                    # If customer not found, collect details and create a new customer record
                    name = safe_input("Enter name (or 'exit' to cancel): ")
                    if name is None:
                        return
                    phone = safe_input("Enter phone number (or 'exit' to cancel): ")
                    if phone is None:
                        return
                    mem_input = safe_input(
                        "Enter 'Yes' if customer wants to be premium member (or 'exit' to cancel): "
                    )
                    if mem_input is None:
                        return
                    if mem_input.lower() == "yes":
                        cust.add_customer(name, phone, "Premium")
                        new_member = True
                    else:
                        cust.add_customer(name, phone, "Regular")
                    customer_id, membership = cust.check_customer_details(name)
                    if customer_id:
                        self.process_employee_checkout(employee_id, customer_id, membership,new_member)
            elif user_choice == 2:
                # Anonymous checkout: generate a reference number as customer_id
                customer_id = self.generate_reference_number()
                membership = "Anonymous"
                self.process_employee_checkout(employee_id, customer_id, membership)
            else:
                print(f" {user_choice} is not a valid option. Please choose again.")
        except Exception as e:
            print(f" Error: {e}")

    def process_employee_checkout(self, employee_id, customer_id, membership, new_member = None):
        """
        Handles checkout processed by an employee.
        An employee discount (20%) is applied only if:
        - The customer is an employee (found in the employees table), and
        - The processing employee is not the same as the customer.
        """
        cart = []
        while True:

            product_name = input("Enter product name to add to cart (or -1 to finish): ").strip()
            if product_name == "-1":
                break
            if not product_name:
                print("Product name cannot be empty.")
                continue

            try:
                quantity = int(input("Enter quantity: "))
                if quantity <= 0:
                    print("Quantity must be greater than 0.")
                    continue
                cart.append({"name": product_name, "quantity": quantity})
            except ValueError:
                print("Invalid quantity. Please enter a valid number.")

        if new_member:
            cart.append({"name": "membership", "quantity": 1, "sold_price": 50.0})

        if not cart:
            print("No items in cart. Checkout canceled.")
            return

        payment_method = input("Choose payment method (Cash/Card): ").strip()
        self.process_payment(employee_id, customer_id, cart, payment_method, membership)

    def process_payment(self, employee_id, customer_id, cart, payment_method, membership):
        """Handles payment, updates inventory, and prints a bill."""
        # Validate payment method early
        if payment_method.lower() not in ["cash", "card"]:
            print(" Invalid payment method! Transaction canceled.")
            return False

        total = self.calculate_cart_total(cart)
        if total is None:
            print(" Transaction failed due to stock issues.")
            return False

        # For employee checkout, pass the processing employee ID; for self checkout, this will be None.
        discounted_total, discount_percentage, discount_amount = self.calculate_discount(
            customer_id, total, processing_employee_id=employee_id
        )

        # Apply tax on the discounted total
        total_after_tax, tax_amount = self.calculate_total_after_tax(discounted_total)

        # Add a 2% transaction fee if payment is by card
        transaction_fee = 0
        if payment_method.lower() == "card":
            transaction_fee = total_after_tax * 0.02
        final_total = total_after_tax + transaction_fee

        # Build an items_detail string with sold price for each item (format: name:quantity:sold_price)
        items_detail = ", ".join([f"{item['name']}:{item['quantity']}:{item['sold_price']:.2f}" for item in cart])
        reference_number = self.generate_reference_number()

        print(f"Applying {discount_percentage}% discount (-${discount_amount:.2f}). "
              f"Tax applied after discount: +${tax_amount:.2f}.", end=" ")
        if transaction_fee:
            print(f"Card transaction fee (2%): +${transaction_fee:.2f}.", end=" ")
        print(f"Final Amount: ${final_total:.2f}")

        print(f" Payment successful ({payment_method.capitalize()}).")

        # Build item detail and total quantity for sales record
        total_quantity = sum(item['quantity'] for item in cart)

        # Insert the sale into the database
        try:
            query = (
                "INSERT INTO sales (employee_id, customer_id, items, quantity, tax, discount, total, membership, reference_number, payment_method) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )
            self.db.execute_query(query, (
                employee_id if employee_id is not None else None,
                customer_id,
                items_detail,
                total_quantity,
                f"{tax_amount:.2f}",
                f"{discount_amount:.2f}",
                f"{final_total:.2f}",
                membership,
                reference_number,
                payment_method
            ))
        except Exception as e:
            print(f"Error inserting sale into database: {e}")
            return False

        # Update the inventory for each purchased item (skip updating inventory for membership fee)
        for item in cart:
            if item["name"].lower() == "membership":
                continue
            try:
                self.db.execute_query("UPDATE inventory SET quantity = quantity - ? WHERE name = ?",
                                      (item["quantity"], item["name"]))
            except Exception as e:
                print(f"Error updating inventory for '{item['name']}': {e}")
                continue

        print(" Inventory updated successfully.")
        self.print_bill(cart, total, discount_percentage, discount_amount, discounted_total,
                        tax_amount, transaction_fee, final_total, reference_number, payment_method, membership)
        return True

    def print_bill(self, cart, subtotal, discount_percentage, discount_amount, total_after_discount,
                   tax_amount, transaction_fee, final_total, reference_number, payment_method, membership, is_refund=False, refund_reference=None):
        """Prints a detailed bill receipt with itemized costs, membership status,
           discount, tax, and transaction fee details.
        """
        print("\n===============================")
        if is_refund:
            print("          REFUND RECEIPT        ")
        else:
            print("          SUPERMARKET        ")
        print("===============================")
        print(f"Ref No: {reference_number}")
        if is_refund and refund_reference:
            print(f"Refund Ref: {refund_reference}")
        print(f"Membership Status: {membership}")
        if is_refund and refund_reference:
            print(f"Items Refunded:")
        else:
            print("Items Purchased:")

        # For each item, use the sold_price stored in the cart if available.
        for item in cart:
            unit_price = item.get("sold_price")
            if unit_price is None:
                # Fallback: fetch current price from inventory (might not match the sale price)
                product = self.db.fetch_query("SELECT price FROM inventory WHERE name=?", (item['name'],))
                unit_price = product[0][0] if product and product[0] else 0
            item_total = unit_price * item['quantity']
            refund_note = " (Refunded)" if is_refund else ""
            print(f"- {item['name']} x{item['quantity']} @ ${unit_price:.2f} each = ${item_total:.2f}{refund_note}")

        print("-------------------------------")
        print(f"Subtotal: ${subtotal:.2f}")
        print(f"Discount ({discount_percentage}%): -${discount_amount:.2f}")
        print(f"Total after discount: ${total_after_discount:.2f}")
        print(f"Tax (8%): +${tax_amount:.2f}")
        if transaction_fee:
            print(f"Card Transaction Fee (2%): +${transaction_fee:.2f}")
        print(f"Final Total: ${final_total:.2f}")
        print(f"Payment Method: {payment_method.capitalize()}")
        print("===============================")
        if is_refund:
            print("      Refund Processed        ")
        else:
            print("     Thank you for shopping!   ")
        print("===============================\n")

    def refund(self):
        """Processes a refund for a previous purchase."""
        print("Want a refund on purchase? Make sure your items were purchased within the last 7 days.")
        reference_no = safe_input("Enter the reference number of previous bill (Enter exit to void process): ")
        if reference_no is None:
            print("Refund process aborted.")
            return

        # Fetch the sale record by reference number
        sale_record = self.db.fetch_query(
            "SELECT id, employee_id, customer_id, items, quantity, total, date, remarks, payment_method FROM sales WHERE reference_number = ?",
            (reference_no,)
        )
        if not sale_record:
            print(" Sale record not found.")
            return
        sale = sale_record[0]
        sale_id = sale[0]
        sale_employee_id = sale[1]
        sale_customer_id = sale[2]
        sale_items_str = sale[3]  # format: "name:quantity:price, name2:quantity:price, ..."
        sale_total = float(sale[5])
        sale_date_str = sale[6]
        sale_payment_method = sale[8]
        sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")

        # Check refund period
        if datetime.now() - sale_date > timedelta(days=7):
            print(" Refund period expired. Refunds are only accepted within 7 days of purchase.")
            return

        # Do not allow refund if the customer is an employee
        if self.db.fetch_query("SELECT id FROM employees WHERE id=?", (sale_customer_id,)):
            print(" Refund not allowed for employee customers.")
            return

        # Ask for refund processor's employee id for authorization
        refund_processor = safe_input("Enter your employee ID for refund processing: ")
        if sale_employee_id is not None and str(sale_employee_id) == refund_processor:
            print(" You cannot process a refund for your own sale.")
            return

        # Parse the sale items into two dictionaries: one for refundable quantities and one for the sold prices.
        sale_items = {}
        sale_prices = {}
        for part in sale_items_str.split(","):
            if part.strip():
                tokens = part.split(":")
                if len(tokens) >= 2:
                    item_name = tokens[0].strip()
                    try:
                        qty = int(tokens[1].strip())
                    except ValueError:
                        continue
                    if len(tokens) == 3:
                        try:
                            sold_price = float(tokens[2].strip())
                        except ValueError:
                            sold_price = None
                    else:
                        sold_price = None
                    sale_items[item_name] = qty
                    sale_prices[item_name] = sold_price

        refund_items = {}
        total_refund_amount = 0
        while True:
            input_str = safe_input("Enter the item you want to refund and quantity (format: item,quantity) (Enter exit to finish): ")
            if input_str is None or input_str.lower() == "exit":
                break
            try:
                item_name, qty_str = input_str.split(",")
                item_name = item_name.strip()
                refund_qty = int(qty_str.strip())
                if item_name not in sale_items:
                    print(f" Item '{item_name}' was not part of the original sale.")
                    continue
                if refund_qty > sale_items[item_name]:
                    print(f" Refund quantity for '{item_name}' exceeds refundable quantity ({sale_items[item_name]}).")
                    continue
                # Do not allow refunding membership fee
                if item_name.lower() == "membership":
                    print(" Membership fee cannot be refunded.")
                    continue
                # Use the sold price from the original sale
                sold_price = sale_prices.get(item_name)
                if sold_price is None:
                    # Fallback (should rarely happen)
                    product = self.db.fetch_query("SELECT price FROM inventory WHERE name=?", (item_name,))
                    sold_price = product[0][0] if product and product[0] else 0
                refund_amount = sold_price * refund_qty
                total_refund_amount += refund_amount
                # Accumulate refund items
                if item_name in refund_items:
                    refund_items[item_name] += refund_qty
                else:
                    refund_items[item_name] = refund_qty
                # Adjust remaining refundable quantity for this item to avoid over-refunding
                sale_items[item_name] -= refund_qty
            except Exception as e:
                print(f"Invalid input. Please enter in the format: item,quantity {e}")
                continue

        if not refund_items:
            print("No valid refund items entered. Refund process aborted.")
            return

        # Check refund amount limit for employee-processed refunds
        if total_refund_amount > 200:
            manager_check = self.db.fetch_query("SELECT role FROM employees WHERE id=?", (refund_processor,))
            if not manager_check or manager_check[0][0].lower() != "manager":
                print(" Refund amount exceeds $200. Please have a manager process this refund.")
                return

        # Generate a refund reference number
        refund_ref = self.generate_reference_number()

        # Update inventory: add refunded quantities back (skip membership)
        for item, qty in refund_items.items():
            try:
                self.db.execute_query("UPDATE inventory SET quantity = quantity + ? WHERE name = ?", (qty, item))
            except Exception as e:
                print(f"Error updating inventory for '{item}': {e}")

        # Update the original sale record with refund remarks
        existing_remarks = sale[7] if sale[7] else ""
        updated_remarks = (existing_remarks + " | " if existing_remarks else "") + f"Refunded: {refund_items} (Refund Ref: {refund_ref})"
        try:
            self.db.execute_query("UPDATE sales SET remarks = ? WHERE id = ?", (updated_remarks, sale_id))
        except Exception as e:
            print(f"Error updating sale record remarks: {e}")

        # Insert a new sales record for the refund with negative values.
        # Note: Tax, discount, and transaction fee are not refunded.
        refund_items_detail = ", ".join([f"{item}:{qty}:{sale_prices.get(item, 0):.2f}" for item, qty in refund_items.items()])
        total_refund_qty = sum(refund_items.values())
        negative_total = -total_refund_amount
        try:
            query = (
                "INSERT INTO sales (employee_id, customer_id, items, quantity, tax, discount, total, membership, reference_number, payment_method, remarks) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )
            self.db.execute_query(query, (
                refund_processor,         # Processed by refund employee
                sale_customer_id,
                refund_items_detail,
                -total_refund_qty,        # Negative quantity for refund
                "0.00",                   # No tax refunded
                "0.00",                   # No discount refunded
                f"{negative_total:.2f}",  # Negative total refund amount
                "",                       # Membership left blank for refund
                refund_ref,               # Refund reference as the new reference_number
                "refund",                 # Payment method set as refund
                "Refund Transaction"      # Remarks for refund transaction
            ))
        except Exception as e:
            print(f"Error inserting refund record into database: {e}")
            return

        print(" Refund processed successfully.")
        # Print refund bill with a refund header
        # Build a cart-like list from refund_items for printing
        refund_cart = []
        for item, qty in refund_items.items():
            refund_cart.append({"name": item, "quantity": qty, "sold_price": sale_prices.get(item, 0)})
        self.print_bill(
            cart=refund_cart,
            subtotal=total_refund_amount,
            discount_percentage=0,
            discount_amount=0,
            total_after_discount=total_refund_amount,
            tax_amount=0,
            transaction_fee=0,
            final_total=negative_total,
            reference_number=reference_no,
            payment_method="refund",
            membership="",
            is_refund=True,
            refund_reference=refund_ref
        )
