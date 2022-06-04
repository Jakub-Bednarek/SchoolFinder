from helpers.logger import log_inf
from PyQt5.QtWidgets import QWidget, QProgressBar, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        self.__is_finished = False
        self.__setup_window()
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.start_loading)
        self.timer.start(2000)


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
        self.labelTitle.setText('School Finder')
        self.labelTitle.setAlignment(Qt.AlignCenter)

        self.labelDescription = QLabel(self.frame)
        self.labelDescription.resize(self.width(), 50)
        self.labelDescription.move(0, self.labelTitle.height())
        self.labelDescription.setObjectName('LabelDesc')
        self.labelDescription.setText('<strong>Loading...</strong>')
        self.labelDescription.setAlignment(Qt.AlignCenter)

        self.progressBar = QProgressBar(self.frame)
        self.progressBar.resize(int(self.width() / 2), int(self.height() / 6))
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.move(int(self.width() / 4) - 10, int(self.height() - (self.height() / 3 )))
        self.progressBar.setFormat('%p%')
        self.progressBar.setTextVisible(True)
        self.progressBar.setRange(0, self.__counter_max)
        self.progressBar.setValue(0)

        self.labelLoading = QLabel(self.frame)
        self.labelLoading.resize(self.width() - 10, 50)
        self.labelLoading.move(0, self.progressBar.y() + 70)
        self.labelLoading.setObjectName('LabelLoading')
        self.labelLoading.setAlignment(Qt.AlignCenter)
        self.labelLoading.setText('loading...')
        
        self.__set_style()
        
    def __set_style(self):
        self.setStyleSheet('''
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
        
    
    def start_loading(self):
        self.progressBar.setValue(self.__counter)
        
        log_inf(f"Progress: {self.__counter}")
        if self.__counter >= self.__counter_max:
            self.timer.stop()
            self.close()
            self.__is_finished = True
    
    def is_finished(self):
        return self.__is_finished
        
        
    def __setup_window(self):
        self.setWindowTitle("SchoolFinder")
        self.setFixedSize(500, 300)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.__counter = 0
        self.__counter_max = 0
        
    def add(self, amount=1):
        self.__counter_max += amount
        
    def add_finished(self):
        self.__counter += 1
    
splash_screen = None

def assign_splash_screen(new_splash_screen):
    global splash_screen
    splash_screen = new_splash_screen
        
def add_to_counter(amount=1):
    if splash_screen:
        splash_screen.add(amount)
        
def add_finished():
    if splash_screen:
        splash_screen.add_finished()