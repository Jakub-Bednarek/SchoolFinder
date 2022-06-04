import os

from dotenv import load_dotenv
from bokeh.models import GMapOptions
from bokeh.plotting import gmap
from bokeh.io import save

from helpers.logger import log_inf

BOKEH_MAP_PATH = "res/html_maps/map.html"

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def generate_map_html(lat, lng, zoom=13, map_type='roadmap'):
    log_inf("Generating bokeh map plot.")
    
    gmap_options = GMapOptions(lat=lat, lng=lng, map_type=map_type, zoom=zoom)
    html_file_path = save(gmap(api_key, gmap_options, title="Demo", width=600, height=500), filename=BOKEH_MAP_PATH)
    
    log_inf(f"Done, generated file path: {BOKEH_MAP_PATH}")
    
    return html_file_path