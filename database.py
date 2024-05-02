import sqlite3

class DatabaseManager:
    def __init__(self, db_name='DB.db'):
        self.db_name = db_name

    def create_database(self):
        # Connect to the SQLite database or create it if it doesn't exist
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create the Model table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Model (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                path TEXT,
                isactive INTEGER DEFAULT 0
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def insert_model_into_database(self, name, path):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Insert the data into the Model table
            cursor.execute('INSERT INTO Model (name, path, isactive) VALUES (?, ?, 0)', (name, path))
            conn.commit()
            print("Model inserted successfully!")
        except sqlite3.Error as e:
            print("Error occurred while inserting model:", e)
        finally:
            # Close the connection
            conn.close()
    def fetch_all_models(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Fetch all rows from the Model table
            cursor.execute('SELECT * FROM Model')
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print("Error occurred while fetching models:", e)
            return None
        finally:
            # Close the connection
            conn.close()

# Example of using the DatabaseManager class
if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.create_database()
    db_manager.insert_model("Model1", "path/to/model1.gguf")
