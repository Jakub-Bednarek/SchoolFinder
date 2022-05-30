import shapefile
import os

from shapely.geometry import shape

DATA_PATH = "res/data"

def read_data(file_name: str):
    path = f"{os.path.abspath('.')}/{DATA_PATH}/{file_name}"
    shape = shapefile.Reader(path)
    feature = shape.shapeRecords()[0]
    for feature in shape.shapeRecords():
        print(feature.shape.__geo_interface__)