"""Module for geojson streaming logic

Makes use of the excelent ijson library to stream and parse into python objects a JSON
document starting at the `features` item. This assumes that a geojson is in the form

::

    {
        "type": "FeatureCollection",
        "features": [
            { ... },
            ...
        ],
        "properties
    }

"""
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import geojson
import ijson


class GeoJSONBatchStreamer:
    """Wrapper class around ijson iterable, allowing iteration in batches

    Attributes:
        geojson (Union[str, Path]): Filepath for a valid geojson document.
    """

    def __init__(self, geojson: Union[str, Path]) -> None:
        """
        Constructor for GeoJSONBatchStreamer
        
        Args:
            geojson (Union[str, Path]): Filepath for a valid geojson document. Will
                attempt to convert to a Path object regardless of input type.
        
        Raises:
            FileNotFoundError: If `geojson` does not exist.
        """
        self.geojson = Path(geojson)
        if not self.geojson.exists():
            raise FileNotFoundError(f"file {self.geojson.name} does not exist")

    def stream(
        self, batch: Optional[int] = None, prefix: Optional[str] = None
    ) -> Iterator[geojson.feature.FeatureCollection]:
        """
        Generator method to yield batches of geojson Features in a Feature Collection.
        
        Args:
            batch (Optional[int], optional): The number of features in a single batch. Defaults to 100.
            prefix (Optional[str], optional): The prefix of the element of interest in the
                geojson document. Usually this should be `'features.item'`. Only change this if
                you now what you are doing. See https://github.com/ICRAR/ijson for more info.
                Defaults to `'features.item'`.
        
        Yields:
            (Iterator[geojson.feature.FeatureCollection]): 
                The next batch of features wrapped in a new Feature Collection. This itself is
                just a subclass of a Dict instance, containing typical geojson attributes
                including a JSON array of Features. When `StopIteration` is raised, will yield
                whatever has been gathered so far in the `data` variable to ensure all
                features are collected.
        """
        if batch is None:
            batch = 100
        if prefix is None:
            prefix = "features.item"

        with self.geojson.open("r") as fp:
            features: Iterator[Dict[str, Any]] = ijson.items(fp, prefix)
            try:
                while True:
                    data: List[Dict[str, Any]] = []
                    for _ in range(batch):
                        data.append(next(features))
                    yield geojson.FeatureCollection(data)
            except StopIteration:
                if data:
                    yield geojson.FeatureCollection(data)  # yield remainder of data
                return
