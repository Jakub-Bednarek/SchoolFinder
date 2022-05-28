from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("School finder")
        self.initUI()
            
    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("First label")
        self.label.move(50, 50)