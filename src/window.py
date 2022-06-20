import configparser
import time
import os

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
    QFileDialog,
    QErrorMessage,
    QMessageBox
)
from PyQt5.QtGui import QIcon

from twitter_management.tweet_parsers import parse_tweet
from script_runner import run_script
from helpers.logger import log_inf, log_err
from widgets.collapsible_box import CollapsibleBox
from twitter_management.post_tweet import (
    TweetNotPostedException,
    post,
    check_return_code,
)

SCRIPT_PATH_PREFIX = "script_outputs"
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
            self.is_scheduled = False
            self.is_interval = False

        def add_seconds(self, seconds):
            if seconds is not None and seconds >= 0 and seconds < 60:
                self.seconds = seconds
                self.is_interval = True

            return self

        def add_minutes(self, minutes):
            if minutes is not None and minutes >= 0 and minutes < 60:
                self.minutes = minutes
                self.is_interval = True

            return self

        def add_hours(self, hours):
            if hours is not None and hours >= 0 and hours < 24:
                self.hours = hours
                self.is_interval = True

            return self

        def add_days(self, days):
            if days is not None and days > 0 and 360:
                self.days = days
                self.is_interval = True

            return self

        def add_date_time(self, datetime):
            self.date_time = datetime
            self.is_scheduled = True

        def add_scripts(self, scripts):
            self.scripts = scripts

        def __str__(self):
            return f"Seconds: {self.seconds}, Minutes: {self.minutes}, Hours: {self.hours}, Days: {self.days}, datetime: {self.date_time}"

    def __init__(self):
        log_inf("Initializing MainWindow")

        super(MainWindow, self).__init__()
        self.initUI()
        self.resize(800, 500)
        self.__timer = None
        self.__settings = self.Settings()
        self.has_script = False

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

        layout = QGridLayout()
        self.__tweet_text = QPlainTextEdit()

        self.__submit_button = QPushButton("Submit")
        self.__submit_button.setIcon(QIcon("res/icons/twitter_logo.png"))
        self.__submit_button.clicked.connect(self.__post_tweet)

        self.__stop_button = QPushButton("Stop")
        self.__stop_button.setIcon(QIcon("res/icons/stop.png"))
        self.__stop_button.clicked.connect(self.__stop_timer)

        layout.addWidget(self.__tweet_text, 0, 0, 1, 2)
        layout.addWidget(self.__submit_button, 1, 0)
        layout.addWidget(self.__stop_button, 1, 1)
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
        self.__paths_list = []
        self.__scripts_val_list = []
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
        
        self.__scripts_val_list.append(text_area)
        button = QPushButton("Add new script")
        button.clicked.connect(self.__choose_script_path)

        layout.addWidget(label)
        layout.addWidget(text_area)
        layout.addWidget(button)
        widget.setLayout(layout)
        
        self.has_script = True

        self.__scripts_widget_layout.addWidget(widget)

    def __choose_script_path(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Choose script", "", "Python Files (*.py)"
        )
        if file:
            sender = self.sender()
            sender.setText(os.path.basename(file))
            self.__paths_list.append(file)
            run_script(file)

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
        self.__settings = self.__gather_settings()
        if self.__settings.is_scheduled or self.__settings.is_interval:
            self.__start_timer()
        else:
            self.__post_single_tweet()

    def __post_single_tweet(self):
        content = self.__tweet_text.toPlainText()
        if self.has_script:
            var_script_pair = self.__convert_scripts()
            if not var_script_pair:
                return
            
            content = self.__handle_tweet_vals_replacement(content, var_script_pair)
            if not content:
                return
        if not content:
            self.__show_error_dialog("Tweet area is empty!")
            return
        
        return_code = post({"text": content})

        try:
            check_return_code(return_code)
            self.__show_info_dialog("Your tweet has been posted successfully!")
            log_inf(f"Posted successfully")
        except TweetNotPostedException as e:
            self.__show_error_dialog("There was a problem with posting your tweet! Check if content is not same as last tweet!")
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

        return settings

    def __check_interval_tweet(self):
        day, hour, min, sec = map(int, time.strftime("%d %H %M %S").split())
        
        if self.__settings.seconds:
            if sec % self.__settings.seconds != 0:
                return

        if self.__settings.minutes:
            if min % self.__settings.minutes != 0:
                return

        if self.__settings.hours:
            if hour % self.__settings.hours != 0:
                return

        if self.__settings.days:
            if day % self.__settings.days != 0:
                return

        self.__post_single_tweet()

    def __check_scheduled_tweet(self):
        current_date = QtCore.QDateTime.currentDateTime().date()
        current_time = QtCore.QDateTime.currentDateTime().time()
        scheduled_time = self.__settings.date_time

        if (
            current_date == scheduled_time.date()
            and current_time.hour() == scheduled_time.time().hour()
            and current_time.minute() == scheduled_time.time().minute()
        ):
            self.__post_single_tweet()
            self.__timer.stop()

    def __start_timer(self):
        self.__timer = QtCore.QTimer()

        if self.__settings.is_scheduled:
            self.__timer.timeout.connect(self.__check_scheduled_tweet)
        elif self.__settings.is_interval:
            self.__timer.timeout.connect(self.__check_interval_tweet)
        self.__timer.start(1000)

    def __stop_timer(self):
        if self.__timer:
            self.__timer.stop()

    def __convert_val(self, val):
        try:
            return int(val)
        except ValueError as e:
            log_err(e)
            
    def __show_error_dialog(self, text):
        error_dialog = QErrorMessage()
        error_dialog.showMessage(text)
        error_dialog.exec_()
        
    def __show_info_dialog(self, text):
        dialog = QMessageBox.information(self, "Info!", text)

    def __convert_scripts(self):
        scripts_val_dict = {}
        i = 0
        for i in range(0, len(self.__scripts_val_list)):
            try:
                script = self.__paths_list[i]
                var = self.__scripts_val_list[i]
                run_script(script)
                var_script_pair = self.__build_var_script_pair(var, script)
                if var_script_pair:
                    scripts_val_dict[var_script_pair[0]] = var_script_pair[1]
            except:
                self.__show_error_dialog("Error: one of areas is not filled correctly, can't submit!")
                return None
            
        return scripts_val_dict
                
    def __load_script_value_from_file(self, path):
        filename = os.path.basename(path)[:-3]
        filename = f"{SCRIPT_PATH_PREFIX}/{filename}.txt"
        
        with open(filename, "r") as file:
            return file.read()
        
    def __build_var_script_pair(self, text_area, script):
        try:
            var = self.__check_var_value(text_area)
            script_val = self.__load_script_value_from_file(script)
            
            print(f"VAR: |{var}| len: {len(var)}")
            if len(var) > 0 and script_val:
                return (var, script_val)
            else:
                self.__show_error_dialog(f"Script or var areas are not filled!")
        except Exception as e:
            self.__show_error_dialog(f"Failed to load var name or script, error: {e}")
            return None
                
        
    def __check_var_value(self, text_area):
        return text_area.text() if not None else None
    
    def __handle_tweet_vals_replacement(self, content, var_script_dict):
        replaced_content, missing_vals = parse_tweet(content, var_script_dict)
        if missing_vals:
            self.__show_error_dialog(f"Atleast one of the script variables didn't match in tweet content: {missing_vals}")
            return None
        
        return replaced_content
    
        


main_window = None


def set_main_window(window):
    global main_window
    main_window = window


def get_main_window():
    global main_window
    return main_window
