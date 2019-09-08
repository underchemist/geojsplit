import argparse
import logging
import sys
from logging.config import dictConfig
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import geojson
import simplejson as json

from . import __version__
from .geojsplit import GeoJSONBatchStreamer


def input_geojson(args: argparse.Namespace) -> None:
    """Entrypoint function to iter through a valid geojson document and save to multiple files"""

    def gen_filename(
        filename: Path,
        file_count: int,
        width: Optional[int] = None,
        parent: Optional[Path] = None,
    ) -> Path:
        """Generate unique filename according to number of iterations thus far."""
        if width is None:
            width = 4
        if parent is None:
            parent = filename.parent
        elif isinstance(parent, str):
            parent = Path(parent)
        suffix: str = filename.suffix
        stem: str = filename.stem

        return parent / (stem + "_x" + pad(file_count, width) + suffix)

    logger: logging.Logger = logging.getLogger(__name__)
    logger.debug(f"starting splitting with geojson {args.geojson}")
    gj: GeoJSONBatchStreamer = GeoJSONBatchStreamer(args.geojson)

    count: int
    features: geojson.feature.FeatureCollection
    for count, features in enumerate(gj.stream(batch=args.geometry_count)):
        new_filename: Path = gen_filename(
            gj.geojson, count, width=args.suffix_length, parent=args.output
        )
        try:
            if not args.dry_run:
                if not new_filename.parent.exists():
                    logger.debug(f"creating output directory {args.output}")
                    new_filename.parent.mkdir(parents=True, exist_ok=True)
                with new_filename.open("w") as fp:
                    json.dump(features, fp)
            logger.debug(
                f"successfully saved {len(features['features'])} features to {new_filename}"
            )
        except IOError as e:
            logger.error(f"Could not write features to {new_filename}", exc_info=e)

        # account for 0 based index of enumerate that is required for `pad` method.
        if args.limit is not None:
            if count >= args.limit - 1:
                break


def pad(file_count: int, width: int) -> str:
    """
    Generate sortable alphabetic string to append to filenames.

    Arguments:
        file_count (int): The current file count.
        width (int): 
    """
    logger: logging.Logger = logging.getLogger(__name__)
    alphabet: str = "abcdefghijklmopqrstuvwxyz"

    if file_count >= len(alphabet) ** width:
        logger.error(
            f"Suffix of width of {width} is not enough to generate a unique filename. Increase "
        )
        sys.exit(1)

    char_array: List[str] = []
    digit: int
    for digit in range(width - 1, -1, -1):
        digit_cap: int = len(alphabet) ** digit
        idx: int = file_count // digit_cap
        file_count -= idx * digit_cap
        char_array.append(alphabet[idx])

    return "".join(char_array)


def setup_logger() -> None:
    dct: Dict[str, Any] = {
        "version": 1,
        "formatters": {
            "formatter": {
                "class": "logging.Formatter",
                "format": "%(name)s:%(levelname)s:%(message)s",
            }
        },
        "handlers": {
            "stream_handler": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "formatter",
            }
        },
        "root": {"level": "ERROR", "handlers": ["stream_handler"]},
    }

    dictConfig(dct)


def limit_type(x):
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError("LIMIT must be > 1")
    return x


def setup_parser() -> argparse.ArgumentParser:
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
        type=limit_type,
        help="limit number of split geojson file to at most LIMIT, with GEOMETRY_COUNT number of features.",
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
    parser.add_argument(
        "--version",
        help="show %(prog)s version number",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main() -> None:
    setup_logger()
    logger: logging.Logger = logging.getLogger(__name__)
    parser: argparse.ArgumentParser = setup_parser()
    args: argparse.Namespace = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"called {__name__} with arguments:")
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            logger.debug(f"{arg_name}: {arg_value}")

    input_geojson(args)
    logger.debug(f"finished splitting geojson")


if __name__ == "__main__":
    main()
