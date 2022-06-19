from webbrowser import open

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject

from twitter_management.authorization import InvalidPinException, authenticator
from helpers.logger import log_err
from window import get_main_window

ICONS_PATH = "res/icons/"


class Communicate(QObject):
    authenticationSuccessfull = pyqtSignal()


class LoginScreen(QWidget):
    def __init__(self, screen):
        super(LoginScreen, self).__init__()
        self.__screen_width = screen.size().width()
        self.__screen_height = screen.size().height()
        self.initUI()

    def initUI(self):
        self.setup_window()
        self.communicate = Communicate()

        layout = QVBoxLayout()
        open_web_button = QPushButton(self)
        open_web_button.setText("Go to authorization page")
        open_web_button.setIcon(QIcon(f"{ICONS_PATH}/twitter_logo.png"))
        open_web_button.clicked.connect(self.go_to_authorization_page)
        layout.addWidget(open_web_button)

        pin_label = QLabel("PIN")
        self.__pin_text_area = QLineEdit()
        layout.addWidget(pin_label)
        layout.addWidget(self.__pin_text_area)

        submit_button = QPushButton(self)
        submit_button.setText("SUBMIT")
        submit_button.clicked.connect(self.submit_pin)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def is_authorized(self):
        return self.__success

    def setup_window(self):
        width = int(self.__screen_width / 5)
        height = int(self.__screen_height / 5)
        print(f"Width: {width}, Height: {height}")
        self.resize(width, height)

    def go_to_authorization_page(self):
        open(authenticator.get_authorization_url())

    def submit_pin(self):
        text = self.__pin_text_area.text()
        try:
            authenticator.sign_in_with_pin(text)
            self.hide()
            get_main_window().show()
        except InvalidPinException as e:
            log_err(e)
