import pandas as pd
class SalesReportGenerator:
    def __init__(self, db):
        self.db = db

    def generate_reports(self, output_file='sales_report.xlsx'):
        """
        Generates an Excel file with multiple sheets:
          - Today Sales
          - Weekly Sales
          - Top Products
          - Top Employees
          - Overall Insights
        """
        # -----------------------------
        # Fetch sales data from the database
        # -----------------------------
        try:
            query_today = (
                "SELECT id, employee_id, customer_id, items, quantity, tax, discount, total, date, "
                "membership, reference_number, payment_method, remarks FROM sales "
                "WHERE date(date)=date('now')"
            )
            today_sales = self.db.fetch_query(query_today)
        except Exception as e:
            print(f"Error fetching today's sales: {e}")
            today_sales = []

        try:
            query_weekly = (
                "SELECT id, employee_id, customer_id, items, quantity, tax, discount, total, date, "
                "membership, reference_number, payment_method, remarks FROM sales "
                "WHERE date(date) >= date('now', '-7 days')"
            )
            weekly_sales = self.db.fetch_query(query_weekly)
        except Exception as e:
            print(f"Error fetching weekly sales: {e}")
            weekly_sales = []

        try:
            query_all = (
                "SELECT id, employee_id, customer_id, items, quantity, tax, discount, total, date, "
                "membership, reference_number, payment_method, remarks FROM sales"
            )
            all_sales = self.db.fetch_query(query_all)
        except Exception as e:
            print(f"Error fetching overall sales: {e}")
            all_sales = []

        # -----------------------------
        # Create DataFrames from the fetched data
        # -----------------------------
        columns_sales = ['id', 'employee_id', 'customer_id', 'items', 'quantity', 'tax',
                         'discount', 'total', 'date', 'membership', 'reference_number',
                         'payment_method', 'remarks']
        try:
            df_today = pd.DataFrame(today_sales, columns=columns_sales)
            df_weekly = pd.DataFrame(weekly_sales, columns=columns_sales)
            df_all = pd.DataFrame(all_sales, columns=columns_sales)
        except Exception as e:
            print(f"Error creating DataFrames: {e}")
            return

        # -----------------------------
        # Generate overall insights
        # -----------------------------

        # 1. Top Products: Aggregate quantity sold per product.
        product_sales = {}
        try:
            for items_str in df_all['items']:
                if not items_str:
                    continue
                # Expected format: "apple:2:1.00, banana:3:0.50" (each token: name:quantity:sold_price)
                for part in items_str.split(','):
                    part = part.strip()
                    if not part:
                        continue
                    tokens = part.split(':')
                    if len(tokens) >= 2:
                        product_name = tokens[0].strip()
                        try:
                            quantity = int(tokens[1].strip())
                        except ValueError:
                            continue
                        product_sales[product_name] = product_sales.get(product_name, 0) + quantity
            df_product_sales = pd.DataFrame(list(product_sales.items()),
                                            columns=['Product', 'Total Quantity Sold'])
            df_product_sales.sort_values(by='Total Quantity Sold', ascending=False, inplace=True)
        except Exception as e:
            print(f"Error generating top products data: {e}")
            df_product_sales = pd.DataFrame(columns=['Product', 'Total Quantity Sold'])

        # 2. Top Employees: Which employee made the most sales.
        try:
            df_emp = df_all[df_all['employee_id'].notna()].copy()
            if not df_emp.empty:
                # Convert employee_id to integer for grouping
                df_emp['employee_id'] = df_emp['employee_id']
                df_emp_grouped = df_emp.groupby('employee_id').agg(
                    sales_count=('id', 'count'),
                    total_sales=('total', 'sum')
                ).reset_index()
                df_emp_grouped.sort_values(by='total_sales', ascending=False, inplace=True)
            else:
                df_emp_grouped = pd.DataFrame(columns=['employee_id', 'sales_count', 'total_sales'])
        except Exception as e:
            print(f"Error generating top employees data: {e}")
            df_emp_grouped = pd.DataFrame(columns=['employee_id', 'sales_count', 'total_sales'])

        # 3. Overall Insights: Total sales, average sale, and number of transactions.
        try:
            overall_total_sales = df_all['total'].sum() if not df_all.empty else 0
            average_sale = df_all['total'].mean() if not df_all.empty else 0
            total_transactions = len(df_all)
            insights_data = {
                'Overall Total Sales': [overall_total_sales],
                'Average Sale Amount': [average_sale],
                'Total Transactions': [total_transactions]
            }
            df_overall = pd.DataFrame(insights_data)
        except Exception as e:
            print(f"Error generating overall insights: {e}")
            df_overall = pd.DataFrame()

        # -----------------------------
        # Write all DataFrames to an Excel file with multiple sheets.
        # -----------------------------
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df_today.to_excel(writer, sheet_name='Today Sales', index=False)
                df_weekly.to_excel(writer, sheet_name='Weekly Sales', index=False)
                df_product_sales.to_excel(writer, sheet_name='Top Products', index=False)
                df_emp_grouped.to_excel(writer, sheet_name='Top Employees', index=False)
                df_overall.to_excel(writer, sheet_name='Overall Insights', index=False)
            print(f"Sales report generated: {output_file}")
        except Exception as e:
            print(f"Error writing Excel file: {e}")

