from PyQt5.QtCore import QObject, pyqtSignal
import linkifier


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)
    problem = pyqtSignal()

    def __init__(self, chosen_files: list):
        super().__init__()
        self.chosen_files = chosen_files

    def run(self):
        i = 1
        for file in self.chosen_files:
            self.progress.emit(i, file)
            try:
                linkifier.linkify(file)
            except:
                self.problem.emit()
                return
            i += 1
        self.finished.emit()
