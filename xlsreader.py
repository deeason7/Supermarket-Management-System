import sqlite3
import pandas as pd

class XLSDatabaseLoader:
    def __init__(self, db_name="supermarket.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    @staticmethod
    def read_xls(file_path):
        """Read an XLS file with multiple sheets and return a dictionary of DataFrames."""
        return pd.read_excel(file_path, sheet_name=None)  # Read all sheets

    def insert_data(self, table_name, df):
        """Insert data from DataFrame into the specified database table."""
        if df.empty:
            print(f" Skipping empty sheet: {table_name}")
            return

        try:
            df.to_sql(table_name.lower(), self.conn, if_exists="append", index=False)
            print(f" Data inserted into table: {table_name}")
        except Exception as e:
            print(f" Error inserting data into {table_name}: {e}")

    def load_xls_to_db(self, file_path):
        """Reads an XLS file with multiple sheets and inserts them into respective tables."""
        sheets = self.read_xls(file_path)

        for table_name, df in sheets.items():
            print(f" Processing sheet: {table_name}")
            self.insert_data(table_name, df)

    def close(self):
        """Close the database connection."""
        self.conn.close()
        print(" Database connection closed.")