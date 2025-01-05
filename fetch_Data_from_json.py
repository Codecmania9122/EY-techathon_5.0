import json
import sqlite3

# Step 1: Load JSON data
with open(r'C:\Users\SAYANTANI\PycharmProjects\PythonProject\EY\interview_results_20241230_130122.json', 'r') as file:
    data = json.load(file)

# Step 2: Check the structure of the loaded data
print("Loaded data:", data)  # Add this to verify the structure

# Ensure the data is a list of dictionaries
if isinstance(data, list) and all(isinstance(item, dict) for item in data):
    # Step 3: Connect to SQLite3 database
    conn = sqlite3.connect('user_responses.db')  # This creates the DB file if it doesn't exist
    cursor = conn.cursor()


    # Step 5: Insert data into the table
    for person in data:
        name = person.get('name', 'Unknown')  # Use default value if key doesn't exist
        age = person.get('age', None)  # Use None if age is not available
        occupation = person.get('occupation', 'Not Specified')
        monthly_income = person.get('monthly_income', 'Not Provided')
        savings_investments = person.get('savings_investments', 'Not Provided')
        financial_terms_familiarity = person.get('financial_terms_familiarity', 'Not Provided')

        cursor.execute("""
            INSERT INTO interview_results (name, age, occupation, monthly_income, savings_investments, financial_terms_familiarity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, age, occupation, monthly_income, savings_investments, financial_terms_familiarity))

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Data successfully inserted into the database.")
else:
    print("Error: The loaded data is not in the expected format.")
