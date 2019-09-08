from pathlib import Path
from typing import Iterator, List, Union, Dict, Optional, Any

import geojson
import ijson


class GeoJSONBatchStreamer:
    """Wrapper class around ijson iterable, allowing iteration in batches
    """

    def __init__(self, geojson: Union[str, Path]) -> None:
        self.geojson = Path(geojson)
        if not self.geojson.exists():
            raise FileNotFoundError(f"file {self.geojson.name} does not exist")

    def stream(
        self, batch: Optional[int] = None, prefix: Optional[str] = None
    ) -> Iterator[geojson.feature.FeatureCollection]:
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

