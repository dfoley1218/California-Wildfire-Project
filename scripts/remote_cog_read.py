import rasterio
from rasterio.windows import Window
import logging
import numpy as np

def read_elevation_window(url: str, row_off: int, col_off: int,
    width: int, height: int) -> np.ndarray:
        with rasterio.Env(CPL_DEBUG="ON", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
            with rasterio.open(url) as src:
                win = Window(col_off, row_off, width, height)
                numarray = src.read(1, window=win)
        return numarray

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cogRead = read_elevation_window("https://data.danielfoley.dev/dixie_elevation_cog.tif", 0, 0, 512, 512)
    print(cogRead.shape, cogRead.dtype)