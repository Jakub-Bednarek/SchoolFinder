import sys

from PyQt5.QtWidgets import QApplication
from window import MainWindow

class App():
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__main_window = MainWindow()
        self.running = True
         
    def run(self):
        self.__main_window.show()
        sys.exit(self.__app.exec_())