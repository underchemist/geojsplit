import logging
from argparse import ArgumentTypeError
from pathlib import Path
import itertools

import geojson
import pytest
from geojsplit import cli


@pytest.fixture
def geojsplit_parser():
    return cli.setup_parser()


def random_geojson_feature_collection(n=5):
    features = [geojson.utils.generate_random("Polygon") for _ in range(n)]
    feature_collection = geojson.FeatureCollection(features)

    return feature_collection


@pytest.fixture
def random_geojson_file(tmp_path):
    def func(n=5):
        geojson_file = tmp_path / "random.geojson"
        with geojson_file.open("w") as f:
            geojson.dump(random_geojson_feature_collection(n=n), f)
        return geojson_file

    return func


def test_pad_filecount_too_large():
    # filecount > 26 ** 1 = 26
    file_count = 27
    width = 1
    assert cli.pad(file_count, width) == ""


@pytest.mark.parametrize(
    "file_count,expected",
    [(0, "aaaa"), (1, "aaab"), ((25 ** 4) - 1, "zzzz"), (25 ** 4, "")],
)
def test_pad_output(file_count, expected):
    assert cli.pad(file_count, width=4) == expected


def test_limit_type():
    with pytest.raises(ArgumentTypeError):
        cli.limit_type(-1)


def test_exit_on_invalid_limit(geojsplit_parser):
    with pytest.raises(SystemExit) as cm:
        geojsplit_parser.parse_args(["--limit", "-1"])

    assert cm.value.code == 2


def test_input_geojson_roundtrip(random_geojson_file):
    geojson_file = random_geojson_file(25)
    tmp_path = geojson_file.parent
    cli.main(args=[str(geojson_file)])
    data = []
    for path in tmp_path.glob("*_x*.geojson"):
        with path.open() as f:
            data.append(geojson.load(f))

    with geojson_file.open() as f:
        whole_file = geojson.load(f)

    assert whole_file == geojson.FeatureCollection(
        list(
            itertools.chain.from_iterable(
                feature_collection.features for feature_collection in data
            )
        )
    )


def test_input_geojson_output_dir(random_geojson_file):
    geojson_file = random_geojson_file()
    parent = geojson_file.parent
    output_dir = parent / "a/b/c/"
    expected_output = output_dir / "random_xaaaa.geojson"

    assert not expected_output.exists()
    cli.main(args=["--output", str(output_dir), str(geojson_file)])
    assert expected_output.exists()


def test_input_geojson_limit(random_geojson_file):
    geojson_file = random_geojson_file(10)
    parent = geojson_file.parent
    limit = 1
    cli.main(args=["--limit", str(limit), str(geojson_file)])
    outputs = list(parent.glob("*x*.geojson"))

    assert len(outputs) == limit


def test_input_geojson_geometry_count(random_geojson_file):
    geojson_file = random_geojson_file(n=25)
    parent = geojson_file.parent
    geometry_count = 2
    cli.main(args=["--geometry-count", str(geometry_count), str(geojson_file)])
    outputs = list(parent.glob("*x*.geojson"))

    assert len(outputs) == int(25 // 2 + 1)
