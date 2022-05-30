from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from helpers.logger import log_inf

class MainWindow(QMainWindow):
    def __init__(self):
        log_inf("Initializing MainWindow")
        
        super(MainWindow, self).__init__()
        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("School finder")
        self.initUI()
        
        log_inf("Successfully MainWindow")
            
    def initUI(self):
        log_inf("Initializing UI")
        
        self.label = QtWidgets.QLabel(self)
        self.label.setText("First label")
        self.label.move(50, 50)
        
        log_inf("Successfully inititalized UI")