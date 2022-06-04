import sys
import time

from helpers.logger import log_inf
from PyQt5.QtWidgets import QWidget, QPushButton, QProgressBar, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        self.__is_finished = False
        self.__setup_window()
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.start_loading)
        self.timer.start(3000)


    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.frame = QFrame()
        layout.addWidget(self.frame)

        self.labelTitle = QLabel(self.frame)
        self.labelTitle.setObjectName('LabelTitle')

        # center labels
        self.labelTitle.resize(self.width() - 10, 150)
        self.labelTitle.move(0, 40) # x, y
        self.labelTitle.setText('Splash Screen')
        self.labelTitle.setAlignment(Qt.AlignCenter)

        self.labelDescription = QLabel(self.frame)
        self.labelDescription.resize(self.width() - 10, 50)
        self.labelDescription.move(0, self.labelTitle.height())
        self.labelDescription.setObjectName('LabelDesc')
        self.labelDescription.setText('<strong>Working on Task #1</strong>')
        self.labelDescription.setAlignment(Qt.AlignCenter)

        self.progressBar = QProgressBar(self.frame)
        self.progressBar.resize(self.width() - 200 - 10, 50)
        self.progressBar.move(100, self.labelDescription.y() + 130)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setFormat('%p%')
        self.progressBar.setTextVisible(True)
        self.progressBar.setRange(0, self.__counter_max)
        self.progressBar.setValue(20)

        self.labelLoading = QLabel(self.frame)
        self.labelLoading.resize(self.width() - 10, 50)
        self.labelLoading.move(0, self.progressBar.y() + 70)
        self.labelLoading.setObjectName('LabelLoading')
        self.labelLoading.setAlignment(Qt.AlignCenter)
        self.labelLoading.setText('loading...')
        
    
    def start_loading(self):
        self.progressBar.setValue(self.__counter)
        
        log_inf(f"Progress: {self.__counter}")
        if self.__counter >= self.__counter_max:
            self.timer.stop()
            self.close()
            self.__is_finished = True
            
            
        self.__counter += 1
    
    def is_finished(self):
        return self.__is_finished
        
        
    def __setup_window(self):
        self.setWindowTitle("SchoolFinder")
        self.setFixedSize(500, 300)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.__counter = 0
        self.__counter_max = 5
        
        