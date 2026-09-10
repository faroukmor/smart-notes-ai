from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.database.database_operations import notes_database
from core.rag_engine import get_embedding
import sys, os
import json
import html as html_lib
from core.ai_worker import AIWorker
from core.config import DB_PATH
from core.database.database_setup import create_database


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


class smart_note(QObject):

    ai_answer_ready = pyqtSignal(str)
    ai_answer_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        create_database(DB_PATH)
        self.note_db = notes_database(DB_PATH)
        self.returned_ai_answer = None
        self.current_theme = None

    def add_note(self, title, content, tags):
        embedding = get_embedding(content)
        if embedding is None:
            return ("Error: Could not reach Ollama for embeddings. "
                    "Make sure Ollama is running and the embedding model is pulled.")
        embedding = json.dumps(embedding.tolist())
        return self.note_db.Add_note(title, content, tags, embedding)

    def update_note(self, title, new_content):
        new_embedding = get_embedding(new_content)
        if new_embedding is None:
            return ("Error: Could not reach Ollama for embeddings. "
                    "Make sure Ollama is running and the embedding model is pulled.")
        new_embedding = json.dumps(new_embedding.tolist())
        return self.note_db.Update_note(title, new_content, new_embedding)

    def delete_note(self, title):
        return self.note_db.Delete_data_note(title)

    def show_all_notes(self, t):
        try:
            returned_notes = self.note_db.show_notes()

            html_message = f"""<body style='background-color: {t['bg_card']}; color: {t['text_main']};'>
            <h1 style='color: {t['primary']};'>All Notes:</h1>
            <hr style='border: 1px solid {t['border_html']};'>"""

            if not returned_notes:
                html_message += (
                    f"<p style='color: {t['text_muted']};'>"
                    f"No notes available. Add your first note!</p>"
                )
            elif isinstance(returned_notes, str):
                html_message += (f"<p style='color: {t['text_muted']};'>" f"{html_lib.escape(returned_notes)}</p>")
            else:
                for note in returned_notes:

                    title, content, tags, creation_date = (
                        note[0],
                        note[1],
                        note[2],
                        note[3]
                    )

                    html_message += (
                        f"<div style='border: 1px solid {t['border_card']}; "
                        f"padding: 10px; margin-bottom: 10px; "
                        f"border-radius: 8px; background-color: {t['bg_main']}; "
                        f"box-shadow: 0 2px 4px {t['shadow']};'>"
                    )

                    html_message += (
                        f"<h3><span style='color: {t['primary']};'>"
                        f"{html_lib.escape(str(title))}</span></h3>"
                    )

                    html_message += (
                        f"<p style='color: {t['text_main']};'>"
                        f"{html_lib.escape(str(content))}</p>"
                    )

                    html_message += (
                        f"<p><small>"
                        f"<b style='color: {t['text_secondary']}'>Tags:</b> "
                        f"<i style='color: {t['text_muted']};'>"
                        f"{html_lib.escape(str(tags)) if tags else 'No tags'}</i>"
                        f"</small></p>"
                    )

                    html_message += (
                        f"<p style='text-align: right; "
                        f"color: {t['text_faint']};'>"
                        f"<small>Created: {html_lib.escape(str(creation_date))}</small></p>"
                    )

                    html_message += "</div>"

            return html_message

        except IndexError:
            return "IndexError! propably(check the database)"

    def search_note(self, title_searched, t):
        returned_notes = self.note_db.search_note(title_searched)

        title_searched_esc = html_lib.escape(str(title_searched))
        html_message = (
            f"<h2 style='color: {t['primary']};'>"
            f"Search Results for '{title_searched_esc}':</h2>"
            f"<hr style='border: 1px solid {t['border_html']};'>"
        )

        if not returned_notes:
            html_message += (
                f"<p style='color: {t['text_muted']}'>"
                f"No notes found matching '{title_searched_esc}'.</p>"
            )
        elif isinstance(returned_notes, str):
            html_message += (f"<p style='color: {t['text_muted']}' >" f"{html_lib.escape(returned_notes)}</p>")
        else:
            for note in returned_notes:

                note_id, title, content, creation_date, tags = (
                    note[0],
                    note[1],
                    note[2],
                    note[3],
                    note[4]
                )

                html_message += (
                    f"<div style='border: 1px solid {t['border_card']}; "
                    f"padding: 10px; margin-bottom: 10px; "
                    f"border-radius: 8px; background-color: {t['bg_card']}; "
                    f"box-shadow: 0 2px 4px {t['shadow']};'>"
                )

                html_message += (
                    f"<h3>"
                    f"<span style='color: {t['primary']};'>"
                    f"ID: {note_id}</span> - "
                    f"<span style='color: {t['text_main']};'>"
                    f"{html_lib.escape(str(title))}</span></h3>"
                )

                html_message += (
                    f"<p style='color: {t['text_main']};'>"
                    f"{html_lib.escape(str(content))}</p>"
                )

                html_message += (
                    f"<p><small>"
                    f"<b style='color: {t['text_secondary']}'>Tags:</b> "
                    f"<i style='color: {t['text_muted']};'>"
                    f"{html_lib.escape(str(tags)) if tags else 'No tags'}</i>"
                    f"</small></p>"
                )

                html_message += (
                    f"<p style='text-align: right; "
                    f"color: {t['primary']};'>"
                    f"<small>Created: {html_lib.escape(str(creation_date))}</small></p>"
                )

                html_message += "</div>"

        return html_message

    def ai_note(self, user_input, t):
        self.last_question = user_input
        self.current_theme = t

        self.thread = QThread()
        self.worker = AIWorker(user_input)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.ai_answer)
        self.worker.failed.connect(self.ai_failed)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.failed.connect(self.thread.quit)
        self.worker.failed.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def ai_answer(self, answer, user_input):
        t = self.current_theme
        html_message = (
            f"<h2 style='color: {t['primary']};'>"
            f"Results for '{html_lib.escape(str(user_input))}':</h2>"
            f"<hr style='border: 1px solid {t['border_html']};'>"
        )

        if not answer:
            html_message += (
                f"<p style='color: {t['text_muted']}'>"
                f"No notes found matching '{html_lib.escape(str(user_input))}'.</p>"
            )
        else:
            html_message += (
                f"<p style='font-size: 25px; "
                f"color: {t['primary']};'>"
                f"{html_lib.escape(str(answer))}</p>"
            )

        self.returned_ai_answer = html_message

        # إرسال الـ HTML إلى Main_Window
        self.ai_answer_ready.emit(html_message)

    def ai_failed(self, error_message, user_input):
        self.returned_ai_answer = (f"<p style='color: red;'>AI request failed: " f"{html_lib.escape(str(error_message))}</p>")
        self.ai_answer_failed.emit(self.returned_ai_answer)

    def save_changes(self):
        self.note_db.save_changes()

    def close_connection(self):
        self.note_db.close_connection()

    def closeEvent(self, event):
        self.note_db.save_changes()
        self.note_db.close_connection()
        event.accept()