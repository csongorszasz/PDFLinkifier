from PyQt5.QtCore import QObject, pyqtSignal
import linkifier
from pytesseract import TesseractNotFoundError
import sys

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)
    problem = pyqtSignal(Exception)

    def __init__(self, chosen_files: list):
        super().__init__()
        self.chosen_files = chosen_files

    def run(self):
        i = 1
        for file in self.chosen_files:
            self.progress.emit(i, file)
            try:
                linkifier.linkify(file)
            except Exception as e:
                self.problem.emit(e)
                return

            i += 1
        self.finished.emit()
