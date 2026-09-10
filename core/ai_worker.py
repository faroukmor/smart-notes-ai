from PyQt5.QtCore import QObject, pyqtSignal
from core.rag_engine import chat_function


class AIWorker(QObject):

    finished = pyqtSignal(str, str)
    failed = pyqtSignal(str, str)

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        try:
            answer = chat_function(self.user_input)
            if answer is None:
                answer = ""
            self.finished.emit(answer, self.user_input)
        except Exception as e:
            self.failed.emit(str(e), self.user_input)


