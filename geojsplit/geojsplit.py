import argparse
import json
import logging
import sys
from logging.config import fileConfig
from pathlib import Path
from typing import List

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


def input_geojson(args):
    def gen_filename(filename: Path, file_count, width=None, parent=None):
        if width is None:
            width = 4
        if parent is None:
            parent = filename.parent
        elif isinstance(parent, str):
            parent = Path(parent)
        suffix = filename.suffix
        stem = filename.stem

        return parent / (stem + "_x" + pad(file_count, width) + suffix)

    logger = logging.getLogger(__file__)
    logger.debug(f"Starting splitting with geojson {args.geojson}")
    gj = GeoJSONStreamer(args.geojson)
    if args.limit > 0:
        for count, features in enumerate(
            gj.stream(
                batch=args.geometry_count,
                **{k: v for k, v in vars(args).items() if k != "geojson"},
            )
        ):
            new_filename = gen_filename(
                gj.geojson, count, width=args.suffix_length, parent=args.output
            )
            try:
                if not args.dry_run:
                    if not new_filename.parent.exists():
                        logger.debug(f"creating output directory {args.output}")
                        new_filename.parent.mkdir(parents=True, exist_ok=True)
                    with new_filename.open("w") as fp:
                        geojson.dump(features, fp)
                logger.debug(
                    f"successfully saved {len(features['features'])} features to {new_filename}"
                )
            except IOError as e:
                logger.error(f"Could not write features to {new_filename}", exc_info=e)

            if count >= args.limit - 1:
                break


def pad(file_count: int, width: int) -> str:
    """
    Generate sortable alphabetic string to append to filenames.

    Arguments:
        file_count (int): The current file count.
        width (int): 
    """
    logger: logging.Logger = logging.getLogger(__file__)
    alphabet: str = "abcdefghijklmopqrstuvwxyz"

    if file_count >= len(alphabet) ** width:
        logger.error(
            f"Suffix of width of {width} is not enough to generate a unique filename. Increase "
        )
        sys.exit(1)

    char_array: List[str] = []
    for digit in range(width - 1, -1, -1):
        digit_cap: int = len(alphabet) ** digit
        idx: int = file_count // digit_cap
        file_count -= idx * digit_cap
        char_array.append(alphabet[idx])

    return "".join(char_array)


def setup_logger():
    fileConfig("logging.conf")


def setup_parser():
    parser = argparse.ArgumentParser(
        prog="geojsplit", description="Split a geojson file into many geojson files."
    )
    parser.add_argument("geojson", help="filename of geojson file to split")
    parser.add_argument(
        "-l",
        "--geometry-count",
        type=int,
        help="the number of features to be distributed to each file.",
    )
    parser.add_argument(
        "-m",
        "--max-lines",
        type=int,
        help="the number of lines to search through looking for a geojson features object",
    )
    parser.add_argument(
        "-a",
        "--suffix-length",
        type=int,
        help="number of characters in the suffix length for split geojsons",
    )
    parser.add_argument(
        "-o", "--output", help="output directory to save split geojsons"
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        help="limit number of split geojson files to at most n",
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        help="see output without actually writing to file",
        action="store_true",
    )

    return parser


def main():
    setup_logger()
    logger = logging.getLogger(__file__)
    parser = setup_parser()
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"called {__file__} with arguments:")
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            logger.debug(f"{arg_name}: {arg_value}")

    input_geojson(args)
    logger.debug(f"finished splitting geojson")


if __name__ == "__main__":
    main()
