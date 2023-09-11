from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog
from PyQt5 import uic
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("pdf-linkifier.ui", self)
        # self.browse_button.clicked.connect(self.browseButtonPressed)
        self.show()

    # def browseButtonPressed(self):
    #     filepath = QFileDialog.getOpenFileName(self, "Fájl kiválasztása", "", "PDF (*.pdf)")
    #     if filepath is not None:
    #         filename = filepath[0].split('/')[-1]
    #         self.browsed_filename_label.setText(filename)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()