import fiona

from enum import Enum, auto
#from helpers.logger import log_inf, log_wrn

DEFAULT_BIKE_SHP = 'res/data/TrasyRowerowe.shp'

class GeoType(Enum):
    HUMAN_BIKE = auto()
    BIKE = auto()
    BIKE_PATH = auto()
    BIKE_BUS = auto()
    CONTRAPAS = auto()
    CONTRAMOVE = auto()
    SHAFTS = auto()
    PARK_ROAD = auto()
    CALM_ROAD = auto()
    PASS_PART = auto()
    CONNECTOR = auto()
    
geotype_to_name = {
    "droga dla pieszych i rowerów": GeoType.HUMAN_BIKE,
    "droga dla rowerów": GeoType.BIKE,
    "pas ruchu dla rowerów": GeoType.BIKE_PATH,
    "pas BUS + ROWER": GeoType.BIKE_BUS,
    "kontrapas": GeoType.CONTRAPAS,
    "kontraruch": GeoType.CONTRAMOVE,
    "trasa na wałach": GeoType.SHAFTS,
    "trasa przez park": GeoType.PARK_ROAD,
    "strefa ruchu uspokojonego 20 i 30 km/h" :GeoType.CALM_ROAD,
    "możliwość przejazdu" :GeoType.PASS_PART,
    "łącznik drogowy": GeoType.CONNECTOR
}

class GeoRecord:
    def __init__(self, type: GeoType, coordinates):
        self.__type = type
        self.__coordinates = coordinates
        self.__uses = 0
        
    def get_coordinates(self):
        return self.__coordinates


class GeodataStorage:
    def __init__(self):
        self.__shapes = {}
        
    def load(self, filename: str):
        #log_inf(f"Loading geodata file: {filename}")
        shape = fiona.open(filename)
        
        for s in shape:
            try:
                type = geotype_to_name[s['properties']['TYP']]
                print(s)
                if type not in self.__shapes:
                    self.__shapes[type] = [self.__create_geo_record(s, type)]
                else:
                    self.__shapes[type].append(self.__create_geo_record(s, type))
            except Exception as e:
                pass
        #log_inf("Successfully loaded file.")
        
    def print(self):
        print(self.__shapes)
        for key, val in self.__shapes.items():
            for shape in val:
                print(shape.get_coordinates())
            
    def __create_geo_record(self, record, type):
        return GeoRecord(type, record['geometry']['coordinates'])
    
storage = GeodataStorage()
storage.load(DEFAULT_BIKE_SHP)
storage.print()