import time

import pytesseract
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QStatusBar, QMessageBox, QDialog, QDialogButtonBox
from PyQt5 import uic
from PyQt5.Qt import QColor, QThread, QPoint, QFont, QAction
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap
from pyqtspinner import WaitingSpinner

import sys
import os.path
from winotify import Notification, audio
import logging
import requests
import subprocess
from pathlib import Path
from os.path import exists
import ctypes

import worker
import resources


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

        uic.loadUi("assets/pdflinkifier.ui", self)
        self.setWindowIcon(QIcon(":/icons/app_icon.ico"))


        self.init_tesseract()

        self.spinner_linkify = create_spinner(self.ok_button)

        self.browse_button.clicked.connect(self.browse_button_pressed)
        self.ok_button.clicked.connect(self.ok_button_pressed)

        about_action = QAction(QIcon(), "Útmutató", self)
        about_action.triggered.connect(self.show_about_dialog_action)
        self.menuBar.addAction(about_action)

        self.chosen_files = []
        self.current_dir = ""
        self.is_processing = False
        # self.chosen_files = ['C:\GitHub\PDFLinkifier\samples\csalamade.pdf']
        # self.update_gui_begin_processing()
        # self.process_files()

        self.show()

    def init_tesseract(self):
        try:
            pytesseract.get_tesseract_version()
            return
        except pytesseract.TesseractNotFoundError:
            pass
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pytesseract.get_tesseract_version()
            return
        except pytesseract.TesseractNotFoundError:
            pass
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            pytesseract.get_tesseract_version()
            return
        except pytesseract.TesseractNotFoundError as e:
            dlg = QMessageBox()
            dlg.setIcon(QMessageBox.Warning)
            dlg.setWindowTitle(self.windowTitle())
            dlg.setText("Hiányzó modul: Tesseract-OCR.\nSzeretné telepíteni?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            yes_button = dlg.button(QMessageBox.Yes)
            yes_button.setText("Igen")
            no_button = dlg.button(QMessageBox.No)
            no_button.setText("Nem")

            dlg.exec_()

            if dlg.clickedButton() == yes_button:
                self.install_tesseract()
            else:
                sys.exit(1)

    def install_tesseract(self):
        QMessageBox.information(self, self.windowTitle(), "A letöltés befejeztével meg fog nyílni a telepítő.")
        downloads_path = str(Path.home() / "Downloads")
        installer_filename = "tesseract-ocr-w64-setup-5.3.3.20231005.exe"
        installer_path = f"{downloads_path}\\{installer_filename}"
        p = None

        if exists(installer_path):
            logging.info("Already downloaded")
        else:
            url = f"https://digi.bib.uni-mannheim.de/tesseract/{installer_filename}"
            logging.info(f"Downloading {installer_filename} from {url}")
            r = requests.get(url, allow_redirects=True)
            open(installer_path, "wb").write(r.content)
            logging.info(f"Download successful")

        try:
            logging.info(f"Installing Tesseract-OCR")
            p = subprocess.check_call(installer_path, shell=True)
        except Exception as e:
            QMessageBox.critical(self, self.windowTitle(), f"Hiba történt:\n{e}", QMessageBox.Ok)
            logging.error(f"Installation failed: {e}")
            sys.exit(1)

        logging.info(f"Installation successful")
        QMessageBox.warning(self, self.windowTitle(), "Sikeres telepítés.\nA helyes működéshez a számítógép újraindítása szükséges.")
        sys.exit(0)


    def closeEvent(self, a0: QCloseEvent) -> None:
        if not self.is_processing:
            a0.accept()
            return

        dlg = QMessageBox()
        dlg.setIcon(QMessageBox.Warning)
        dlg.setWindowTitle(self.windowTitle())
        dlg.setText("Biztosan ki akar lépni?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        yes_button = dlg.button(QMessageBox.Yes)
        yes_button.setText("Igen")
        no_button = dlg.button(QMessageBox.No)
        no_button.setText("Nem")

        dlg.exec_()

        if dlg.clickedButton() == yes_button:
            a0.accept()
        else:
            a0.ignore()

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

    def show_about_dialog_action(self):
        QMessageBox.about(
            self,
            "Útmutató",
            """
            <b>A program célja:</b>
            <br>
            <br>
            PDF formátumú kottás könyvekhez készít egy belső linkekkel ellátott tartalomjegyzéket, illetve kereshetővé teszi a dalokat cím szerint.
            <br>
            <br>
            A feldolgozott fájlok neve a <b><i>-feldolgozott</i></b> utótagot kapják, míg az eredeti fájl megmarad érintetlenül.
            <br>
            <br>
            <b>Használat:</b>
            <br>
            <br>
            A <b><i>Fájlok kiválasztása</i></b> gomb megnyomásával előugrik egy ablak, melyben kiválaszthatunk egy vagy több <b><i>.pdf</i></b> dokumentumot.
            <br>
            Ha sikerült kiválasztani a feldolgozni kívánt dokumentumokat, a <b><i>Fájlok kiválasztása</i></b> gomb mellet megjelenik, hogy hány fájl lett kiválasztva.
            <br>
            Az <b><i>OK</i></b> gomb megnyomásával elindíthatjuk a folyamatot, melynek befejeztéről értesít majd minket a rendszer.
            <br>
            Futtatás közbeni háttérben történő eseményekért lásd az <b><i>events.log</b></i> fájlt. 
            """
        )

    def print_to_statusbar(self, msg, color="black", hold_time=3000):
        """hold_time is in miliseconds"""
        self.statusBar().setStyleSheet(f"color: {color}")
        self.statusBar().showMessage(msg, hold_time)
        self.statusBar().repaint()

    def update_gui_begin_processing(self):
        self.centralWidget().setEnabled(False)
        self.ok_button.setStyleSheet("QPushButton { background-color: none; border: none; }")
        self.ok_button.setText("")
        self.menuBar.setEnabled(False)
        self.spinner_linkify.start()

    def reset(self):
        self.spinner_linkify.stop()
        self.chosen_files = []
        self.browsed_filename_label.setText("0 fájl")
        self.ok_button.setStyleSheet("")
        self.ok_button.setText("OK")
        self.menuBar.setEnabled(True)
        self.centralWidget().setEnabled(True)

    def process_files(self):
        self.worker_thr = QThread()
        self.worker_obj = worker.Worker(self.chosen_files)
        self.worker_obj.moveToThread(self.worker_thr)

        self.worker_thr.started.connect(self.worker_obj.run)
        self.worker_thr.finished.connect(self.worker_thr.deleteLater)
        self.worker_obj.finished.connect(self.worker_thr.quit)
        self.worker_obj.finished.connect(self.worker_obj.deleteLater)
        self.worker_obj.finished.connect(self.report_success)
        self.worker_obj.finished.connect(self.reset)
        self.worker_obj.progress.connect(self.report_progress)
        self.worker_obj.problem.connect(self.report_problem)
        self.is_processing = True
        self.worker_thr.start()

    def report_progress(self, nr, filepath):
        self.print_to_statusbar(f"{nr}/{len(self.chosen_files)} {get_filename_from_path(filepath)}", hold_time=0)

    def report_success(self):
        self.is_processing = False
        self.print_to_statusbar("Siker!", color="green", hold_time=10000)
        toast = Notification(
            app_id='PDFLinkifier',
            title='A fájlok feldolgozása sikeresen befejeződött.',
            msg='',
            icon=f"{os.path.abspath('assets/app_icon.ico')}",
            duration='long'
        )
        toast.set_audio(audio.Default, loop=False)
        toast.add_actions(label='Fájlok megtekintése', launch=self.current_dir)
        toast.show()

    def report_problem(self, exception: Exception):
        QMessageBox.critical(self, self.windowTitle(), f"Hiba történt:\n{exception}", QMessageBox.Ok)
        logging.error(f"Something went wrong: {exception}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(filename="events.log", level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

    app = QApplication([])
    window = MainWindow()
    app.exec_()