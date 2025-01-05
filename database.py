import sqlite3
import os


def create_database():
    """Deletes the existing SQLite database (if it exists) and creates a new users table."""
    # Delete the existing database if it exists
    if os.path.exists("user_responses.db"):
        os.remove("user_responses.db")
        print("Existing database deleted successfully.")

    # Create a new database and users table
    conn = sqlite3.connect("user_responses.db")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                occupation TEXT,
                monthly_income TEXT,
                savings_investments TEXT,
                financial_terms_familiarity TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.close()
    print("New database and table created successfully.")


def fetch_all_users():
    """Fetch and display all user data in tabular form."""
    conn = sqlite3.connect("user_responses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    # Print data in tabular form
    headers = [description[0] for description in cursor.description]
    print(f"\n{' | '.join(headers)}")
    print("-" * 100)
    for row in rows:
        print(" | ".join(str(item) if item is not None else "NULL" for item in row))

    conn.close()


if __name__ == "__main__":
    create_database()
    print("To view the data, call `fetch_all_users()` from your main program or test scripts.")
    fetch_all_users()

