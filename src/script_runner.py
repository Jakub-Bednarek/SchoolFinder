import subprocess
import os


def load_value_from_script(path):
    filename = os.path.basename(path)


def run_script(path):
    subprocess.run(["python3", path])
