from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QGroupBox, QLineEdit,QMessageBox) 
from PyQt5.QtGui import QIcon
from core.smartnote import smart_note, resource_path
import sys

class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.smart_note = smart_note()
        self.smart_note.ai_answer_ready.connect(self.display_ai_answer)
        self.smart_note.ai_answer_failed.connect(self.display_ai_failed)

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
        self.ai_button = QPushButton("Ask AI")
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Search note by title or tags... (or press Enter)")
        self.search_input.returnPressed.connect(self.search_note)
        
        self.ai_input = QLineEdit()
        self.ai_input.setObjectName("ai_input")
        self.ai_input.setPlaceholderText("ask AI about your notes (or press Enter)")
        self.ai_input.returnPressed.connect(self.ai_note)

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
        self.showAll_button.clicked.connect(self.show_all_notes)
        self.delete_button.clicked.connect(self.delete_note)
        self.update_button.clicked.connect(self.update_note)
        self.search_button.clicked.connect(self.search_note)
        self.ai_button.clicked.connect(self.ai_note)
        self.theme_btn.clicked.connect(self.toggle_theme)

    def add_note(self):
        title = self.title_input.text()
        content = self.content_editor.toPlainText()
        tags = self.tags_input.text()
        if title == "":
            self.output_textEdit.setText("Empty Title!")
        elif content == "":
            self.output_textEdit.setText("Empty Content!")
        else:
            returned_text = self.smart_note.add_note(title,content,tags) 
            self.output_textEdit.setText(returned_text)  
        self.title_input.clear()
        self.content_editor.clear()
        self.tags_input.clear()  


    def show_all_notes(self):
        returned_text = self.smart_note.show_all_notes(self.current_theme)
        if returned_text == "IndexError! propably(check the database)":
            self.output_textEdit.setText(returned_text)
        else:
            self.output_textEdit.setHtml(returned_text)

    
    def delete_note(self):
        title = self.title_input.text()
        if title == "":
            self.output_textEdit.setText("Empty Title!")
        else:    
            reply = QMessageBox.question(self, 'Confirm Deletion', 
                             "Are you sure you want to delete this note?",
                             QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                returned_text = self.smart_note.delete_note(title)
                self.output_textEdit.setText(returned_text)
            else:
                self.output_textEdit.setText("Deletion cancelled.")
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
            returned_text = self.smart_note.update_note(title, new_content)
            self.output_textEdit.setText(f"{returned_text}")
        self.title_input.clear()
        self.content_editor.clear()
        self.tags_input.clear()
             
    def search_note(self):
        title_searched = self.search_input.text()
        if title_searched == "":
            self.output_textEdit.setText("You Didn't Write Anything To Search.") 
        else:
            returned_text = self.smart_note.search_note(title_searched,self.current_theme)
            self.output_textEdit.setHtml(returned_text)
        self.search_input.clear()
   
    def ai_note(self):
        user_input = self.ai_input.text()
        if user_input == "":
            self.output_textEdit.setText("You Didn't Write Anything To ask.") 
        else:
            self.ai_button.setEnabled(False)
            self.output_textEdit.setText("Wait for AI respond...")
            self.last_question = user_input
            self.smart_note.ai_note(
                            user_input,
                            self.current_theme
                        )

    def display_ai_answer(self, html_message):
        self.output_textEdit.setHtml(html_message)

        self.ai_button.setEnabled(True)
        self.ai_input.clear()


    def display_ai_failed(self, html_message):
        self.output_textEdit.setHtml(html_message)

        self.ai_button.setEnabled(True)


    def closeEvent(self, event):
        self.smart_note.save_changes()
        self.smart_note.close_connection()
        event.accept()

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

     
def main():
    app = QApplication(sys.argv)
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()