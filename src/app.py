import sys
import configparser

from PyQt5.QtWidgets import QApplication
from window import MainWindow
from helpers.logger import log_inf
from widgets.splash_screen import SplashScreen

class App():
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__set_style()
        
        self.__splash_screen = SplashScreen()
        self.__splash_screen.show()
        self.__main_window = MainWindow()
        self.running = True
        
    def __del__(self):
        log_inf("Destroyed app")
         
    def run(self):
        self.__main_window.show()
        
        log_inf("Starting app")
        sys.exit(self.__app.exec_())
        
    def __set_style(self):
        self.__app.setStyleSheet('''
            #LabelTitle {
                font-size: 60px;
                color: #93deed;
            }

            #LabelDesc {
                font-size: 30px;
                color: #c2ced1;
            }

            #LabelLoading {
                font-size: 30px;
                color: #e8e8eb;
            }

            QFrame {
                background-color: #2F4454;
                color: rgb(220, 220, 220);
            }

            QProgressBar {
                background-color: #DA7B93;
                color: rgb(200, 200, 200);
                border-style: none;
                border-radius: 10px;
                text-align: center;
                font-size: 30px;
            }

            QProgressBar::chunk {
                border-radius: 10px;
                background-color: qlineargradient(spread:pad x1:0, x2:1, y1:0.511364, y2:0.523, stop:0 #1C3334, stop:1 #376E6F);
            }
        ''')
        
    def __load_config(self, file_name: str):
        pass
    
    def __save_config(self, file_name: str):
        pass