import configparser
import time
import os
import pyperclip

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMainWindow,
    QGridLayout,
    QWidget,
    QPlainTextEdit,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QErrorMessage,
    QMessageBox,
    qApp,
    QAction
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
DEFAULT_TEMPLATE_SCRIPT_PATH = 'src/script_template.py'

class InvalidSettingException(Exception):
    pass


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
            if seconds is not None:
                if seconds >= 0 and seconds < 60:
                    self.seconds = seconds
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for seconds variable: range 0-59, provided: {seconds}"
                    )

        def add_minutes(self, minutes):
            if minutes is not None:
                if minutes >= 0 and minutes < 60:
                    self.minutes = minutes
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for minutes variable: range 0-59, provided: {minutes}"
                    )

        def add_hours(self, hours):
            if hours is not None:
                if hours >= 0 and hours < 24:
                    self.hours = hours
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for hours variable: range 0-23, provided: {hours}"
                    )

            return self

        def add_days(self, days):
            if days is not None:
                if days > 0 and 360:
                    self.days = days
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for days variable: range 0-365, provided: {days}"
                    )

            return self

        def add_date_time(self, datetime):
            current_date = QtCore.QDateTime.currentDateTime().date()
            current_time = QtCore.QDateTime.currentDateTime().time()

            if datetime is not None:
                if datetime.date() > current_date and datetime.time() > current_time:
                    self.date_time = datetime
                    self.is_scheduled = True
                else:
                    raise InvalidSettingException(
                        f"Date variable can't be in the past!"
                    )

        def add_scripts(self, scripts):
            self.scripts = scripts

        def __str__(self):
            return f"Seconds: {self.seconds}, Minutes: {self.minutes}, Hours: {self.hours}, Days: {self.days}, datetime: {self.date_time}"

    def __init__(self, screen):
        log_inf("Initializing MainWindow")

        super(MainWindow, self).__init__()
        self.__screen = screen
        self.initUI()
        self.resize(1000, 500)
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
        
    def closeEvent(self, event):
        if self.__show_exit_prompt() == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def __exit(self):
        if self.__show_exit_prompt() == QMessageBox.Yes:
            qApp.exit()
            
    def __show_exit_prompt(self):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', 
                        quit_msg, QMessageBox.Yes, QMessageBox.No, QMessageBox.Yes)
        
        return reply

    def __create_main_window(self):
        self.setGeometry(0, 0, 1080, 720)
        self.setWindowTitle("School finder")
        self.__create_dock()
        self.__create_tweet_area()
        self.__create_central_widget()
        self.__create_menu()

        self.setCentralWidget(self.__central_widget)

    def __create_central_widget(self):
        self.__central_widget = QWidget()

        central_widget_layout = QGridLayout()
        central_widget_layout.addWidget(self.__tweet_area, 0, 0, 1, 2)
        central_widget_layout.addWidget(self.__dock, 0, 2)

        self.__central_widget.setLayout(central_widget_layout)
        
    def __create_menu(self):
        self.__create_file_menu()
        self.__create_help_menu()
        
    def __create_file_menu(self):
        exit_act = QAction('Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(self.__exit)
        
        load_tweet_act = QAction('Load tweet', self)
        load_tweet_act.setShortcut('Ctrl+L')
        load_tweet_act.setStatusTip('Load your tweet from .txt file!')
        load_tweet_act.triggered.connect(self.__load_tweet)
        
        save_tweet_act = QAction('Save tweet', self)
        save_tweet_act.setShortcut('Ctrl+S')
        save_tweet_act.setStatusTip('Save your tweet to file!')
        save_tweet_act.triggered.connect(self.__save_tweet)
        
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(exit_act)
        file_menu.addAction(load_tweet_act)
        file_menu.addAction(save_tweet_act)
        file_menu.setMinimumWidth(200)
        
    def __create_help_menu(self):
        interval_act = QAction('Intervals', self)
        interval_act.setStatusTip('Help about intervals section')
        interval_act.triggered.connect(self.__show_intervals_help)
        
        date_act = QAction('Schedule', self)
        date_act.setStatusTip('Help about schedule section')
        date_act.triggered.connect(self.__show_schedule_help)
        
        scripts_act = QAction('Scripts', self)
        scripts_act.setStatusTip('Help about scripts section')
        scripts_act.triggered.connect(self.__show_scripts_help)
        
        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction(interval_act)
        help_menu.addAction(date_act)
        help_menu.addAction(scripts_act)
        help_menu.setMinimumWidth(200)
        
    def __show_intervals_help(self):
        msg = """Intervals consists of 4 main areas, each specifying the time to post new Tweet\n
Example of filled areas: Seconds 20 Days 4 \n   This means, bot will post new Tweet every day which is divisble by 4 and second divisble by 20\n
Notice that both requirements must be fullfiled!\n\nPossible values:\n   Seconds: 0-59\n   Minutes: 0-59\n   Hours: 0-23\n   Days: 1-365"""
        QMessageBox.information(self, 'Intervals help', msg)
        
    def __show_schedule_help(self):
        msg = """Schedule consists of 1 area which is date-time.\nMain purpose is to schedule time of posting Tweet to never miss perfect time.\n
To use simply check box on the left and insert date.\n
Warning - date can't be in the past!"""
        QMessageBox.information(self, 'Schedule help', msg)
        
    def __show_scripts_help(self):
        msg = """Scripts area is definetly the most interesting one!\nTo start creating variables dependent on script, simply click 'Save' button below and paste it's content to python file.\n
Inside the file there's instruction how to write your own script.\nWhen you're ready it's time to use it in the bot!\n\nFirst - import the script by pressing 'Add new script' button.
Next, name your variable in the area to the left, it can be whatever you want!\n\nLast step is to use it in actual Tweet:\nFind a place where you want to put your variable.
Then simply write it's name inside curly braces {}, it's that simple!\nFor example if you choose to name your variable 'cat', then inside your Tweet insert {cat}.\n
If you're not sure if everything works, simply click 'Check' button, in case of errors, help will be provided."""
        reply = QMessageBox.information(self, 'Intervals help', msg, QMessageBox.Ok, QMessageBox.Save)
        
        if reply == QMessageBox.Save:
            content = self.__load_script_template()
            if content is not None:
                pyperclip.copy(content)
                spam = pyperclip.paste()
            
    def __load_script_template(self):
        try:
            with open(DEFAULT_TEMPLATE_SCRIPT_PATH, 'r') as file:
                return file.read()
        except Exception as e:
            self.__show_error_dialog("Failed to copy content, make sure that script_template.py file is not deleted!")
            return None
            

    def __create_dock(self):
        self.__dock = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        parameters = QWidget()
        scroll.setWidget(parameters)
        vlay = QVBoxLayout(parameters)
        vlay.addWidget(self.__create_schedule_intervals_box())
        vlay.addWidget(self.__create_schedule_date())
        vlay.addWidget(self.__create_script_box())

        docklayout = QVBoxLayout(self.__dock)
        docklayout.addWidget(scroll)

    def __create_tweet_area(self):
        self.__tweet_area = QWidget()

        layout = QGridLayout()
        self.__tweet_text = QPlainTextEdit()
        self.__test_tweet_text = QPlainTextEdit()

        self.__submit_button = QPushButton("Submit")
        self.__submit_button.setIcon(QIcon("res/icons/twitter_logo.png"))
        self.__submit_button.clicked.connect(self.__post_tweet)

        self.__stop_button = QPushButton("Stop")
        self.__stop_button.setIcon(QIcon("res/icons/stop.png"))
        self.__stop_button.clicked.connect(self.__stop_timer)

        self.__test_output_button = QPushButton("Check")
        # self.__test_output_button.setIcon(QIcon(''))
        self.__test_output_button.clicked.connect(self.__handle_test_tweet_area)

        layout.addWidget(QLabel("Write your tweet here!"), 0, 0, 1, 3)
        layout.addWidget(self.__tweet_text, 1, 0, 1, 3)
        layout.addWidget(QLabel("Check output here!"), 2, 0, 1, 3)
        layout.addWidget(self.__test_tweet_text, 3, 0, 1, 3)
        layout.addWidget(self.__submit_button, 4, 0)
        layout.addWidget(self.__stop_button, 4, 1)
        layout.addWidget(self.__test_output_button, 4, 2)
        self.__tweet_area.setMinimumWidth(int(self.size().width() / 5 * 3))
        self.__tweet_area.setLayout(layout)

    def __create_schedule_intervals_box(self):
        widget = QWidget()

        interval_label = QLabel()
        interval_label.setText("<font color=#2798f5>INTERVALS</font>")
        interval_label.setFont(QtGui.QFont("Open sans", weight=QtGui.QFont.Bold))
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
        layout.addWidget(interval_label, 0, 0)
        layout.addWidget(seconds_checkbox, 1, 0)
        layout.addWidget(minutes_checkbox, 2, 0)
        layout.addWidget(hours_checkbox, 3, 0)
        layout.addWidget(days_checkbox, 4, 0)
        layout.addWidget(self.__seconds_line, 1, 1)
        layout.addWidget(self.__minutes_line, 2, 1)
        layout.addWidget(self.__hours_line, 3, 1)
        layout.addWidget(self.__days_line, 4, 1)
        layout.setSpacing(10)

        widget.setLayout(layout)
        return widget

    def __create_schedule_date(self):
        widget = QWidget()
        schedule_label = QLabel()
        schedule_label.setText("<font color=#2798f5>SCHEDULE</font>")
        schedule_label.setFont(QtGui.QFont("Open sans", weight=QtGui.QFont.Bold))
        schedule_switch = QCheckBox("Date")
        schedule_switch.stateChanged.connect(self.__change_date_time_state)
        self.__date_time = QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.__date_time.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(schedule_label, 0, 0)
        layout.addWidget(schedule_switch, 1, 0)
        layout.addWidget(self.__date_time, 1, 1)
        widget.setLayout(layout)
        return widget

    def __create_script_box(self):
        widget = QWidget()

        scripts_label = QLabel()
        scripts_label.setText("<font color=#2798f5>SCRIPTS</font>")
        scripts_label.setFont(QtGui.QFont("Open sans", weight=QtGui.QFont.Bold))
        self.__scripts_layout = QVBoxLayout()
        self.__scripts_widget = QWidget()
        self.__scripts_widget_layout = QVBoxLayout()
        self.__paths_list = []
        self.__scripts_val_list = []
        add_script_button = QPushButton("Add new script")
        add_script_button.clicked.connect(self.__add_new_script)

        self.__scripts_layout.addWidget(scripts_label)
        self.__scripts_layout.addWidget(
            self.__scripts_widget, alignment=QtCore.Qt.AlignLeft
        )
        self.__scripts_layout.addWidget(
            add_script_button
        )

        widget.setLayout(self.__scripts_layout)
        self.__scripts_widget.setLayout(self.__scripts_widget_layout)
        return widget

    def __add_new_script(self):
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel("Name")

        text_area = QLineEdit()
        text_area.setMinimumWidth(int(self.size().width() / 13))
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
        if not self.__settings:
            return

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
            self.__show_error_dialog(
                "There was a problem with posting your tweet! Check if content is not same as last tweet!"
            )
            log_err(e)

    def __gather__all_tweet_data(self):
        content = self.__tweet_text.toPlainText()
        if self.has_script:
            var_script_pair = self.__convert_scripts()
            if not var_script_pair:
                return None

            content = self.__handle_tweet_vals_replacement(content, var_script_pair)
            if not content:
                return None
        if not content:
            self.__show_error_dialog("Tweet area is empty!")
            return None

        return content
    
    def __load_tweet(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose file to load", "", "All Files (*.*)"
        )
        
        try:
            with open(filename, 'r') as file:
                self.__tweet_text.setPlainText(file.read())
            self.__show_info_dialog(f"Successfully loaded {filename}!")
        except Exception as e:
            self.__show_error_dialog(str(e))
            
    def __save_tweet(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Choose file to save", "", "All Files (*.*)"
        )
        
        try:
            with open(filename, 'w') as file:
                file.write(self.__tweet_text.toPlainText())
            self.__show_info_dialog(f"Successfully saved {filename}!")
        except Exception as e:
            self.__show_error_dialog(str(e))
        

    def __gather_settings(self):
        settings = self.Settings()

        try:
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
        except InvalidSettingException as e:
            self.__show_error_dialog(str(e))
            return None

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
                self.__show_error_dialog(
                    "Error: one of areas is not filled correctly, can't submit!"
                )
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
            self.__show_error_dialog(
                f"Atleast one of the script variables didn't match in tweet content: {missing_vals}"
            )
            return None

        return replaced_content

    def __handle_test_tweet_area(self):
        content = self.__gather__all_tweet_data()

        if content:
            self.__test_tweet_text.setPlainText(content)


main_window = None


def set_main_window(window):
    global main_window
    main_window = window


def get_main_window():
    global main_window
    return main_window
