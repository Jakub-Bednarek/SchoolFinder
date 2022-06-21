import pathlib
import os
from datetime import datetime

PATH_PREFIX = "script_outputs/"

# This is function that returns value passed to our program, write your code inside and don't forget about return
def perform_script():
    # YOUR CODE GOES HERE
    time = datetime.now()
    return str(time)


# Don't touch this part of code as it may break functionality
def create_dir_if_not_existing():
    p = pathlib.Path(PATH_PREFIX)
    if not p.exists():
        os.mkdir(f"./{PATH_PREFIX}")


def save_to_file():
    values = perform_script()
    filename = os.path.basename(__file__)[:-3]
    create_dir_if_not_existing()

    with open(f"{PATH_PREFIX}{filename}.txt", "w") as file:
        file.write(values)
        file.flush()


try:
    save_to_file()
except Exception as e:
    print(e)
