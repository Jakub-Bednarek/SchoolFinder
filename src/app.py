import sys

from PyQt5.QtWidgets import QApplication
from window import MainWindow
from helpers.logger import log_inf

class App():
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__main_window = MainWindow()
        self.running = True
         
    def run(self):
        self.__main_window.show()
        
        log_inf("Starting app")
        sys.exit(self.__app.exec_())