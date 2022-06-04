import configparser

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QGroupBox, QWidget, QLineEdit

from helpers.logger import log_inf, log_err

from widgets.map_explorer import MapExplorer
from widgets.splash_screen import add_finished

DEFAULT_WINDOW_CONFIG_FILE = "conf/window.ini"

class MainWindow(QMainWindow):
    def __init__(self):
        log_inf("Initializing MainWindow")
        
        super(MainWindow, self).__init__()
        self.initUI()
        add_finished()
        
        log_inf("Successfully MainWindow")
        
    def __del__(self):
        self.__save_config(DEFAULT_WINDOW_CONFIG_FILE)
        
        log_inf("Destroyed window")
        
    # config stuff
    def __load_config(self, file_name: str):
        pass
        
    def __save_config(self, file_name: str):
        config = configparser.ConfigParser()
        
        config['Default'] = {}
        config['Default']['style'] = 'default'
        config['Default']['window_name'] = "School finder"
        config['Dimensions'] = {}
        config['Dimensions']['window_width'] = '200'
        config['Dimensions']['window_height'] = '200'
        config['Dimensions']['window_x_pos'] = '100'
        config['Dimensions']['window_y_pos'] = '100'
        config['Dimensions']['fullscreen'] = 'False'
        
        try:
            with open(file_name, 'w') as configfile:
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
        self.__create_map_area()
        self.__create_parameters_panel()
        self.__create_central_widget()
        
        self.setCentralWidget(self.__central_widget)
        
    def __create_central_widget(self):
        self.__central_widget = QWidget()
        
        central_widget_layout = QGridLayout()
        central_widget_layout.addWidget(self.__map_groupbox, 0, 0)
        central_widget_layout.addWidget(self.__parameters_panel, 0, 1)
        
        self.__central_widget.setLayout(central_widget_layout)
    
    def __create_map_area(self):
        map_area_layout = QGridLayout()
        
        self.__map_explorer = MapExplorer()
        map_area_layout.addWidget(self.__map_explorer)
        self.__map_explorer.start()
        
        self.__map_groupbox = QGroupBox()
        self.__map_groupbox.setLayout(map_area_layout)
        
    
    def __create_parameters_panel(self):
        self.__parameters_panel = QWidget()
        
        width_min_area = QLineEdit("0")
        width_max_area = QLineEdit("100")
        height_min_area = QLineEdit("0")
        height_max_area = QLineEdit("20")
        depth_min_area = QLineEdit("0")
        depth_max_area = QLineEdit("100")
        
        parameters_panel_layout = QGridLayout()
        parameters_panel_layout.addWidget(width_min_area, 0, 0)
        parameters_panel_layout.addWidget(width_max_area, 0, 1)
        parameters_panel_layout.addWidget(height_min_area, 1, 0)
        parameters_panel_layout.addWidget(height_max_area, 1, 1)
        parameters_panel_layout.addWidget(depth_min_area, 2, 0)
        parameters_panel_layout.addWidget(depth_max_area, 2, 1)
        
        self.__parameters_panel.setLayout(parameters_panel_layout)
        