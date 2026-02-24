# California Wildfire Analysis Project

A geospatial data analysis project for exploring and visualizing California fire perimeters and prescribed burns using GeoPandas, with interactive visualizations via ipywidgets.

## Project Overview

This project analyzes wildfire and prescribed burn perimeter data from California's fire database (2010-2024). It provides tools to:
- Load and explore fire perimeter geodata (GDB format)
- Visualize fire locations on interactive base maps
- Filter and analyze fires by year
- Compare prescribed burns vs. active wildfire perimeters

## Data

- **Source**: `data/raw/fire24_1.gdb` – ESRI Geodatabase containing:
  - `firep24_1`: California wildfire perimeters
  - `rxburn24_1`: Prescribed burn perimeters
- **Coordinate System**: EPSG 3310 (California Albers projection)

## Project Structure

```
ca-wildfire-project/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── data/
│   ├── raw/                          # Original fire perimeter GDB
│   │   └── fire24_1.gdb/
│   └── processed/                    # Processed/derived datasets
└── notebooks/
    └── 01_explore_fire_perimeters.ipynb  # Main analysis notebook
```

## Installation

### Prerequisites
- Python 3.11+ (recommended 3.14)
- pip or conda package manager

### Setup (Recommended: Conda)

Using conda-forge ensures proper installation of geospatial dependencies (especially GDAL/Fiona on Windows):

```bash
conda create -n ca-wildfire python=3.11 geopandas -c conda-forge
conda activate ca-wildfire
pip install -r requirements.txt
```

### Setup (Alternative: pip)

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Note**: On Windows, if pip fails to build geopandas/fiona, use the conda approach above.

## Dependencies

- **geopandas** – Geospatial vector data manipulation
- **pandas** – Data manipulation and analysis
- **shapely** – Geometric operations
- **pyogrio** – Vector I/O backend
- **matplotlib** – Visualization
- **contextily** – Basemap tiles for interactive maps
- **ipywidgets** – Interactive controls in Jupyter notebooks
- **jupyter** & **ipykernel** – Notebook environment
- **requests** – HTTP library for data fetching

See `requirements.txt` for pinned versions.

## Usage

### Launch Jupyter Notebook

```bash
jupyter notebook notebooks/01_explore_fire_perimeters.ipynb
```

### Notebook Walkthrough

The main notebook (`01_explore_fire_perimeters.ipynb`) contains:

1. **Import Libraries** – Load geospatial and visualization packages
2. **Load Data** – Read fire perimeter GDB layer into a GeoDataFrame
3. **Exploratory Analysis** – Inspect shape, CRS, and columns
4. **Static Visualization** – Plot fire perimeters on base map (2010–2024)
5. **Interactive Analysis** – Use ipywidgets slider to filter and plot fires by year

### Example: Load and Explore Fire Data

```python
import geopandas as gpd

# Load wildfire perimeters
gdf = gpd.read_file("data/raw/fire24_1.gdb", layer="firep24_1")
print(gdf.shape)          # (n_fires, n_columns)
print(gdf.crs)            # EPSG:3310
print(gdf.columns.tolist())

# Filter 2024 fires
gdf_2024 = gdf[gdf['YEAR_'] == 2024]
gdf_2024.plot()
```

### Example: Plot Recent Fires on Basemap

```python
import contextily as ctx
import matplotlib.pyplot as plt

# Filter and reproject to Web Mercator
gdf_recent = gdf[gdf['YEAR_'] >= 2010].to_crs(epsg=3857)

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
gdf_recent.plot(ax=ax, alpha=0.5, color="red")
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
plt.title("California Wildfires (2010-2024)")
plt.show()
```

## Key Columns in Fire Perimeter Data

| Column | Description |
|--------|-------------|
| `YEAR_` | Year of fire |
| `geometry` | Fire perimeter polygon (EPSG:3310) |
| (others) | Incident name, acreage, discovery date, etc. |

*Refer to the GDB metadata for complete column definitions.*

## Troubleshooting

### ImportError: No module named 'fiona'

**Issue**: Fiona (GDAL I/O backend) failed to install.

**Solution**: Use conda instead of pip:
```bash
conda create -n ca-wildfire python=3.11 geopandas -c conda-forge
```

Conda provides pre-compiled binaries for GDAL/Fiona, avoiding build failures on Windows.

### CRS or Layer Name Errors

- Verify GDB path: `data/raw/fire24_1.gdb`
- Check layer names: `firep24_1` (wildfires) or `rxburn24_1` (prescribed burns)
- Confirm EPSG 3310 is recognized: `gdf.crs` should show `EPSG:3310`

## Contributing

To extend this project:
1. Add new analysis notebooks in `notebooks/`
2. Store processed data in `data/processed/`
3. Update `requirements.txt` for new dependencies

## References

- [GeoPandas Documentation](https://geopandas.org/)
- [Contextily (Basemaps)](https://contextily.readthedocs.io/)
- [ipywidgets (Interactive Controls)](https://ipywidgets.readthedocs.io/)
- [EPSG:3310 (California Albers)](https://epsg.io/3310)

## License

Specify your project license here (e.g., MIT, CC0). California fire perimeter data source may have its own license—verify with original data provider.

## Contact

For questions or issues, open an issue or contact the project maintainer.

---

**Last Updated**: February 2026
