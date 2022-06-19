import sys

from app import App
from data_reader import read_data

sys.path.append("./helpers")

def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
