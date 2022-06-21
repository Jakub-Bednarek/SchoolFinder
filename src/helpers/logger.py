import logging
import time
import sys
import os
import pathlib
from typing import List

DEFAULT_LOG_FILE = "logs/app.log"
DEFAULT_LOG_COLOR = "INFO"
DEFAULT_LOG_LEVEL = logging.DEBUG


class Logger:
    LOG_COLORS = {
        "INFO": "\033[0m",
        "DEBUG": "\033[33m",
        "WARN": "\033[35m",
        "ERROR": "\033[31m",
        "RESET": "\033[0m",
    }
    FORMAT = "%(message)s"

    class DefaultFormatter(logging.Formatter):
        def __init__(self, *args, **kwargs):
            logging.Formatter.__init__(self, *args, **kwargs)
            self.__start_time = time.time()

        def format(self, record):
            colorized_msg = self.colorize(record.msg, record.levelname)

            return (
                f"T={self.formatTime(self, record)} -{record.module}-: {colorized_msg}"
            )

        def formatTime(self, record, datefmt=None):
            return round(time.time() - self.__start_time, 4)

        def colorize(self, msg: str, severity: str):
            color = Logger.LOG_COLORS.get(severity, DEFAULT_LOG_COLOR)

            return f"{color}{msg}{Logger.LOG_COLORS['RESET']}"

    def log_msg(self, msg: str, severity: int):
        """Function logs message with corresponding severity
        
        Parameters:
            msg(str): message to be logged
            severity(str): level that will be set to log message"""
        self.__root_logger.log(severity, msg)

    def __init__(self, file_path: str = DEFAULT_LOG_FILE):
        try:
            self.__start(file_path)
            self.log_msg(f"Created logger writing to file {file_path}", logging.INFO)
        except:
            self.log_msg(
                f"Failed to create logger writing to file {file_path}", logging.INFO
            )

    def create_paths(self, dest_path: str):
        """Function creates path in file system based on given string
        
        Parameters:
            dest_path(str): path to folder that will be created"""
        path = self.create_log_path_str(dest_path)
        if os.path.exists(path):
            return
        else:
            os.makedirs(path)

    def create_log_path_str(self, dest_path: str):
        """Function creates log path string from provided destination path
        
        Parameters:
            dest_path(str): path to be converted
        Returns:
            str: converted path"""
        tokens = dest_path.split("/")

        if len(tokens) <= 1:
            return dest_path

        path = str(pathlib.Path().absolute())
        for token in tokens[0 : len(tokens) - 1]:
            path += "/" + token

        return path

    def __start(self, file_path: str):
        """Function sets up logger and all it's variables
        
        Parameters:
            file_path(str): path where logs will be saved"""
        self.create_paths(file_path)

        file_handle = logging.FileHandler(
            filename=file_path, mode="w", encoding="utf-8"
        )
        file_handle.setFormatter(self.DefaultFormatter(self.FORMAT))

        console_handle = logging.StreamHandler(stream=sys.stdout)
        console_handle.setFormatter(self.DefaultFormatter(self.FORMAT))

        self.__root_logger = logging.RootLogger(DEFAULT_LOG_LEVEL)
        self.__root_logger.addHandler(file_handle)
        self.__root_logger.addHandler(console_handle)


logger = Logger()


def log_inf(msg):
    """Function logs message with severity: INFO"""
    logger.log_msg(msg, logging.INFO)


def log_dbg(msg):
    """Function logs message with severity: DEBUG"""
    logger.log_msg(msg, logging.DEBUG)


def log_wrn(msg):
    """Function logs message with severity: WARNING"""
    logger.log_msg(msg, logging.WARN)


def log_err(msg):
    """Function logs message with severity: ERROR"""
    logger.log_msg(msg, logging.ERROR)
