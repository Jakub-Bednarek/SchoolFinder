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
    QAction,
    QDesktopWidget,
)
from PyQt5.QtGui import QIcon

from twitter_management.tweet_parsers import parse_tweet
from script_runner import run_script
from helpers.logger import log_inf, log_err
from twitter_management.post_tweet import (
    TweetNotPostedException,
    post,
    check_return_code,
)

SCRIPT_PATH_PREFIX = "script_outputs"
DEFAULT_WINDOW_CONFIG_FILE = "conf/window.ini"
DEFAULT_TEMPLATE_SCRIPT_PATH = "src/script_template.py"


class InvalidSettingException(Exception):
    pass


class MainWindow(QMainWindow):
    """Class that handles all GUI elements of Tweet area and parameters section"""
    class Settings:
        """Class representing settings that are included when posting Tweet"""
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
            """Adds seconds to settings instance, must be in range 0-59
            
            Parameters:
                seconds (int): seconds to set"""
            if seconds is not None:
                if self.__check_if_value_convertible(seconds) and seconds >= 0 and seconds < 60:
                    self.seconds = seconds
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for seconds variable: range 0-59, provided: {seconds}"
                    )

        def add_minutes(self, minutes):
            """Adds minutes to settings instance, must be in range 0-59
            
            Parameters:
                minutes (int): minutes to set"""
            if minutes is not None:
                if self.__check_if_value_convertible(minutes) and minutes >= 0 and minutes < 60:
                    self.minutes = minutes
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for minutes variable: range 0-59, provided: {minutes}"
                    )

        def add_hours(self, hours):
            """Adds hours to settings instance, must be in range 0-23
            
            Parameters:
                hours (int): hours to set"""
            if hours is not None:
                if self.__check_if_value_convertible(hours) and hours >= 0 and hours < 24:
                    self.hours = hours
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for hours variable: range 0-23, provided: {hours}"
                    )

            return self

        def add_days(self, days):
            """Adds days to settings instance, must be in range 0-365
            
            Parameters:
                days (int): days to set"""
            if days is not None:
                if self.__check_if_value_convertible(days) and days > 0 and 360:
                    self.days = days
                    self.is_interval = True
                else:
                    raise InvalidSettingException(
                        f"Invalid value for days variable: range 0-365, provided: {days}"
                    )

            return self

        def add_date_time(self, datetime):
            """Adds date_time to settings instance for schedule section, can't be in past
            
            Parameters:
                datetime (QDateTime): date to set"""
            current_date = QtCore.QDateTime.currentDateTime()

            if datetime is not None:
                print(f"datetime: {datetime}, current: {current_date}")
                if datetime > current_date:
                    self.date_time = datetime
                    self.is_scheduled = True
                else:
                    raise InvalidSettingException(
                        f"Date variable can't be in the past!"
                    )
                    
        def get_interval(self):
            """Converts interval settings to string that is readable by QDateTime widget
            
            Returns:
                str: Converted value for interval settings"""
            out_str = []
            if self.seconds:
                out_str.append(f"\n   Seconds: {self.seconds} ")
            if self.minutes:
                out_str.append(f"\n   Minutes: {self.minutes} ")
            if self.hours:
                out_str.append(f"\n   Hours: {self.hours} ")
            if self.days:
                out_str.append(f"\n   Days: {self.days}")
            
            return "".join(out_str)

        def __check_if_value_convertible(self, value):
            try:
                return int(value)
            except:
                messageBox = QErrorMessage()
                messageBox.showMessage(f"Invalid value provided: {value}")
                messageBox.exec_()
                return False

        def __str__(self):
            return f"Seconds: {self.seconds}, Minutes: {self.minutes}, Hours: {self.hours}, Days: {self.days}, datetime: {self.date_time}"

    def __init__(self, screen):
        log_inf("Initializing MainWindow")

        super(MainWindow, self).__init__()
        self.initUI()
        self.resize(1000, 500)
        self.__timer = None
        self.__settings = self.Settings()
        self.has_script = False
        self.__load_config(DEFAULT_WINDOW_CONFIG_FILE)

        log_inf("Successfully MainWindow")

    # config stuff
    def __load_config(self, file_name: str):
        """Loads config file for MainWindow class.
        
            Parameters:
                file_name (str): Name of config file"""
        log_inf(f"Loading config file {file_name}")
        self.__config = configparser.ConfigParser()
        self.__config.read(DEFAULT_WINDOW_CONFIG_FILE)

        try:
            self.__load_window_title_conf()
            self.__load_window_size_conf()
            self.__load_window_pos_conf()

            self.__load_interval_values_conf()
            self.__load_schedule_values_conf()

            self.__load_twitter_area_conf()
            log_inf(f"Loaded config file {file_name}")
        except Exception as e:
            log_err(f"Failed to load config file {file_name}, error: {e}")
            self.__show_error_dialog(str(e))

    def __save_config(self, file_name: str):
        """Saves config file for MainWindow class.
        
            Parameters:
                file_name (str): Name of config file to save settings"""
        log_inf(f"Loading config {file_name}")
        config = configparser.ConfigParser()

        config["Default"] = {}
        config["Default"]["window_name"] = self.windowTitle()

        config = self.__save_window_values(config)
        config = self.__save_parameters_values(config)
        config = self.__save_twitter_area(config)

        try:
            with open(file_name, "w") as configfile:
                config.write(configfile)
            log_inf(f"Saved config file {file_name}")
        except Exception as e:
            log_err(f"Failed to save config file {file_name}, error: {e}")

    def __save_window_values(self, config):
        """Saves Dimensions of MainWindow.
        
            Parameters:
                config (ConfigParser): instance of ConfigParser that collects settings"""
                
        config["Dimensions"] = {}
        config["Dimensions"]["window_width"] = str(self.size().width())
        config["Dimensions"]["window_height"] = str(self.size().height())
        config["Dimensions"]["window_x_pos"] = str(self.pos().x())
        config["Dimensions"]["window_y_pos"] = str(self.pos().y())

        return config

    def __save_parameters_values(self, config):
        """Saves Parameters of MainWindow.
        
            Parameters:
                config (ConfigParser): instance of ConfigParser that collects settings"""
        config["Parameters"] = {}
        settings = self.__gather_settings()

        if not settings:
            log_err("Failed to save parameters settings")
            return

        if settings.seconds:
            config["Parameters"]["seconds"] = str(settings.seconds)
        else:
            config["Parameters"]["seconds"] = "0"
        if settings.minutes:
            config["Parameters"]["minutes"] = str(settings.minutes)
        else:
            config["Parameters"]["minutes"] = "0"
        if settings.hours:
            config["Parameters"]["hours"] = str(settings.hours)
        else:
            config["Parameters"]["hours"] = "0"
        if settings.days:
            config["Parameters"]["days"] = str(settings.days)
        else:
            config["Parameters"]["days"] = "0"
        if settings.date_time:
            config["Parameters"]["date"] = str(
                settings.date_time.toString("yyyy,M,d,h,m,s")
            )

        return config

    def __save_twitter_area(self, config):
        """Saves Twitter area of MainWindow.
        
            Parameters:
                config (ConfigParser): instance of ConfigParser that collects settings"""
        config["Twitter area"] = {}
        config["Twitter area"]["content"] = self.__tweet_text.toPlainText()

        return config

    # Window config loading functions
    def __load_window_title_conf(self):
        """Loads title of MainWindow"""
        
        if "Default" in self.__config:
            if "window_name" in self.__config["Default"]:
                self.setWindowTitle(self.__config["Default"]["window_name"])

    def __load_window_size_conf(self):
        """Loads Dimensions of MainWindow"""
        
        if "Dimensions" in self.__config:
            if "window_width" in self.__config["Dimensions"]:
                self.setFixedWidth(int(self.__config["Dimensions"]["window_width"]))
            if "window_height" in self.__config["Dimensions"]:
                self.setFixedHeight(int(self.__config["Dimensions"]["window_height"]))

    def __load_window_pos_conf(self):
        """Loads position of MainWindow"""
        
        screen = QDesktopWidget().screenGeometry()
        if "Dimensions" in self.__config:
            if (
                "window_x_pos" in self.__config["Dimensions"]
                and "window_y_pos" in self.__config["Dimensions"]
            ):
                x = int(self.__config["Dimensions"]["window_x_pos"])
                y = int(self.__config["Dimensions"]["window_y_pos"])
                self.move(x, y)

    # Settings config loading functions
    def __load_interval_values_conf(self):
        """Loads interval values of Interval Section"""
        
        if "Parameters" in self.__config:
            if "seconds" in self.__config["Parameters"]:
                self.__seconds_line.setText(self.__config["Parameters"]["seconds"])
            if "minutes" in self.__config["Parameters"]:
                self.__minutes_line.setText(self.__config["Parameters"]["minutes"])
            if "hours" in self.__config["Parameters"]:
                self.__hours_line.setText(self.__config["Parameters"]["hours"])
            if "days" in self.__config["Parameters"]:
                self.__days_line.setText(self.__config["Parameters"]["days"])

    def __load_schedule_values_conf(self):
        if "Parameters" in self.__config:
            if "date" in self.__config["Parameters"]:
                date = self.__config["Parameters"]["date"].split(",")
                date_time = QtCore.QDateTime(
                    int(date[0]),
                    int(date[1]),
                    int(date[2]),
                    int(date[3]),
                    int(date[4]),
                    int(date[5]),
                )
                self.__date_time.setDateTime(date_time)

    # Twitter post loading functions
    def __load_twitter_area_conf(self):
        """Loads Twitter area of MainWindow"""
        if "Twitter area" in self.__config:
            if "content" in self.__config["Twitter area"]:
                self.__tweet_text.setPlainText(self.__config["Twitter area"]["content"])

    # UI creation
    def initUI(self):
        """Inialies UI for MainWindow"""
        log_inf("Initializing UI")

        self.__create_main_window()
        self.setWindowIcon(QIcon('src/icons/twitter_logo.png'))

        log_inf("Successfully inititalized UI")

    def closeEvent(self, event):
        """Overloaded event for application close event"""
        if self.__show_exit_prompt() == QMessageBox.Yes:
            self.__save_config(DEFAULT_WINDOW_CONFIG_FILE)
            event.accept()
        else:
            event.ignore()

    def __exit(self):
        """Function asking whether user wants to exit or not"""
        if self.__show_exit_prompt() == QMessageBox.Yes:
            log_inf("Exiting app")
            qApp.exit()

    def __show_exit_prompt(self):
        """Function showing exit prompt returning value of user answer.
        
        Returns:
            reply: users answer"""
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(
            self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No
        )

        return reply

    def __create_main_window(self):
        """Function that creates all areas of main window"""
        self.__create_dock()
        self.__create_tweet_area()
        self.__create_central_widget()
        self.__create_menu()

        self.setCentralWidget(self.__central_widget)

    def __create_central_widget(self):
        """Function creating central widget of MainWindow"""
        self.__central_widget = QWidget()

        central_widget_layout = QGridLayout()
        central_widget_layout.addWidget(self.__tweet_area, 0, 0, 1, 2)
        central_widget_layout.addWidget(self.__dock, 0, 2)

        self.__central_widget.setLayout(central_widget_layout)

    def __create_menu(self):
        """Function calling all functions that create new menu tabs"""
        self.__create_file_menu()
        self.__create_edit_menu()
        self.__create_help_menu()

    def __create_file_menu(self):
        """Function creates file menu tab with all actions connected to the buttons"""
        load_tweet_act = QAction("Load tweet", self)
        load_tweet_act.setShortcut("Ctrl+L")
        load_tweet_act.setStatusTip("Load your tweet from .txt file!")
        load_tweet_act.triggered.connect(self.__load_tweet)

        save_tweet_act = QAction("Save tweet", self)
        save_tweet_act.setShortcut("Ctrl+S")
        save_tweet_act.setStatusTip("Save your tweet to file!")
        save_tweet_act.triggered.connect(self.__save_tweet)
        
        exit_act = QAction("Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.setStatusTip("Exit application")
        exit_act.triggered.connect(self.__exit)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(load_tweet_act)
        file_menu.addAction(save_tweet_act)
        file_menu.addAction(exit_act)
        file_menu.setMinimumWidth(200)
        
    def __create_edit_menu(self):
        """Function creates edit menu tab with all actions connected to the buttons"""
        clear_tweet_area_act = QAction("Clear area", self)
        clear_tweet_area_act.setStatusTip("Clear tweet area")
        clear_tweet_area_act.setShortcut("Ctrl+D")
        clear_tweet_area_act.triggered.connect(self.__clear_tweet_area)
        
        copy_tweet_area_act = QAction("Copy", self)
        copy_tweet_area_act.setStatusTip("Copy tweet area")
        copy_tweet_area_act.setShortcut("Ctrl+C")
        copy_tweet_area_act.triggered.connect(self.__copy_tweet_area)
        
        paste_tweet_area_act = QAction("Paste", self)
        paste_tweet_area_act.setStatusTip("Paste to tweet area")
        paste_tweet_area_act.setShortcut("Ctrl+V")
        paste_tweet_area_act.triggered.connect(self.__paste_tweet_area)
        
        cut_clear_area_act = QAction("Cut area", self)
        cut_clear_area_act.setStatusTip("Cut tweet area")
        cut_clear_area_act.setShortcut("Ctrl+X")
        cut_clear_area_act.triggered.connect(self.__cut_tweet_area)
        
        edit_menu = self.menuBar().addMenu("Edit")
        edit_menu.addAction(clear_tweet_area_act)
        edit_menu.addAction(copy_tweet_area_act)
        edit_menu.addAction(paste_tweet_area_act)
        edit_menu.addAction(cut_clear_area_act)
        edit_menu.setMinimumWidth(200)

    def __create_help_menu(self):
        """Function creates help menu tab with all actions connected to the buttons"""
        interval_act = QAction("Intervals", self)
        interval_act.setStatusTip("Help about intervals section")
        interval_act.triggered.connect(self.__show_intervals_help)

        date_act = QAction("Schedule", self)
        date_act.setStatusTip("Help about schedule section")
        date_act.triggered.connect(self.__show_schedule_help)

        scripts_act = QAction("Scripts", self)
        scripts_act.setStatusTip("Help about scripts section")
        scripts_act.triggered.connect(self.__show_scripts_help)
        
        about_act = QAction("About", self)
        about_act.setStatusTip("About the creator")
        about_act.triggered.connect(self.__show_about_help)

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(interval_act)
        help_menu.addAction(date_act)
        help_menu.addAction(scripts_act)
        help_menu.addAction(about_act)
        help_menu.setMinimumWidth(200)

    def __show_intervals_help(self):
        """Function opens QMessageBox with information prompt with Intervals Help message"""
        msg = """Intervals consists of 4 main areas, each specifying the time to post new Tweet\n
Example of filled areas: Seconds 20 Days 4 \n   This means, bot will post new Tweet every day which is divisble by 4 and second divisble by 20\n
Notice that both requirements must be fullfiled!\n\nPossible values:\n   Seconds: 0-59\n   Minutes: 0-59\n   Hours: 0-23\n   Days: 1-365"""
        QMessageBox.information(self, "Intervals help", msg)

    def __show_schedule_help(self):
        """Function opens QMessageBox with information prompt with Intervals Schedule message"""
        msg = """Schedule consists of 1 area which is date-time.\nMain purpose is to schedule time of posting Tweet to never miss perfect time.\n
To use simply check box on the left and insert date.\n
Warning - date can't be in the past!"""
        QMessageBox.information(self, "Schedule help", msg)

    def __show_scripts_help(self):
        """Function opens QMessageBox with information prompt with Scripts Help message. If user answers 'Save', then script template file content gets copied to clipboard"""
        msg = """Scripts area is definetly the most interesting one!\nTo start creating variables dependent on script, simply click 'Save' button below and paste it's content to python file.\n
Inside the file there's instruction how to write your own script.\nWhen you're ready it's time to use it in the bot!\n\nFirst - import the script by pressing 'Add new script' button.
Next, name your variable in the area to the left, it can be whatever you want!\n\nLast step is to use it in actual Tweet:\nFind a place where you want to put your variable.
Then simply write it's name inside curly braces {}, it's that simple!\nFor example if you choose to name your variable 'cat', then inside your Tweet insert {cat}.\n
If you're not sure if everything works, simply click 'Check' button, in case of errors, help will be provided."""
        reply = QMessageBox.information(
            self, "Intervals help", msg, QMessageBox.Ok, QMessageBox.Save
        )

        if reply == QMessageBox.Save:
            content = self.__load_script_template()
            if content is not None:
                pyperclip.copy(content)
                spam = pyperclip.paste()
                
    def __show_about_help(self):
        """Function opens QMessageBox with author informations"""
        msg = """Hi!\nMy name is Jakub Bednarek, Im student of Wroclaw University of Technology and this is my app for Script Languages course.
Application was created with intent to be easy to use and self explanatory.\n
Scripts part may be a bit confusing at first, but give it a go and you will definetly learn it in seconds, it's easy!\n
If there's enough time, Im planning on rewriting app on C++ with server intergration and new features for better Tweet content!
"""
        QMessageBox.information(self, "Schedule help", msg)

    def __load_script_template(self):
        """Function loading script template file
        
        Returns:
            str | None: If file was loaded successfully then file content otherwise None"""
        log_inf("Loading script template")
        try:
            with open(DEFAULT_TEMPLATE_SCRIPT_PATH, "r") as file:
                return file.read()
                log_inf("Successfully read script template")
        except Exception as e:
            self.__show_error_dialog(
                "Failed to copy content, make sure that script_template.py file is not deleted!"
            )
            return None

    def __create_dock(self):
        """Function creates dock area for all settings sections"""
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
        """Function creates tweet area with all widgets inside"""
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
        self.__test_output_button.setIcon(QIcon('res/icons/okay_icon.png'))
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
        """Function creates schedule intervals box
        
        Returns:
            QWidget: widget containing all schedule interval box widgets"""
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
        """Function creates schedule date widget
        
        Returns:
            QWidget: widget containing everything for schedule section"""
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
        """Function creates script box widget
        
        Returns:
            QWidget: widget containing everything for scripts section"""
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
        self.__scripts_layout.addWidget(add_script_button)

        widget.setLayout(self.__scripts_layout)
        self.__scripts_widget.setLayout(self.__scripts_widget_layout)
        return widget

    def __add_new_script(self):
        """Function adds label, text area and button that gets added to scripts list"""
        log_inf("Adding new script")
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel("Name")

        text_area = QLineEdit()
        text_area.setMinimumWidth(int(self.size().width() / 6))
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
        """Function that opens QFileDialog asking to specify path for script.
        If function choosen file is loaded correctly, function calls run_script function for correctness"""
        
        file, _ = QFileDialog.getOpenFileName(
            self, "Choose script", "", "Python Files (*.py)"
        )
        if file:
            sender = self.sender()
            sender.setText(os.path.basename(file))
            self.__paths_list.append(file)
            log_inf(f"Added new script path {file}")
            self.__show_info_dialog(f"Success! Added new script {file}.")
            run_script(file)

    def __change_seconds_state(self):
        """Function changes seconds line state"""
        self.__seconds_line.setEnabled(not self.__seconds_line.isEnabled())

    def __change_minutes_state(self):
        """Function changes minutes line state"""
        self.__minutes_line.setEnabled(not self.__minutes_line.isEnabled())

    def __change_hours_state(self):
        """Function changes hours line state"""
        self.__hours_line.setEnabled(not self.__hours_line.isEnabled())

    def __change_days_state(self):
        """Function changes days line state"""
        self.__days_line.setEnabled(not self.__days_line.isEnabled())

    def __change_date_time_state(self):
        """Function changes date_time line state"""
        self.__date_time.setEnabled(not self.__date_time.isEnabled())

    # tweet posting
    def __post_tweet(self):
        """Function gathers all settings, then decides wheter it's scheduled, interval or normal Tweet and calls proper function"""
        self.__settings = self.__gather_settings()
        if not self.__settings:
            return

        if self.__settings.is_scheduled or self.__settings.is_interval:
            self.__start_timer()
        else:
            self.__post_single_tweet()

    def __post_single_tweet(self):
        """Function posts Tweet and checks whether operation succeded or not, in case of error, user gets dialog with error message"""
        log_inf("Posting single tweet")
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
        """Function gathers Tweet text area and calls functions that converts variables dependent on scripts."""
        log_inf("Gathering tweet data")
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
        """Function loads Tweet content to Tweet area from specified file, in case of error user gets dialog window with error message"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose file to load", "", "All Files (*.*)"
        )

        try:
            with open(filename, "r") as file:
                self.__tweet_text.setPlainText(file.read())
            self.__show_info_dialog(f"Successfully loaded {filename}!")
        except Exception as e:
            self.__show_error_dialog(str(e))

    def __save_tweet(self):
        """Function saves Tweet content to specified file from Tweet area, in case of error user gets dialog window with error message"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Choose file to save", "", "All Files (*.*)"
        )

        try:
            with open(filename, "w") as file:
                file.write(self.__tweet_text.toPlainText())
            self.__show_info_dialog(f"Successfully saved {filename}!")
        except Exception as e:
            self.__show_error_dialog(str(e))
            
    def __copy_tweet_area(self):
        """"Function copies Tweet area to users clipboard"""
        content = self.__tweet_text.toPlainText()
        pyperclip.copy(content)
        self.__show_info_dialog("Copied!")
        
    def __paste_tweet_area(self):
        """"Function pastes users clipboard content to Tweet text area"""
        content = pyperclip.paste()
        if content:
            self.__tweet_text.setPlainText(content)
            self.__show_info_dialog("Pasted!")
            
    def __clear_tweet_area(self):
        """"Function clears Tweet text area"""
        self.__tweet_text.setPlainText("")
        self.__show_info_dialog("Cleared!")
        
    def __cut_tweet_area(self):
        """"Function copies Tweet text area to clipboard, then clears Tweet text area"""
        content = self.__tweet_text.toPlainText()
        self.__tweet_text.setPlainText("")
        pyperclip.copy(content)
        self.__show_info_dialog("Cut!")

    def __gather_settings(self):
        """"Function gathers all settings from Intervals section, then returns it
        
        Returns:
        Settings | None: if operations succedes Settings class instance is returned, None otherwise"""
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
        except:
            self.__show_error_dialog("Provided settings are invalid!")
            return None

        return settings

    def __check_interval_tweet(self):
        """"Function checks whether current time matches interval settings, if so then posts Tweet"""
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
        """"Function checks whether current time matches scheduled time, if so then posts Tweet and stops timer"""
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
        """"Function starts timer that is connected to scheduled or interval function checking if Tweet should be sent or not"""
        self.__timer = QtCore.QTimer()

        if self.__settings.is_scheduled:
            self.__show_info_dialog(f"Success! You Tweet is scheduled for:\n   Date: {self.__settings.date_time.date().toString('dd.MM.yyyy')}\n   Time: {self.__settings.date_time.time().toString('hh:mm:ss')}")
            self.__timer.timeout.connect(self.__check_scheduled_tweet)
        elif self.__settings.is_interval:
            self.__show_info_dialog(f"Success! You Tweet is set for interval: {self.__settings.get_interval()}")
            self.__timer.timeout.connect(self.__check_interval_tweet)
        self.__timer.start(1000)

    def __stop_timer(self):
        """"Function stops timer if one is currently running"""
        if self.__timer:
            self.__show_info_dialog("Interval has been stopped!")
            self.__timer.stop()
        else:
            self.__show_error_dialog("Interval is not started!")

    def __convert_val(self, val):
        """"Function tries to convert passed value to int without throwing error, log error in case of exception
        
        Parameters:
            val (Any): value to be converted"""
        return int(val)

    def __show_error_dialog(self, text):
        """"Function opens QErrorMessage with passed text
        
        Parameters:
            text(str): text to be present in dialog box"""
        error_dialog = QErrorMessage()
        error_dialog.showMessage(text)
        error_dialog.exec_()

    def __show_info_dialog(self, text):
        """"Function opens QMessageBox with information severity and passed text
        
        Parameters:
            text(str): text to be present in dialog box"""
        dialog = QMessageBox.information(self, "Info!", text)

    def __convert_scripts(self):
        """"Function runs scripts and matches returned values with corresponding variables
        
        Returns:
            dict | None: dictionary with paired variables and script or None in case of failure"""
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
        """"Function loads values from exectued script
        
        Parameters:
            path(str): path to file where value was saved
            
        Returns:
            str: loded value"""
        filename = os.path.basename(path)[:-3]
        filename = f"{SCRIPT_PATH_PREFIX}/{filename}.txt"

        with open(filename, "r") as file:
            return file.read()

    def __build_var_script_pair(self, text_area, script):
        """"Function pairs variable name with variable value and returns as tuple
        
        Parameters:
            text_area(QLineEdit): widget that represent text area with variable name
            script(str): name of script to be executed
            
        Returns:
            tuple(str, str) | None: tuple of variable name and value or None in case of failure"""
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
        """"Function returns text of provided text_area
        
        Params:
            text_area(QLineEdit): widget from which text will be taken
        Returns:
            str | None: text value from widget or None in case of failure"""
        return text_area.text() if not None else None

    def __handle_tweet_vals_replacement(self, content, var_script_dict):
        """"Function replaces variables with their corresponding values in Tweet text
        
        Params:
            content(str): content of Tweet area to be processed
            var_script_Dict(dict(str, str)): dictionary with var name - value paris
        Returns:
            str | None: replaced tweet content or None in case of failure"""
        replaced_content, missing_vals = parse_tweet(content, var_script_dict)
        if missing_vals:
            self.__show_error_dialog(
                f"Atleast one of the script variables didn't match in tweet content: {missing_vals}"
            )
            return None

        return replaced_content

    def __handle_test_tweet_area(self):
        """"Function tries to convert Tweet text with variables for test output"""
        content = self.__gather__all_tweet_data()

        if content:
            self.__test_tweet_text.setPlainText(content)
            self.__show_info_dialog("Successfully parsed scripts!")


main_window = None


def set_main_window(window):
    global main_window
    main_window = window


def get_main_window():
    global main_window
    return main_window
