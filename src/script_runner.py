import subprocess
import os

from PyQt5.QtWidgets import QErrorMessage

def load_value_from_script(path):
    """Function loads file name from provided path"""
    filename = os.path.basename(path)

def run_script_python3(path):
    """Function runs script using python3 string as execution variable"""
    try:
        subprocess.run(["python3", path])
    except:
        return False
    
    return True
        

def run_script_python(path):
    """Function runs script using python string as execution variable"""
    try:
        subprocess.run(['python', path])
    except:
        return False
    
    return True
    
def run_script(path):
    """Function tries to run script with python3, then python in case of failure, shows error if none of the methods worked"""
    if not run_script_python3(path):
        if not run_script_python(path):
            error_dialog = QErrorMessage()
            error_dialog.showMessage("Provided script contains errors or Python enviroment is not installed! Can't run script.")
            error_dialog.exec_()
