import sys
import os
import cv2
import base64

from pathlib import Path

from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

from classes.bridge import Bridge


class MainWindow(QMainWindow):

    def __init__(self, base_dir):
        super().__init__()

        self.setWindowTitle("Sliver Design System")
        self.resize(1200, 800)

        self.base_dir = base_dir
        self.templates_dir = os.path.join(base_dir, "templates")

        # -------- Web view --------
        self.view = QWebEngineView()
        self.view.setZoomFactor(0.7)
        self.setCentralWidget(self.view)

        # -------- Bridge --------
        self.bridge = Bridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        # -------- Camera --------
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.grab_frame)

        # Apply zoom after load (important)
        self.view.loadFinished.connect(lambda: self.view.setZoomFactor(0.7))

        # -------- Load first page --------
        self.load_page("../templates/index.html")

    # -------- PAGE LOAD --------
    def load_page(self, page_name):

        print(f"Switching to {page_name}")

        # Stop camera before switching
        if self.timer.isActive():
            self.stop_camera()

        self.view.setHtml("")

        full_path = os.path.join(self.templates_dir, page_name)
        self.view.load(QUrl.fromLocalFile(full_path))

    # -------- CAMERA START --------
    def start_camera(self):

        if self.timer.isActive():
            print("Camera already running")
            return

        print("Camera Starting...")

        if self.cap is None:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print("Camera not found")
            return

        self.timer.start(30)
        print("Camera Started")

    # -------- CAMERA STOP --------
    def stop_camera(self):

        self.timer.stop()

        if self.cap:
            self.cap.release()
            self.cap = None

        print("Camera Stopped")

    # -------- FRAME SEND --------
    def grab_frame(self):

        if not self.cap:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        _, buffer = cv2.imencode(".jpg", frame)
        jpg = base64.b64encode(buffer).decode()

        self.bridge.frame_signal.emit(jpg)

    # -------- TRAINING --------
    def start_training_process(self):
        print("Running training process...")

    # -------- REPORT WINDOW --------
    def open_report_window(self):

        if hasattr(self, "report_window") and self.report_window.isVisible():
            self.report_window.raise_()
            self.report_window.activateWindow()
            return

        self.report_window = QMainWindow()
        self.report_window.setWindowTitle("Report Window")
        self.report_window.resize(900, 600)

        self.report_view = QWebEngineView()
        self.report_view.setZoomFactor(1.0)
        self.report_window.setCentralWidget(self.report_view)

        self.report_channel = QWebChannel()
        self.report_bridge = Bridge(self)
        self.report_channel.registerObject("bridge", self.report_bridge)
        self.report_view.page().setWebChannel(self.report_channel)

        self.report_view.loadFinished.connect(
            lambda: self.report_view.setZoomFactor(1.0)
        )

        report_file = Path(__file__).parent / "templates" / "report.html"
        report_url = QUrl.fromLocalFile(str(report_file.resolve()))

        self.report_view.load(report_url)
        self.report_window.show()

    # -------- CLEANUP --------
    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)


# -------- MAIN --------
if __name__ == "__main__":

    # DPI fix (important for zoom issue)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    window = MainWindow(base_dir)
    window.show()

    sys.exit(app.exec_())
