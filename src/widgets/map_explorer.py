import pathlib

from PyQt5 import QtWidgets, QtWebEngineWidgets
from map_managers.map_manager import generate_map_html

DEFAULT_LAT = 51.110760
DEFAULT_LNG = 17.034015


class MapExplorer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MapExplorer, self).__init__(parent)
        
    def start(self):
        self.__create_web_engine()
        self.__setup_layout()
        self.__start_plot_on_web_engine()
        
    def __create_web_engine(self):
        self.__web_engine = QtWebEngineWidgets.QWebEngineView()   
        
    def __start_plot_on_web_engine(self):
        bokeh_map_path = generate_map_html(DEFAULT_LAT, DEFAULT_LNG)
        html_content = self.__read_map_html(bokeh_map_path)
        
        self.__web_engine.setHtml(html_content)
        
    def __setup_layout(self):
        self.__layout = QtWidgets.QVBoxLayout(self)
        self.__layout.addWidget(self.__web_engine)
        self.resize(500, 400)

    
    def __read_map_html(self, bokeh_map_path: str) -> str:
        with open(bokeh_map_path, "r", encoding="utf-8") as html_file:
            return "".join(html_file.readlines())