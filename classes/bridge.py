# classes/bridge.py

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class Bridge(QObject):

    frame_signal = pyqtSignal(str)

    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref

    # -------- CAMERA ----------
    @pyqtSlot()
    def startCamera(self):
        self.app_ref.start_camera()

    @pyqtSlot()
    def stopCamera(self):
        self.app_ref.stop_camera()

    # -------- NAVIGATION ----------
    @pyqtSlot()
    def goHome(self):
        self.app_ref.load_page("../template/index.html")

    @pyqtSlot()
    def goReport(self):
        self.app_ref.open_report_window()

    @pyqtSlot()
    def goTraining(self):
        self.app_ref.load_page("../template/traning.html")

    @pyqtSlot()
    def startTraining(self):
        print("Training started")
        self.app_ref.start_training_process()   