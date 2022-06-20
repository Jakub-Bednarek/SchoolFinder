from webbrowser import open

from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QErrorMessage,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSignal, QObject

from twitter_management.authorization import InvalidPinException, authenticator
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

        layout = QGridLayout()

        first_step_label = QLabel()
        first_step_label.setText(
            "<font color=#2798f5>1. Go to authorization page.</font>"
        )
        first_step_label.setFont(QFont("Open sans", 45, weight=QFont.Bold))

        open_web_button = QPushButton(self)
        open_web_button.setText("Authorization page")
        open_web_button.setIcon(QIcon(f"{ICONS_PATH}/twitter_logo.png"))
        open_web_button.clicked.connect(self.go_to_authorization_page)

        pin_label = QLabel("PIN")
        pin_label.setText("<font color=#2798f5>PIN</font>")
        pin_label.setFont(QFont("Open sans", weight=QFont.Bold))
        self.__pin_text_area = QLineEdit()

        submit_button = QPushButton(self)
        submit_button.setText("SUBMIT")
        submit_button.clicked.connect(self.submit_pin)

        second_step_label = QLabel()
        second_step_label.setText(
            "<font color=#2798f5>2. Paste pin below and submit!</font>"
        )
        second_step_label.setFont(QFont("Open sans", 45, weight=QFont.Bold))

        layout.addWidget(first_step_label, 0, 0)
        layout.addWidget(open_web_button, 1, 0)
        layout.addWidget(QLabel(), 2, 0)
        layout.addWidget(second_step_label, 3, 0)
        layout.addWidget(self.__pin_text_area, 4, 0)
        layout.addWidget(submit_button, 5, 0)
        layout.setSpacing(10)

        self.setLayout(layout)

    def is_authorized(self):
        return self.__success

    def setup_window(self):
        width = int(self.__screen_width / 5)
        height = int(self.__screen_height / 5)
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
            msg = QErrorMessage()
            msg.showMessage(str(e))
            msg.exec_()
