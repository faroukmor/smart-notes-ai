import sys 
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QGroupBox, QLineEdit,QMessageBox, QColorDialog) 
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from database_operations import notes_database
from rag_engine import chat_function,get_embedding
import sys, os, shutil
import json


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# إعداد قاعدة البيانات 
DB_NAME = "notes_manager.db"
db_src = resource_path(DB_NAME)

if getattr(sys, 'frozen', False):
    # المجلد الذي ستعمل فيه القاعدة بعد التحويل
    appdata_dir = os.path.join(os.environ['APPDATA'], "Note_manager")
    os.makedirs(appdata_dir, exist_ok=True)
    db_dst = os.path.join(appdata_dir, DB_NAME)
    # نسخ القاعدة أول مرة فقط
    if not os.path.exists(db_dst):
        shutil.copyfile(db_src, db_dst)
else:
    db_dst = db_src  # أثناء التطوير على البايثون



class AIWorker(QObject):

    finished = pyqtSignal(str,str)   

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        answer = chat_function(self.user_input)
        self.finished.emit(answer,self.user_input)




class smart_note(QMainWindow):
    def __init__(self):
        super().__init__()
        self.note_db = notes_database(db_dst)
        self.setWindowTitle("SMART NOTES MANAGER")
        self.setGeometry(1270,35,500,990)
        
        
        icon_path = resource_path("assets/myicon.jfif") 
        self.setWindowIcon(QIcon(icon_path))

        
        self.label_title = QLabel("SMART NOTES MANAGER")
        self.label_title.setObjectName("appTitleLabel")

        self.add_button = QPushButton("Add Note")
        self.update_button = QPushButton("Update Note")
        self.delete_button = QPushButton("Delete Note")
        self.showAll_button = QPushButton("Show All Notes")
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter note title...")
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags (e.g., work, personal)...")
        
        self.content_editor = QTextEdit()
        self.content_editor.setPlaceholderText("Write your note content here...")
        
        self.search_button = QPushButton("Search Note")
        self.ai_button = QPushButton("ask")
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Search note by title or tags...")
        
        self.ai_input = QLineEdit()
        self.ai_input.setObjectName("ai_input")
        self.ai_input.setPlaceholderText("ask AI about your notes")

        self.output_textEdit = QTextEdit()
        self.output_textEdit.setText("Welcome to Smart Notes Manager! Start by adding a note.")
        self.output_textEdit.setObjectName("output") 
        

        self.initUI()
        
    
    def initUI(self): 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        title_bar_layout = QHBoxLayout()
        title_bar_layout.addWidget(self.label_title)
        self.theme_btn = QPushButton("Dark")
        title_bar_layout.addWidget(self.theme_btn)


        searching_layout = QHBoxLayout()
        searching_layout.addWidget(self.search_input)
        searching_layout.addWidget(self.search_button)

        ai_layout = QHBoxLayout()
        ai_layout.addWidget(self.ai_input)
        ai_layout.addWidget(self.ai_button)

        note_details_group_box = QGroupBox("Note Details")
        note_input_layout = QVBoxLayout()
        title_tags_layout = QHBoxLayout()
        title_tags_layout.addWidget(QLabel("Title:")) 
        title_tags_layout.addWidget(self.title_input)
        title_tags_layout.addWidget(QLabel("Tags:")) 
        title_tags_layout.addWidget(self.tags_input)
        note_input_layout.addLayout(title_tags_layout)
        note_input_layout.addWidget(QLabel("Content:"))
        note_input_layout.addWidget(self.content_editor)
        note_details_group_box.setLayout(note_input_layout)

        # Layout for Add, Update, Delete buttons (first row)
        top_buttons_hbox = QHBoxLayout()
        top_buttons_hbox.addStretch(1) # Push buttons to center
        top_buttons_hbox.addWidget(self.add_button)
        top_buttons_hbox.addWidget(self.update_button)
        top_buttons_hbox.addWidget(self.delete_button)
        top_buttons_hbox.addStretch(1) 

        # Layout for Show All Notes button (second row)
        show_all_button_hbox = QHBoxLayout()
        show_all_button_hbox.addStretch(1) 
        show_all_button_hbox.addWidget(self.showAll_button)
        show_all_button_hbox.addStretch(1) 

        
        # A QVBoxLayout to stack the two HBoxes of buttons
        buttons_vbox = QVBoxLayout()
        buttons_vbox.addLayout(top_buttons_hbox)
        buttons_vbox.addLayout(show_all_button_hbox)

         

        output_group_box = QGroupBox("Notes Display") 
        output_layout = QVBoxLayout()
        output_group_box.setLayout(output_layout)
        output_layout.addWidget(self.output_textEdit)
        
        vbox = QVBoxLayout()
        vbox.addLayout(title_bar_layout, 0)
        vbox.addLayout(searching_layout, 0)
        vbox.addLayout(ai_layout, 0)
        vbox.addWidget(note_details_group_box, 3) 
        vbox.addLayout(buttons_vbox)
        vbox.addWidget(output_group_box, 6) 
        central_widget.setLayout(vbox)

        
        self.LIGHT = {
            'bg_main': 'hsl(233, 50%, 95%)',
            'bg_card': 'white',
            'bg_input': 'hsl(233, 50%, 95%)',
            'bg_output': '#f8f8f8',
            'bg_scrollbar': '#e0e0e0',
            'bg_title': 'hsl(233, 50%, 95%)',
            'primary': 'hsl(233, 50%, 40%)',
            'primary_hover': 'hsl(233, 50%, 55%)',
            'primary_pressed': 'hsl(233, 50%, 30%)',
            'primary_light': 'hsl(233, 50%, 60%)',
            'primary_lighter': 'hsl(233, 50%, 50%)',
            'primary_lightest': 'hsl(233, 50%, 65%)',
            'text_main': '#333',
            'text_secondary': '#444',
            'text_output': '#222',
            'text_muted': '#666',
            'text_faint': '#888',
            'text_inverse': 'white',
            'border_main': '#d0d0d0',
            'border_input': '#a9a9a9',
            'border_output': '#ddd',
            'border_html': '#ccc',
            'border_card': '#eee',
            'shadow': 'rgba(0,0,0,0.05)',
        }

        self.DARK = {
            'bg_main': 'hsl(233, 20%, 12%)',
            'bg_card': 'hsl(233, 15%, 18%)',
            'bg_input': 'hsl(233, 15%, 22%)',
            'bg_output': 'hsl(233, 15%, 15%)',
            'bg_scrollbar': 'hsl(233, 15%, 25%)',
            'bg_title': 'hsl(233, 20%, 12%)',
            'primary': 'hsl(220, 80%, 65%)',
            'primary_hover': 'hsl(220, 80%, 75%)',
            'primary_pressed': 'hsl(220, 80%, 55%)',
            'primary_light': 'hsl(220, 60%, 50%)',
            'primary_lighter': 'hsl(220, 60%, 45%)',
            'primary_lightest': 'hsl(220, 60%, 55%)',
            'text_main': '#e0e0e0',
            'text_secondary': '#b0b0b0',
            'text_output': '#d0d0d0',
            'text_muted': '#999',
            'text_faint': '#777',
            'text_inverse': 'hsl(233, 20%, 12%)',
            'border_main': '#444',
            'border_input': '#555',
            'border_output': '#444',
            'border_html': '#555',
            'border_card': '#3a3a3a',
            'shadow': 'rgba(0,0,0,0.3)',
        }
        
        self.current_theme = self.LIGHT

        self.setStyleSheet(self.build_style(self.current_theme))
        
        self.add_button.clicked.connect(self.add_note)
        self.showAll_button.clicked.connect(self.show_all_note)
        self.delete_button.clicked.connect(self.delete_note)
        self.update_button.clicked.connect(self.update_note)
        self.search_button.clicked.connect(self.search_note)
        self.ai_button.clicked.connect(self.ai_note)
        self.theme_btn.clicked.connect(self.toggle_theme)



    def build_style(self, theme):
        return f"""
            QWidget {{
                background-color: {theme['bg_main']};
                font-family: 'Segoe UI' , Arial;
                color: {theme['text_main']};
            }}

            QLabel#appTitleLabel {{
                color: {theme['primary']};
                font-size: 40px;
                font-weight: bold;
                padding: 10px 0;
                margin-bottom: 10px;
                qproperty-alignment: AlignCenter;
            }}

            QLabel {{
                font-size: 23px;
                color: {theme['text_secondary']};
                font-weight: bold;
                padding: 2px;
            }}

            QGroupBox {{
                font-size: 25px;
                font-weight: bold;
                color: {theme['primary']};
                border: 1px solid {theme['border_main']};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 25px;
                background-color: {theme['bg_card']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                font-weight: bold;
                background-color: {theme['bg_title']};
                border-radius: 5px;
            }}

            QLineEdit, QTextEdit {{
                font-size: 20px;
                padding: 8px;
                border: 1px solid {theme['border_input']};
                border-radius: 5px;
                background-color: {theme['bg_input']};
                selection-background-color: {theme['primary_light']};
                selection-color: {theme['text_inverse']};
            }}
            QLineEdit#search_input{{
                           background-color: {theme['bg_card']};
                           }}
            QLineEdit#ai_input{{
                           background-color: {theme['bg_card']};
                           }}
            QTextEdit {{
                min-height: 150px;
            }}

            QPushButton {{
                background-color: {theme['primary']};
                color: {theme['text_inverse']};
                           font-weight: bold;
                font-size: 20px;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                margin: 5px;
                min-width: 90px;
            }}
            QPushButton:hover{{
                background-color: {theme['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['primary_pressed']};
                padding-left: 17px;
                padding-top: 12px;
            }}

            QTextEdit#output {{
                font-size: 25px;
                background-color: {theme['bg_output']};
                border: 1px solid {theme['border_output']};
                border-radius: 5px;
                padding: 10px;
                min-height: 180px;
                color: {theme['text_output']};
            }}
            QScrollBar:vertical {{
                border: none;            
                background: {theme['bg_scrollbar']};     
                width: 8px;               
                margin: 0px 0px 0px 0px;  
                border-radius: 4px; 
                     
            }}
            QScrollBar::handle:vertical {{
                background: {theme['primary_lighter']};
                border-radius: 4px;            
                min-height: 25px; 
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['primary_lightest']}; 
           }}
            
        """

    def toggle_theme(self):
        if self.current_theme == self.LIGHT:
            self.current_theme = self.DARK
            self.theme_btn.setText("Light")
        else:
            self.current_theme = self.LIGHT
            self.theme_btn.setText("Dark")

        self.setStyleSheet(self.build_style(self.current_theme))
        self.output_textEdit.setText("")
    
    def add_note(self):
        title = self.title_input.text()
        content = self.content_editor.toPlainText()
        tags = self.tags_input.text()
        if title == "":
            self.output_textEdit.setText("Empty Title!")
        elif content == "":
            self.output_textEdit.setText("Empty Content!")
        elif tags == "":
            self.output_textEdit.setText("Empty Tag!")
        else:
            embedding = get_embedding(content)
            embedding = json.dumps(embedding.tolist())
            returned_text = self.note_db.Add_note(title, content, tags, embedding)
            
            self.output_textEdit.setText(returned_text)
        self.title_input.clear()
        self.content_editor.clear()
        self.tags_input.clear()

    def update_note(self):
        title = self.title_input.text()
        new_content = self.content_editor.toPlainText()
        if title == "":
            self.output_textEdit.setText("Empty Title!")
        elif new_content == "":
            self.output_textEdit.setText("Empty Content!")
        else:
            new_embedding = get_embedding(new_content)
            returned_text = self.note_db.Update_note(title,new_content,new_embedding)
            self.output_textEdit.setText(f"{returned_text}")
        self.title_input.clear()
        self.content_editor.clear()
        self.tags_input.clear()

    def delete_note(self):
        title = self.title_input.text()
        if title == "":
            self.output_textEdit.setText("Empty Title!")
        else:    
            
            reply = QMessageBox.question(self, 'Confirm Deletion', 
                             "Are you sure you want to delete this note?",
                             QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
            
                returned_text = self.note_db.Delete_data_note(title)
                self.output_textEdit.setText(returned_text)
            else:
                self.output_textEdit.setText("Deletion cancelled.")
            

        self.title_input.clear()
        self.content_editor.clear()
        self.tags_input.clear()
    
    def show_all_note(self):
        try:
            returned_notes = self.note_db.show_notes()
            t = self.current_theme
            
            html_message = f"""<body style='background-color: {t['bg_card']}; color: {t['text_main']};'>
            <h1 style='color: {t['primary']};'>All Notes:</h1><hr style='border: 1px solid {t['border_html']};'>""" 
            
            if not returned_notes: 
                html_message += f"<p style='color: {t['text_muted']};'>No notes available. Add your first note!</p>"
            else:
                for note in returned_notes:
                    
                    title, content, tags, creation_date = note[0], note[1], note[2], note[3]
                    
                    
                    html_message += f"<div style='border: 1px solid {t['border_card']}; padding: 10px; margin-bottom: 10px; border-radius: 8px; background-color: {t['bg_main']}; box-shadow: 0 2px 4px {t['shadow']};'>"
                    html_message += f"<h3><span style='color: {t['primary']};'>{title}</span></h3>" 
                    html_message += f"<p style='color: {t['text_main']};'>{content}</p>"
                    
                    html_message += f"<p><small><b style='color: {t['text_secondary']}'>Tags:</b> <i style='color: {t['text_muted']};'>{tags if tags else 'No tags'}</i></small></p>"
                    
                    html_message += f"<p style='text-align: right; color: {t['text_faint']};'><small>Created: {creation_date}</small></p>"
                    html_message += "</div>" 
            self.output_textEdit.setHtml(html_message)
        except IndexError:
            self.output_textEdit.setText("IndexError! propably(check the database)")
        
    def search_note(self):
        title_searched = self.search_input.text()
        if title_searched == "":
            self.output_textEdit.setText("You Didn't Write Anything To Search.") 
        else:
            returned_notes = self.note_db.search_note(title_searched)
            t = self.current_theme
            
           
            html_message = f"<h2 style='color: {t['primary']};'>Search Results for '{title_searched}':</h2><hr style='border: 1px solid {t['border_html']}';>"
            
            if not returned_notes:
                html_message += f"<p style='color: {t['text_muted']}'>No notes found matching '{title_searched}'.</p>"
            else:
                for note in returned_notes:
                   
                    note_id, title, content, creation_date, tags = note[0], note[1], note[2], note[3], note[4]

                   
                    html_message += f"<div style='border: 1px solid {t['border_card']}; padding: 10px; margin-bottom: 10px; border-radius: 8px; background-color: {t['bg_card']}; box-shadow: 0 2px 4px {t['shadow']};'>"
                    html_message += f"<h3><span style='color: {t['primary']}';'>ID: {note_id}</span> - <span style='color: {t['text_main']};'>{title}</span></h3>" 
                    html_message += f"<p style='color: {t['text_main']};'>{content}</p>" 
                   
                    html_message += f"<p><small><b style='color: {t['text_secondary']}'>Tags:</b> <i style='color: {t['text_muted']};'>{tags if tags else 'No tags'}</i></small></p>"
                    
                    html_message += f"<p style='text-align: right; color: {t['primary']}';'><small>Created: {creation_date}</small></p>"
                    html_message += "</div>"
            self.output_textEdit.setHtml(html_message)
        self.search_input.clear()

    def ai_note(self):
        user_input = self.ai_input.text()
        if user_input == "":
            self.output_textEdit.setText("You Didn't Write Anything To ask.") 
        else:
            self.ai_button.setEnabled(False)
            self.output_textEdit.setText("Wait for AI respond...")

            self.last_question = user_input
            self.thread = QThread()
            self.worker = AIWorker(user_input)

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)

            self.worker.finished.connect(self.display_ai_answer)

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()
                        
    def display_ai_answer(self,answer,user_input):
        t = self.current_theme

        html_message = f"<h2 style='color: {t['primary']}';'>Results for '{user_input}':</h2><hr style='border: 1px solid {t['border_html']}';'>"
            
        if not answer:
            html_message += f"<p style='color: {t['text_muted']}'>No notes found matching '{user_input}'.</p>"
        else:
            html_message += f"<p style='font-size: 25px; color: {t['primary']}';'>{answer}</p>" 
        self.output_textEdit.setHtml(html_message)
        self.ai_button.setEnabled(True)
        self.ai_input.clear()

    def save_changes(self):
        self.note_db.save_changes()
    def close_connection(self):
        self.note_db.close_connection()

    def closeEvent(self, event):
        self.note_db.save_changes()      
        self.note_db.close_connection() 
        event.accept()
   

    
def main():
    app = QApplication(sys.argv)
    window = smart_note()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()