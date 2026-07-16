import sqlite3
import datetime

class notes_database():
    def __init__(self,db_name):
        self.conn = sqlite3.connect(db_name)
        self.cur  = self.conn.cursor()

    def save_changes(self):
        self.conn.commit()
    def close_connection(self):
        self.conn.close()
    def rollback_changes(self):
        self.conn.rollback()


    def Add_note(self,title, content, tags,embedding):
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        
        try:
            self.cur.execute("INSERT INTO notes(title,content,creation_date,tags,embedding) VALUES (?,?,?,?,?)", (title,content,creation_date,tags,embedding,))
            self.save_changes()
            return f"{title} added successfully ✔️"

        except sqlite3.Error as e:
            return f"Error adding note: {e}"
        


    def Update_note(self,title,new_content,new_embedding):
        try:
            self.cur.execute("SELECT 1 FROM notes WHERE title = ?", (title,))
            exists = self.cur.fetchone() 

            if exists:
                self.cur.execute("UPDATE notes SET content = ? and embedding = ? WHERE title = ?",(new_content,new_embedding,title,))
                return f"{title} updated successfully ✔️"
            else: 
                return f"Error: Note with title '{title}' not found to update."
        except sqlite3.Error as e:
            return f"Error updating note: {e}"
    
    def show_notes(self):
        try:
            self.cur.execute("SELECT title,content,tags,creation_date FROM notes ORDER BY creation_date DESC")
            notes = self.cur.fetchall()
            return notes
        except sqlite3.Error as e:
            return f"Error adding note: {e}"       

    def search_note(self,title):
        try:
            self.cur.execute("SELECT * FROM notes WHERE title LIKE ?",(title,))
            note_you_search = self.cur.fetchall()
            return note_you_search          
        except sqlite3.Error as e:
            return f"Error adding note: {e}"

    def Delete_data_note(self,title):
        try:
            self.cur.execute("SELECT 1 FROM notes WHERE title = ?",(title,))
            exist = self.cur.fetchone()
            if exist:
                self.cur.execute("DELETE FROM notes WHERE title = ?",(title,))
                return f"{title} deleted successfully ✔️"
            else: 
                return f"Error: Note with title '{title}' not found to delete."
        except sqlite3.Error as e:
            return f"Error adding note: {e}"
    


def main():
    note_db = notes_database('notes_manager.db')
    

main()