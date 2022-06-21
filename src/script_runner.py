import subprocess
import os

from PyQt5.QtWidgets import QErrorMessage

def load_value_from_script(path):
    filename = os.path.basename(path)

def run_script_python3(path):
    try:
        subprocess.run(["python3", path])
    except:
        return False
    
    return True
        

def run_script_python(path):
    try:
        subprocess.run(['python3', path])
    except:
        return False
    
    return True
    
def run_script(path):
    if not run_script_python3(path):
        if not run_script_python(path):
            error_dialog = QErrorMessage()
            error_dialog.showMessage("Provided script contains errors or Python enviroment is not installed! Can't run script.")
            error_dialog.exec_()
