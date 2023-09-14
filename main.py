from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QStatusBar
from PyQt5 import uic
from PyQt5.Qt import QColor
from pyqtspinner import WaitingSpinner
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
            spinner = WaitingSpinner(
                parent=self.ok_button,
                roundness=100.0,
                fade=30.0,
                radius=3,
                lines=125,
                line_length=5,
                line_width=1,
                speed=1.5707963267948966,
                color=QColor(0, 0, 0)
            )
            spinner.start()
            self.ok_button.setText("")

            i = 1
            for file in self.chosen_files:
                self.print_to_statusbar(f"{i}/{len(self.chosen_files)} {get_filename_from_path(file)}", hold_time=0)
                linkifier.linkify(file)
                i += 1

            self.print_to_statusbar("Siker!", color="green")

            spinner.stop()
            self.reset()

    def print_to_statusbar(self, msg, color="black", hold_time=3000):
        """hold_time is in miliseconds"""
        self.statusBar().setStyleSheet(f"color: {color}")
        self.statusBar().showMessage(msg, hold_time)
        self.statusBar().repaint()

    def reset(self):
        self.chosen_files = []
        self.ok_button.setText("OK")
        self.browsed_filename_label.setText("0 fájl")
        self.centralWidget().setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()