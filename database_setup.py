import sqlite3

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cur  = conn.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS notes 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    creation_date TEXT,
                    tags TEXT,
                    embedding TEXT
                )
                ''')

    conn.commit()
    try :
        print("Database 'notes_manager.db' and table 'notes' created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating database or table: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    database_name = 'notes_manager.db'
    create_database(database_name)


