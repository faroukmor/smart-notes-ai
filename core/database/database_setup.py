"""Create the SQLite database and the ``notes`` table (idempotent)."""
import sqlite3


def create_database(db_path):
    """Create the database file + schema if they do not exist yet."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
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
    finally:
        conn.close()


if __name__ == '__main__':
    from core.config import DB_PATH
    create_database(DB_PATH)
    print(f"Database ready at: {DB_PATH}")



