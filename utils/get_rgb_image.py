from typing import Optional, Tuple
from schemas.schema import RGBOptionSchema
from flask import send_file, Response, request
import logging



def _get_rgb_image(
    keys: str, tile_xyz: Optional[Tuple[int, int, int]] = None
) -> Response:
    from rastertiles.rgb import rgb

    some_keys = [key for key in keys.split("/") if key]
    rgb_values = ('red', 'green', 'blue')
    stretch_ranges = ([0.0, 255.0], [0.0, 255.0], [0.0, 255.0])
    tile_size = (512,512)


    image = rgb(
        some_keys,
        rgb_values,
        stretch_ranges=stretch_ranges,
        tile_xyz=tile_xyz,
        tile_size=tile_size
    )

    return send_file(image, mimetype="image/png")

