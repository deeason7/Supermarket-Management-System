from supermarket import supermarket_program
from database import Database

def main():
    db = Database()  # Initialize database

    try:
        supermarket_program()  # Start the supermarket system
    except KeyboardInterrupt:
        print("\n\n🔴 Program interrupted! Closing gracefully...")
    finally:
        db.close() # Ensure database5 connection is closed properly

if __name__ == "__main__":
    main()
