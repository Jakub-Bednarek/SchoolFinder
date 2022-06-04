import sys

from PyQt5.QtWidgets import QApplication
from window import MainWindow
from helpers.logger import log_inf
from widgets.splash_screen import SplashScreen, assign_splash_screen, add_to_counter, add_finished, splash_screen

class App():
    def __init__(self):
        self.__app = QApplication(sys.argv)
        
        self.__splash_screen = SplashScreen()
        assign_splash_screen(self.__splash_screen)
        add_to_counter(2)
        self.__splash_screen.show()
        self.__main_window = MainWindow()
        self.running = True
        
    def __del__(self):
        log_inf("Destroyed app")
         
    def run(self):
        add_finished()
        
        self.__main_window.show()
        
        log_inf("Starting app")
        sys.exit(self.__app.exec_())
        
    def __load_config(self, file_name: str):
        pass
    
    def __save_config(self, file_name: str):
        pass