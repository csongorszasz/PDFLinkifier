from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QStatusBar
from PyQt5 import uic
import sys

import linkifier


def get_filename_from_path(path):
    return path.split('/')[-1]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("pdf-linkifier-v2.ui", self)

        self.browse_button.clicked.connect(self.browse_button_pressed)
        self.ok_button.clicked.connect(self.ok_button_pressed)

        self.chosen_files = []

        self.show()

    def browse_button_pressed(self):
        self.chosen_files = []
        filepaths = QFileDialog.getOpenFileNames(self, "Fájlok kiválasztása", "", "PDF (*.pdf)")
        for filepath in filepaths[0]:
            self.chosen_files.append(filepath)
        self.browsed_filename_label.setText(f"{len(filepaths[0])} fájl")

    def ok_button_pressed(self):
        if len(self.chosen_files) == 0:
            self.print_to_statusbar("Nincs kiválasztott fájl", color="red")
        else:
            self.centralWidget().setEnabled(False)

            self.print_to_statusbar("Fájl(ok) feldolgozása folyamatban", color="black", hold_time=0)

            for file in self.chosen_files:
                self.print_to_statusbar(f"{get_filename_from_path(file)} ...", hold_time=0)
                linkifier.linkify(file)

            self.browsed_filename_label.setText("")
            self.print_to_statusbar("Siker", color="green")

            self.chosen_files = []
            self.centralWidget().setEnabled(True)

    def print_to_statusbar(self, msg, color="black", hold_time=3000):
        """hold_time is in miliseconds"""
        self.statusBar().setStyleSheet(f"color: {color}")
        self.statusBar().showMessage(msg, hold_time)
        self.statusBar().repaint()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()