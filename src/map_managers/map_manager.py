import googlemaps
import os

from dotenv import load_dotenv
from bokeh.models import GMapOptions
from bokeh.plotting import gmap
from bokeh.io import save

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def plot(lat, lng, zoom=10, map_type='roadmap'):
    gmap_options = GMapOptions(lat=lat, lng=lng, map_type=map_type, zoom=zoom)
    save(gmap(api_key, gmap_options, title="Demo", width=500, height=400), "map.html")
    
plot(51.110760, 17.034015)