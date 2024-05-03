import sqlite3
import datetime

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

        # Create the ChatSession table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ChatSession (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT,
                session_time TEXT
                -- Add other session-related columns as needed
            )
        ''')

        # Create the Message table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Message (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                sender TEXT,
                message_text TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES ChatSession(session_id)
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    def fetch_chat_history(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cs.session_date, m.message_text,mm.session_id
                FROM ChatSession cs 
                LEFT JOIN (
                    SELECT session_id, MIN(message_id) as min_message_id 
                    FROM Message 
                    GROUP BY session_id
                ) mm ON cs.session_id = mm.session_id 
                LEFT JOIN Message m ON mm.min_message_id = m.message_id
            """)
            chat_history = cursor.fetchall()
            return chat_history
        except sqlite3.Error as e:
            print("Error occurred while fetching chat history:", e)
            return []

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
    def remove_model(self, model_name):
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            try:
                # Execute SQL to delete the model with the specified name
                cursor.execute('DELETE FROM Model WHERE name = ?', (model_name,))
                conn.commit()
                print("Model removed successfully!")
            except sqlite3.Error as e:
                print("Error occurred while removing model:", e)
            finally:
                # Close the connection
                conn.close()
    def update_all_models_inactive(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Model SET isactive = 0")
            conn.commit()
        except sqlite3.Error as e:
            print("Error occurred while updating models:", e)
        finally:
            conn.close()

    def set_model_active(self, model_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Model SET isactive = 1 WHERE name = ?", (model_name,))
            conn.commit()
        except sqlite3.Error as e:
            print("Error occurred while setting model active:", e)
        finally:
            conn.close()
    def get_active_model_path(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT path FROM Model WHERE isactive = 1")
            result = cursor.fetchone()
            if result:
                return result[0]
        except sqlite3.Error as e:
            print("Error occurred while fetching active model path:", e)
        finally:
            conn.close()
    def get_active_model_name(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM Model WHERE isactive = 1")
            result = cursor.fetchone()
            if result:
                return result[0]
        except sqlite3.Error as e:
            print("Error occurred while fetching active model path:", e)
        finally:
            conn.close()
    def is_any_model_active(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Check if any row is marked as active
            cursor.execute("SELECT COUNT(*) FROM Model WHERE isactive = 1")
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            print("Error occurred while checking for active models:", e)
            return False
        finally:
            # Close the connection
            conn.close()
    def get_or_create_session_id(self):
        # Get today's date and time
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')

        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Check if a session exists for today's date
            cursor.execute("SELECT session_id FROM ChatSession WHERE session_date = ?", (today_date,))
            session_id = cursor.fetchone()

            if session_id:
                # If a session exists, return its ID
                return session_id[0]
            else:
                # If no session exists, create a new session and return its ID
                cursor.execute("INSERT INTO ChatSession (session_date, session_time) VALUES (?, ?)", (today_date, current_time))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print("Error occurred while fetching or creating session ID:", e)
            return None
        finally:
            # Close the connection
            conn.close()

    def save_message(self, session_id, sender, message_text, timestamp):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Insert the message into the Message table
            cursor.execute('''
                INSERT INTO Message (session_id, sender, message_text, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (session_id, sender, message_text, timestamp))
            conn.commit()
            print("Message saved successfully!")
        except sqlite3.Error as e:
            print("Error occurred while saving message:", e)
        finally:
            # Close the connection
            conn.close()
    def fetch_messages_by_session_id(self, session_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT sender, message_text, timestamp FROM Message WHERE session_id = ?", (session_id,))
            messages = cursor.fetchall()
            return messages
        except sqlite3.Error as e:
            print("Error occurred while fetching messages by session ID:", e)
            return []
# Example of using the DatabaseManager class
if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.create_database()
    db_manager.insert_model("Model1", "path/to/model1.gguf")
