"""xyz.py

Utilities to work with XYZ Mercator tiles.
"""

from typing import Optional, Sequence, Union, Mapping, Tuple, Any
import mercantile
from exceptions import exception
from drivers.data_driver import DataDriver

# TODO: add accurate signature if mypy ever supports conditional return types
def get_tile_data(
    driver: DataDriver,
    keys: Union[Sequence[str], Mapping[str, str]],
    tile_xyz: Optional[Tuple[int, int, int]] = None,
    tile_size: Tuple[int, int] = (256, 256),
    preserve_values: bool = False,
    asynchronous: bool = False,
) -> Any:
    """Retrieve raster image from key_names for given XYZ tile and keys"""

    print(keys, 'keys')
    if tile_xyz is None:
        # read whole dataset
        return driver.get_raster_tile(
            keys,
            tile_xyz=tile_xyz,
            tile_size=tile_size,
            preserve_values=preserve_values,
            asynchronous=asynchronous,
        )

    return driver.get_raster_tile(
        keys,
        tile_xyz=tile_xyz,
        tile_size=tile_size,
        preserve_values=preserve_values,
        asynchronous=asynchronous,
    )


def tile_exists(bounds: Sequence[float], tile_x: int, tile_y: int, tile_z: int) -> bool:
    """Check if an XYZ tile is inside the given physical bounds."""
    mintile = mercantile.tile(bounds[0], bounds[3], tile_z)
    maxtile = mercantile.tile(bounds[2], bounds[1], tile_z)

    return mintile.x <= tile_x <= maxtile.x and mintile.y <= tile_y <= maxtile.y
