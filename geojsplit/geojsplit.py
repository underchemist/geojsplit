from pathlib import Path

import geojson


class GeoJSONStreamer:
    def __init__(self, geojson):
        self.geojson = Path(geojson)
        if not self.geojson.exists():
            raise FileNotFoundError(f"file {self.geojson.name} does not exist")
        self.start_line = None

    def _find_feature_start_line(self, max_lines=None):
        if max_lines is None:
            max_lines = 100

        with self.geojson.open("r") as fp:
            for idx, line in enumerate(fp):
                if idx == max_lines:
                    break
                if '  "features":\n' == line:
                    if next(fp) == "  [\n":
                        return idx + 2
            raise EOFError(f"features object not found in {self.geojson.name}")

    def _seek(self, fp, **kwargs):
        if self.start_line is None:
            self.start_line = self._find_feature_start_line(
                max_lines=kwargs["max_lines"]
            )

        for _ in range(self.start_line):
            next(fp)

    def stream(self, batch=None, **kwargs):
        if batch is None:
            batch = 100
        with self.geojson.open("r") as fp:
            self._seek(fp, **kwargs)
            while True:
                data = []
                for _ in range(batch):
                    line = fp.readline()
                    if line == "  ]\n":
                        if data:
                            yield geojson.FeatureCollection(data)
                        return
                    data.append(geojson.loads(line.strip(" \n,")))
                yield geojson.FeatureCollection(data)
