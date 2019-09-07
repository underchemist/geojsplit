from pathlib import Path

import geojson
import ijson


class GeoJSONStreamer:
    def __init__(self, geojson):
        self.geojson = Path(geojson)
        if not self.geojson.exists():
            raise FileNotFoundError(f"file {self.geojson.name} does not exist")

    def stream(self, batch=None, prefix=None, **kwargs):
        if prefix is None:
            prefix = "features.item"
        if batch is None:
            batch = 100
        with self.geojson.open("r") as fp:
            features = ijson.items(fp, prefix)
            try:
                while True:
                    data = []
                    for _ in range(batch):
                        data.append(next(features))
                    yield geojson.FeatureCollection(data)
            except StopIteration:
                if data:
                    yield geojson.FeatureCollection(data)  # yield remainder of data
                return

