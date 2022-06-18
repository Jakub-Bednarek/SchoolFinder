import pathlib

from PyQt5 import QtWidgets, QtWebEngineWidgets
from map_managers.map_manager import generate_map_html
from helpers.logger import log_inf, log_wrn
from PyQt5.QtGui import QWheelEvent

DEFAULT_LAT = 51.110760
DEFAULT_LNG = 17.034015
SCROOL_MOVE_DIVIDER = 1440


class MapExplorer(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent=None):
        super(MapExplorer, self).__init__(parent)
        self.__zoom = 10

    def start(self):
        self.__setup_layout()
        self.__load_plot_to_web_engine()

    def change_zoom(self, multiplier: float):
        if multiplier < 0 or multiplier > 100:
            log_wrn(f"Zoom out of bounds (0, 100): {multiplier}")
            return

        self.__zoom *= multiplier
        log_inf(f"New zoom value: {self.__zoom}")

    def __load_plot_to_web_engine(self):
        bokeh_map_path = generate_map_html(
            DEFAULT_LAT, DEFAULT_LNG, zoom=int(self.__zoom)
        )
        html_content = self.__read_map_html(bokeh_map_path)

        self.setHtml(html_content)

    def __setup_layout(self):
        self.__layout = QtWidgets.QVBoxLayout(self)
        self.resize(700, 400)

    def __read_map_html(self, bokeh_map_path: str) -> str:
        with open(bokeh_map_path, "r", encoding="utf-8") as html_file:
            return "".join(html_file.readlines())

    # Events
    def wheelEvent(self, event: QWheelEvent):
        self.__zoom += self.__zoom * (event.angleDelta().y() / SCROOL_MOVE_DIVIDER)
        self.__load_plot_to_web_engine()
