import pytest

from geojsplit import geojsplit

__version__ = "0.1.0"


def test_geojson_does_not_exist(tmp_path):
    d = tmp_path / "fake.geojson"
    with pytest.raises(FileNotFoundError):
        geojsplit.GeoJSONBatchStreamer(d)
