import pathlib
import os

PATH_PREFIX = "script_outputs/"


def perform_script():
    # YOUR CODE GOES HERE
    return "my_string"


def create_dir_if_not_existing():
    p = pathlib.Path(PATH_PREFIX)
    if not p.exists():
        os.mkdir(f"./{PATH_PREFIX}")


def save_to_file():
    values = perform_script()
    filename = os.path.basename(__file__)[:-3]
    print(filename)
    create_dir_if_not_existing()

    with open(f"{PATH_PREFIX}{filename}.txt", "w") as file:
        file.write(values)
        file.flush()


try:
    save_to_file()
except Exception as e:
    print(e)
