import sys

from PyQt5.QtWidgets import QApplication
from window import MainWindow, set_main_window

from twitter_management.authorization import authenticator
from helpers.logger import log_inf
from qt_material import apply_stylesheet
from widgets.login_screen import LoginScreen


class App:
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__screen = self.__app.primaryScreen()
        self.main_window = MainWindow(self.__screen)

        set_main_window(self.main_window)
        apply_stylesheet(self.__app, theme="dark_blue.xml")
        self.login = LoginScreen(self.__screen)

    def __del__(self):
        log_inf("Destroyed app")

    def run(self):
        log_inf("Starting app")
        self.login.show()

        sys.exit(self.__app.exec_())

    def check_if_login_success(self):
        return self.login
