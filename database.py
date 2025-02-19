import sqlite3

class Database:
    def __init__(self, db_name="supermarket.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)  # Disable auto-commit (default behavior)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """Ensure live changes are visible in the database."""
        self.cursor.execute("PRAGMA journal_mode = WAL;")
        self.cursor.execute("PRAGMA synchronous = FULL;")
        self.create_tables()
        self.conn.commit()

    def create_tables(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS employees (
                id PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                password TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS inventory (
                id PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                aisle_name TEXT NOT NULL,
                FOREIGN KEY (aisle_name) REFERENCES aisles(name) 
            )""",
            """CREATE TABLE IF NOT EXISTS customers (
                id PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                membership TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                customer_id INTEGER,
                items TEXT,
                quantity INTEGER,
                tax REAL NOT NULL,
                discount REAL NOT NULL,
                total REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                membership TEXT,
                reference_number TEXT,
                payment_method TEXT,
                remarks TEXT DEFAULT '',
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (membership) REFERENCES customers(membership)
            )""",
            """CREATE TABLE IF NOT EXISTS aisles (
                id TEXT NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                product_name TEXT DEFAULT ''
            )"""
        ]
        for query in queries:
            self.cursor.execute(query)
        self.conn.commit()

    def execute_query(self, query, params=()):
        """Execute a query and commit changes."""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()

    def fetch_query(self, query, params=()):
        """Fetch query results."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def close(self):
        """Safely closes the database."""
        try:
            self.conn.close()
            print("Database closed safely.")
        except Exception as e:
            print(f"Error closing database: {e}")
