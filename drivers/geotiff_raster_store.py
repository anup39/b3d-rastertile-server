"""drivers/geotiff_raster_store.py

Base class for drivers operating on physical raster files.
"""
from typing import Optional, Any, Callable, Sequence, TypeVar, Tuple
from concurrent.futures import Future, Executor, ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures.process import BrokenProcessPool

import functools
import logging
import warnings
import threading

import numpy as np

from rastertiles import rastertile
from caches.cache import CompressedLFUCache
from baseclasses.baseclass import RasterStore

Number = TypeVar("Number", int, float)

logger = logging.getLogger(__name__)

_executor = None
USE_MULTIPROCESSING: bool = True
RASTER_CACHE_SIZE: int = 1024 * 1024 * 490  # 490 MB
DEFAULT_TILE_SIZE: Tuple[int, int] = (256, 256)
RESAMPLING_METHOD: str = "average"
REPROJECTION_METHOD: str = "linear"
RASTER_CACHE_COMPRESS_LEVEL: int = 9



def create_executor() -> Executor:

    if not USE_MULTIPROCESSING:
        return ThreadPoolExecutor(max_workers=1)

    executor: Executor

    try:
        # this fails on architectures without /dev/shm
        executor = ProcessPoolExecutor(max_workers=3)
    except OSError:
        # fall back to serial evaluation
        warnings.warn(
            "Multiprocessing is not available on this system. "
            "Falling back to serial execution."
        )
        executor = ThreadPoolExecutor(max_workers=1)

    return executor


def submit_to_executor(task: Callable[..., Any]) -> Future:
    global _executor

    if _executor is None:
        _executor = create_executor()

    try:
        future = _executor.submit(task)
    except BrokenProcessPool:
        # re-create executor and try again
        logger.warn("Re-creating broken process pool")
        _executor = create_executor()
        future = _executor.submit(task)

    return future


def ensure_hashable(val: Any) -> Any:
    if isinstance(val, list):
        return tuple(val)

    if isinstance(val, dict):
        return tuple((k, ensure_hashable(v)) for k, v in val.items())

    return val


class GeoTiffRasterStore(RasterStore):
    """Raster store that operates on GeoTiff raster files from disk.

    Path arguments are expected to be file paths.
    """

    _TARGET_CRS: str = "epsg:3857"
    _LARGE_RASTER_THRESHOLD: int = 10980 * 10980
    _RIO_ENV_OPTIONS = dict(
        GDAL_TIFF_INTERNAL_MASK=True, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"
    )

    def __init__(self) -> None:
        self._raster_cache = CompressedLFUCache(
            RASTER_CACHE_SIZE,
            compression_level=RASTER_CACHE_COMPRESS_LEVEL,
        )
        self._cache_lock = threading.RLock()

    # return type has to be Any until mypy supports conditional return types
    def get_raster_tile(
        self,
        path: str,
        tile_xyz: Optional[Tuple[int, int, int]] = None,
        tile_size: Optional[Sequence[int]] = None,
        preserve_values: bool = False,
        asynchronous: bool = False
    ) -> Any:
        future: Future[np.ma.MaskedArray]
        result: np.ma.MaskedArray



        if tile_size is None:
            tile_size = DEFAULT_TILE_SIZE

        kwargs = dict(
            path=path,
            tile_xyz=tile_xyz,
            tile_size=tuple(tile_size),
            preserve_values=preserve_values,
            reprojection_method=REPROJECTION_METHOD,
            resampling_method=RESAMPLING_METHOD,
            target_crs=self._TARGET_CRS,
            rio_env_options=self._RIO_ENV_OPTIONS,
        )

        cache_key = hash(ensure_hashable(kwargs))

        try:
            with self._cache_lock:
                result = self._raster_cache[cache_key]
        except KeyError:
            pass
        else:
            if asynchronous:
                # wrap result in a future
                future = Future()
                future.set_result(result)
                return future
            else:
                return result

        retrieve_tile = functools.partial(rastertile.get_raster_tile, **kwargs)

        future = submit_to_executor(retrieve_tile)

        def cache_callback(future: Future) -> None:
            # insert result into global cache if execution was successful
            if future.exception() is None:
                self._add_to_cache(cache_key, future.result())

        if asynchronous:
            future.add_done_callback(cache_callback)
            return future
        else:
            result = future.result()
            cache_callback(future)
            return result

    def _add_to_cache(self, key: Any, value: Any) -> None:
        try:
            with self._cache_lock:
                self._raster_cache[key] = value
        except ValueError:  # value too large
            pass
