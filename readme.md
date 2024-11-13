# Custom Raster Tile Engine

This project is a custom raster tile engine built with Python, Flask, GDAL, and Rasterio, designed to efficiently serve large raster datasets as map tiles. It enables high-performance access and visualization of geospatial data, making it suitable for applications requiring fast tile rendering for large raster files.

## Features

- **Raster Tiling**: Converts large GeoTIFFs or other raster files into map tiles for web-based applications.
- **Efficient Data Handling**: Uses GDAL and Rasterio to process and serve geospatial raster data quickly.
- **RESTful API**: Built on Flask, providing a simple and scalable API for requesting tiles based on location, zoom, and layer.
- **Customizable**: Supports customization of tile rendering parameters (zoom levels, file formats) and data sources.

## Requirements

- Python 3.7+
- Flask
- GDAL
- Rasterio

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/anup39/b3d-rastertile-server
   cd b3d-rastertile-server

   pip install -r requirements.txt

   python main.py

