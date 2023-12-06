"""drivers/data_driver.py

The driver to interact with.
"""
import os
from typing import (
    Any,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    Dict
)
from baseclasses.baseclass import (RasterStore,)
from drivers.geotiff_raster_store import GeoTiffRasterStore
from settings.setting import get_settings
from pathlib import Path

URLOrPathType = Union[str, Path]

ExtendedKeysType = Union[Sequence[str], Mapping[str, str]]
ExtendedMultiValueKeysType = Union[Sequence[str], Mapping[str, Union[str, List[str]]]]
T = TypeVar("T")


class DataDriver:
    """Data driver object used to retrieve raster tiles and metadata.

    Do not instantiate directly, use :func:`get_driver` instead.
    """
    def __init__(self,  raster_store: RasterStore) -> None:
        self.raster_store = raster_store

        settings = get_settings()
        self.LAZY_LOADING_MAX_SHAPE: Tuple[int, int] = settings.get('LAZY_LOADING_MAX_SHAPE')



    def get_raster_tile(
        self,
        keys: ExtendedKeysType,
        tile_xyz: Optional[Tuple[int, int, int]] = None,
        tile_size: Sequence[int] = (256, 256),
        preserve_values: bool = False,
        asynchronous: bool = False,
    ) -> Any:
        """Load a raster tile with given keys and bounds.

        Arguments:

            keys: Key sequence identifying the dataset to load tile from.
            tile_bounds: Physical bounds of the tile to read, in Web Mercator projection (EPSG3857).
                Reads the whole dataset if not given.
            tile_size: Shape of the output array to return. Must be two-dimensional.
                Defaults to :attr:`Settings.DEFAULT_TILE_SIZE`.
            preserve_values: Whether to preserve exact numerical values (e.g. when reading
                categorical data). Sets all interpolation to nearest neighbor.
            asynchronous: If given, the tile will be read asynchronously in a separate thread.
                This function will return immediately with a :class:`~concurrent.futures.Future`
                that can be used to retrieve the result.

        Returns:

            Requested tile as :class:`~numpy.ma.MaskedArray` of shape ``tile_size`` if
            ``asynchronous=False``, otherwise a :class:`~concurrent.futures.Future` containing
            the result.

        """
        path_source =  os.getenv("OPTIMIZED_PATH")
        path = path_source+keys[0]+"_"+keys[1]+".tif"
        return self.raster_store.get_raster_tile(
            path=path,
            tile_xyz=tile_xyz,
            tile_size=tile_size,
            preserve_values=preserve_values,
            asynchronous=asynchronous,
        )


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(\n"
            f"    raster_store={self.raster_store!r}\n"
            ")"
        )
    

_DRIVER_CACHE: Dict[Tuple[int],DataDriver] = {}

def get_driver() -> DataDriver:
    """Retrieve Data driver instance for the given path.

    This function always returns the same instance for identical inputs.

    Warning:

       Always retrieve Driver instances through this function instead of
       instantiating them directly to prevent caching issues.

    """
    cache_key=os.getpid()
    if cache_key not in _DRIVER_CACHE:
        driver = DataDriver(
            raster_store=GeoTiffRasterStore()
        )
        _DRIVER_CACHE[cache_key] = driver


    return _DRIVER_CACHE[cache_key]
