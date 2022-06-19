import configparser

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QGridLayout,
    QWidget,
    QPlainTextEdit,
    QFrame,
    QLineEdit,
    QDockWidget,
    QScrollArea,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QFileDialog
)
from PyQt5.QtGui import QIcon

from helpers.logger import log_inf, log_err
from widgets.collapsible_box import CollapsibleBox
from twitter_management.post_tweet import (
    TweetNotPostedException,
    post,
    check_return_code,
)

DEFAULT_WINDOW_CONFIG_FILE = "conf/window.ini"


class MainWindow(QMainWindow):
    class Settings:
        def __init__(self):
            self.seconds = None
            self.minutes = None
            self.hours = None
            self.days = None
            self.date_time = None
            self.scripts = None
            
        def add_seconds(self, seconds):
            if seconds is not None and seconds >= 0 and seconds < 60:
                self.seconds = seconds
                
            return self
                
        def add_minutes(self, minutes):
            if minutes is not None and minutes >= 0 and minutes < 60:
                self.minutes = minutes
                
            return self
        
        def add_hours(self, hours):
            if hours is not None and hours >= 0 and hours < 24:
                self.hours = hours
                
            return self
        
        def add_days(self, days):
            if days is not None and days > 0 and 360:
                self.days = days
                
            return self
        
        def add_date_time(self, datetime):
            self.date_time = datetime
            
        def add_scripts(self, scripts):
            self.scripts = scripts
            
        def __str__(self):
            return f"Seconds: {self.seconds}, Minutes: {self.minutes}, Hours: {self.hours}, Days: {self.days}, datetime: {self.date_time}"
            
                
    def __init__(self):
        log_inf("Initializing MainWindow")

        super(MainWindow, self).__init__()
        self.initUI()
        self.resize(800, 500)

        log_inf("Successfully MainWindow")

    def __del__(self):
        self.__save_config(DEFAULT_WINDOW_CONFIG_FILE)

        log_inf("Destroyed window")

    # config stuff
    def __load_config(self, file_name: str):
        pass

    def __save_config(self, file_name: str):
        config = configparser.ConfigParser()

        config["Default"] = {}
        config["Default"]["style"] = "default"
        config["Default"]["window_name"] = "School finder"
        config["Dimensions"] = {}
        config["Dimensions"]["window_width"] = "200"
        config["Dimensions"]["window_height"] = "200"
        config["Dimensions"]["window_x_pos"] = "100"
        config["Dimensions"]["window_y_pos"] = "100"
        config["Dimensions"]["fullscreen"] = "False"

        try:
            with open(file_name, "w") as configfile:
                config.write(configfile)

            log_inf(f"Saved window conf file {file_name}")
        except:
            log_err(f"Failed to write config to file {file_name}")

    # UI creation
    def initUI(self):
        log_inf("Initializing UI")

        self.__create_main_window()

        log_inf("Successfully inititalized UI")

    def __create_main_window(self):
        self.setGeometry(0, 0, 1080, 720)
        self.setWindowTitle("School finder")
        self.__create_dock()
        self.__create_tweet_area()
        self.__create_central_widget()

        self.setCentralWidget(self.__central_widget)

    def __create_central_widget(self):
        self.__central_widget = QWidget()

        central_widget_layout = QGridLayout()
        central_widget_layout.addWidget(self.__tweet_area)
        central_widget_layout.addWidget(self.__dock, 0, 1)

        self.__central_widget.setLayout(central_widget_layout)

    def __create_dock(self):
        self.__dock = QDockWidget("Parameters")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.__dock)
        scroll = QScrollArea()
        self.__dock.setWidget(scroll)
        scroll.setWidgetResizable(True)

        parameters = QWidget()
        scroll.setWidget(parameters)
        vlay = QVBoxLayout(parameters)
        vlay.addWidget(self.__create_schedule_intervals_box())
        vlay.addWidget(self.__create_schedule_date())
        vlay.addWidget(self.__create_script_box())

    def __create_tweet_area(self):
        self.__tweet_area = QWidget()

        layout = QVBoxLayout()
        self.__tweet_text = QPlainTextEdit()
        self.__submit_button = QPushButton()
        self.__submit_button.setText("Submit")
        self.__submit_button.setIcon(QIcon("res/icons/twitter_logo.png"))
        self.__submit_button.clicked.connect(self.__post_tweet)

        layout.addWidget(self.__tweet_text)
        layout.addWidget(self.__submit_button)
        self.__tweet_area.setLayout(layout)

    def __create_schedule_intervals_box(self):
        widget = QWidget()
        seconds_checkbox = QCheckBox("Seconds")
        seconds_checkbox.stateChanged.connect(self.__change_seconds_state)
        minutes_checkbox = QCheckBox("Minutes")
        minutes_checkbox.stateChanged.connect(self.__change_minutes_state)
        hours_checkbox = QCheckBox("Hours")
        hours_checkbox.stateChanged.connect(self.__change_hours_state)
        days_checkbox = QCheckBox("Days")
        days_checkbox.stateChanged.connect(self.__change_days_state)

        self.__seconds_line = QLineEdit()
        self.__seconds_line.setEnabled(False)
        self.__minutes_line = QLineEdit()
        self.__minutes_line.setEnabled(False)
        self.__hours_line = QLineEdit()
        self.__hours_line.setEnabled(False)
        self.__days_line = QLineEdit()
        self.__days_line.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(seconds_checkbox, 0, 0)
        layout.addWidget(minutes_checkbox, 1, 0)
        layout.addWidget(hours_checkbox, 2, 0)
        layout.addWidget(days_checkbox, 3, 0)
        layout.addWidget(self.__seconds_line, 0, 1)
        layout.addWidget(self.__minutes_line, 1, 1)
        layout.addWidget(self.__hours_line, 2, 1)
        layout.addWidget(self.__days_line, 3, 1)

        widget.setLayout(layout)
        return widget

    def __create_schedule_date(self):
        widget = QWidget()
        schedule_switch = QCheckBox("Date")
        schedule_switch.stateChanged.connect(self.__change_date_time_state)
        self.__date_time = QDateTimeEdit()
        self.__date_time.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(schedule_switch, 0, 0)
        layout.addWidget(self.__date_time, 0, 1)
        widget.setLayout(layout)
        return widget
    
    def __create_script_box(self):
        widget = QWidget()
        
        self.__scripts_layout = QVBoxLayout()
        self.__scripts_widget = QWidget()
        self.__scripts_widget_layout = QVBoxLayout()
        add_script_button = QPushButton("Add new script")
        add_script_button.clicked.connect(self.__add_new_script)
        
        self.__scripts_layout.addWidget(self.__scripts_widget)
        self.__scripts_layout.addWidget(add_script_button)
        
        widget.setLayout(self.__scripts_layout)
        self.__scripts_widget.setLayout(self.__scripts_widget_layout)
        return widget
    
    def __add_new_script(self):
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel("Name")
        text_area = QLineEdit()
        button = QPushButton()
        button.clicked.connect(self.__choose_script_path)
        
        layout.addWidget(label)
        layout.addWidget(text_area)
        layout.addWidget(button)
        widget.setLayout(layout)
        
        self.__scripts_widget_layout.addWidget(widget)
        
    def __choose_script_path(self):
        file, _ = QFileDialog.getOpenFileName(self, "Choose script", "", "Python Files (*.py)")
        if file:
            sender = self.sender()
            sender.setText(file)

    def __change_seconds_state(self):
        self.__seconds_line.setEnabled(not self.__seconds_line.isEnabled())

    def __change_minutes_state(self):
        self.__minutes_line.setEnabled(not self.__minutes_line.isEnabled())

    def __change_hours_state(self):
        self.__hours_line.setEnabled(not self.__hours_line.isEnabled())

    def __change_days_state(self):
        self.__days_line.setEnabled(not self.__days_line.isEnabled())
        
    def __change_date_time_state(self):
        self.__date_time.setEnabled(not self.__date_time.isEnabled())

    # tweet posting
    def __post_tweet(self):
        content = {"text": self.__tweet_text.toPlainText()}
        return_code = post(content)
        settings = self.__gather_settings()

        try:
            check_return_code(return_code)
            log_inf(f"Posted successfully")
        except TweetNotPostedException as e:
            log_err(e)
            
    def __gather_settings(self):
        settings = self.Settings()
        
        if self.__seconds_line.isEnabled():
            settings.add_seconds(self.__convert_val(self.__seconds_line.text()))
        if self.__minutes_line.isEnabled():
            settings.add_minutes(self.__convert_val(self.__minutes_line.text()))
        if self.__hours_line.isEnabled():
            settings.add_hours(self.__convert_val(self.__hours_line.text()))
        if self.__days_line.isEnabled():
            settings.add_days(self.__convert_val(self.__days_line.text()))
        if self.__date_time.isEnabled():
            settings.add_date_time(self.__date_time.dateTime())
            
        print(str(settings))
        return settings
            
    def __convert_val(self, val):
        try:
            return int(val)
        except ValueError as e:
            log_err(e)
    
    def __convert_scripts(self):
        pass


main_window = None


def set_main_window(window):
    global main_window
    main_window = window


def get_main_window():
    global main_window
    return main_window
