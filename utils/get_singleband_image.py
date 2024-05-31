from typing import Optional, Tuple
from schemas.schema import RGBOptionSchema
from flask import send_file, Response, request
import logging



def _get_singleband_image(
    keys: str, band:str, colormap:str, tile_xyz: Optional[Tuple[int, int, int]] = None
) -> Response:
    from rastertiles.singleband import singleband

    some_keys = [key for key in keys.split("/") if key]
    band = [key for key in band.split("/") if key]
    colormap = [key for key in colormap.split("/") if key]
    # print(some_keys, band, colormap)
    rgb_values = ('red', 'green', 'blue')
    stretch_ranges = ([0.0, 255.0], [0.0, 255.0], [0.0, 255.0])
    tile_size = (512,512)
    some_keys = (some_keys[0],band[0])
    print(some_keys,'some keys')


    image = singleband(
        keys=some_keys,
        # rgb_values=rgb_values,
        # stretch_ranges=stretch_ranges,
        tile_xyz=tile_xyz,
        tile_size=tile_size
    )

    return send_file(image, mimetype="image/png")

