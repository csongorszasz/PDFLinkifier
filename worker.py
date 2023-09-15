from PyQt5.QtCore import QObject, pyqtSignal
import linkifier


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)

    def __init__(self, chosen_files: list):
        super().__init__()
        self.chosen_files = chosen_files

    def run(self):
        i = 1
        for file in self.chosen_files:
            self.progress.emit(i, file)
            linkifier.linkify(file)
            i += 1
        self.finished.emit()
