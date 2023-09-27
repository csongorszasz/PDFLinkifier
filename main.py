from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QStatusBar, QMessageBox
from PyQt5 import uic
from PyQt5.Qt import QColor, QThread, QPoint, QFont
from PyQt5.QtCore import Qt
from pyqtspinner import WaitingSpinner
import sys
import os.path
from winotify import Notification, audio
import logging

import linkifier
import worker


def get_filename_from_path(path):
    return path.split('/')[-1]


def create_spinner(parent=None, roundness=100.0, fade=30.0, radius=3, lines=125, line_length=5, line_width=1, speed=2, color=QColor(0,0,0)) -> WaitingSpinner:
    return WaitingSpinner(
        parent=parent,
        roundness=roundness,
        fade=fade,
        radius=radius,
        lines=lines,
        line_length=line_length,
        line_width=line_width,
        speed=speed,
        color=color
    )


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("pdf-linkifier-v2.ui", self)
        self.spinner_linkify = create_spinner(self.ok_button)

        self.browse_button.clicked.connect(self.browse_button_pressed)
        self.ok_button.clicked.connect(self.ok_button_pressed)

        self.chosen_files = []
        self.current_dir = ""
        # self.chosen_files = ['C:\GitHub\PDFLinkifier\samples\csalamade.pdf']
        # self.update_gui_begin_processing()
        # self.process_files()

        self.show()

    def browse_button_pressed(self):
        self.chosen_files = []
        filepaths = QFileDialog.getOpenFileNames(self, "Fájlok kiválasztása", "", "PDF (*.pdf)")
        for filepath in filepaths[0]:
            self.chosen_files.append(filepath)
        nr_files = len(self.chosen_files)
        if nr_files:
            self.current_dir = os.path.dirname(self.chosen_files[0])
        self.browsed_filename_label.setText(f"{nr_files} fájl")

    def ok_button_pressed(self):
        if len(self.chosen_files) == 0:
            self.print_to_statusbar("Nincs kiválasztott fájl", color="red")
        else:
            self.update_gui_begin_processing()
            self.process_files()

    def print_to_statusbar(self, msg, color="black", hold_time=3000):
        """hold_time is in miliseconds"""
        self.statusBar().setStyleSheet(f"color: {color}")
        self.statusBar().showMessage(msg, hold_time)
        self.statusBar().repaint()

    def update_gui_begin_processing(self):
        self.centralWidget().setEnabled(False)
        self.ok_button.setStyleSheet("QPushButton { background-color: none; border: none; }")
        self.ok_button.setText("")
        self.spinner_linkify.start()

    def reset(self):
        self.spinner_linkify.stop()
        self.chosen_files = []
        self.browsed_filename_label.setText("0 fájl")
        self.ok_button.setStyleSheet("")
        self.ok_button.setText("OK")
        self.centralWidget().setEnabled(True)

    def process_files(self):
        self.thr = QThread()
        self.worker_obj = worker.Worker(self.chosen_files)
        self.worker_obj.moveToThread(self.thr)

        self.thr.started.connect(self.worker_obj.run)
        self.thr.finished.connect(self.thr.deleteLater)
        self.worker_obj.finished.connect(self.thr.quit)
        self.worker_obj.finished.connect(self.worker_obj.deleteLater)
        self.worker_obj.finished.connect(self.report_success)
        self.worker_obj.finished.connect(self.reset)
        self.worker_obj.progress.connect(self.report_progress)
        self.thr.start()

    def report_progress(self, nr, filepath):
        self.print_to_statusbar(f"{nr}/{len(self.chosen_files)} {get_filename_from_path(filepath)}", hold_time=0)

    def report_success(self):
        self.print_to_statusbar("Siker!", color="green", hold_time=10000)
        toast = Notification(
            app_id='PDFLinkifier',
            title='A fájlok feldolgozása sikeresen befejeződött.',
            msg='',
            duration='long'
        )
        toast.set_audio(audio.Default, loop=False)
        toast.add_actions(label='Fájlok megtekintése', launch=self.current_dir)
        toast.show()


if __name__ == "__main__":
    logging.basicConfig(filename="events.log", level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

    app = QApplication([])
    window = MainWindow()
    app.exec_()