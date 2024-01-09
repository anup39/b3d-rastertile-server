"""handlers/singleband.py

Handle /singleband API endpoint.
"""

from typing import Sequence, Mapping, Union, Tuple, Optional, TypeVar, cast
from typing.io import BinaryIO
import collections
from drivers.data_driver import get_driver
from settings.setting import get_settings
from utils.profile import trace
from  rastertiles import  image 
from rastertiles   import xyz



Number = TypeVar("Number", int, float)
NumberOrString = TypeVar("NumberOrString", int, float, str)
ListOfRanges = Sequence[
    Optional[Tuple[Optional[NumberOrString], Optional[NumberOrString]]]
]
RGBA = Tuple[Number, Number, Number, Number]


@trace("singleband_handler")
def singleband(
    keys: Union[Sequence[str], Mapping[str, str]],
    tile_xyz: Optional[Tuple[int, int, int]] = None,
    # *,
    # colormap: Union[str, Mapping[Number, RGBA], None] = None,
    # stretch_ranges: Optional[Tuple[NumberOrString, NumberOrString]] = None,
    tile_size: Optional[Tuple[int, int]] = None
) -> BinaryIO:
    """Return singleband image as PNG"""
    print(keys,"keys in singleband")
    cmap_or_palette: Union[str, Sequence[RGBA], None]  

    settings = get_settings()
    if tile_size is None:
        tile_size = settings.DEFAULT_TILE_SIZE

    driver = get_driver()

    tile_data = xyz.get_tile_data(
            driver, keys, tile_xyz, tile_size=tile_size 
        )

    cmap_or_palette = cast(Optional[str], [155,122,122,0])
    print(tile_data,'tile data')
    out = image.to_uint8(tile_data, *[0,255])

    return image.array_to_png(out, colormap=cmap_or_palette)