import shutil
import tempfile
import rasterio
from pathlib import Path
import pystac
from pystac import Item, Asset, MediaType
from datetime import datetime, timezone

cog_url = "https://data.danielfoley.dev/dixie_elevation_cog.tif"


def build_dixie_stac_item():
    with rasterio.open(cog_url) as src:
        print(src.bounds)
        item = pystac.Item(
            id = "dixie_elevation_cog",
            bbox = list(src.bounds),
            geometry = {
                "type": "Polygon",
                "coordinates": [[
                    [src.bounds.left, src.bounds.bottom],
                    [src.bounds.left, src.bounds.top],
                    [src.bounds.right, src.bounds.top],
                    [src.bounds.right, src.bounds.bottom],
                    [src.bounds.left, src.bounds.bottom]
                ]]
            },
            datetime = (
                datetime.strptime(src.tags()["TIFFTAG_DATETIME"], "%Y:%m:%d %H:%M:%S")
                if "TIFFTAG_DATETIME" in src.tags()
                else datetime.now(timezone.utc)
            ),
            properties = {}
            )
        item.add_asset(
            key="dixie_elevation_cog",
            asset=pystac.Asset(
                href=cog_url,
                media_type=pystac.MediaType.COG,
            ),
        )
        return item


if __name__ == "__main__":
    item =build_dixie_stac_item()
    print(item.validate())





