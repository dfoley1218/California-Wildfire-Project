import shutil
import tempfile
from pathlib import Path
import pystac
from pystac import Item, Asset, MediaType
from datetime import datetime

cog_url = "https://data.danielfoley.dev/dixie_elevation_cog.tif"

def build_dixie_stac_item():
    Item = pystac.Item(
        id = "dixie_elevation_cog",
        geometry = 
        )