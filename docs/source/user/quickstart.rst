Quickstart
==========

Install 
-------

:ref:`Installation instructions <installation>`

Usage
-----

Although both the library code and the command line tool of geojsplit are relatively
simple, there are use cases for both. You may want to use the backend
``GeoJSONBatchStreamer`` class directly in order to do more sophisticated manipulations
with GeoJOSN documents. As a command line tool geojsplit also works well as a
preprocessing step for working with large GeoJSON documents i.e. for piping into GDAL's
ogr2ogr tool. 

As a library
^^^^^^^^^^^^

Once installed, geojsplit can be imported in like ::

    from geojsplit import geojsplit

    geojson = geojsplit.GeoJSONBatchStreamer("/path/to/some.geojson")
    
    for feature_collection in geojson.stream():
        do_something(feature_collection)
        ...

If the ``/path/to/some.geojson`` does not exists, ``FileNotFound`` will be raised.

You can control how many features are streamed into a Feature Collection using the
``batch`` parameter (Default is 100). ::

    >>> g = geojson.stream(batch=2)  # instatiate generator object
    >>> data = next(g)
    >>> print(data)
    {"features": [{"geometry": {"coordinates": [[[-118.254638, 33.7843], [-118.254637,
    33.784231], [-118.254556, 33.784232], [-118.254559, 33.784339], [-118.254669,
    33.784338], [-118.254668, 33.7843], [-118.254638, 33.7843]]], "type": "Polygon"},
    "properties": {}, "type": "Feature"}, {"geometry": {"coordinates": [[[-118.254414,
    33.784255], [-118.254232, 33.784255], [-118.254232, 33.784355], [-118.254414,
    33.784355], [-118.254414, 33.784255]]], "type": "Polygon"}, "properties": {}, "type":
    "Feature"}], "type": "FeatureCollection"}
    >>> print(len(data["features"]))
    2

If your GeoJSON document has a different format or you want to iterate over different
elements on your document, you can also pass a different value to the ``prefix`` keyword
argument (Default is ``'features.item'``). This is an argument passed directly down to a ``ijson.items`` call, for more
information see https://github.com/ICRAR/ijson.

As a command line tool
^^^^^^^^^^^^^^^^^^^^^^

After installing you should have the geojsplit executable in your ``PATH``. ::

    $ geojsplit -h
    usage: geojsplit [-h] [-l GEOMETRY_COUNT] [-a SUFFIX_LENGTH] [-o OUTPUT]
                    [-n LIMIT] [-v] [-d] [--version]
                    geojson

    Split a geojson file into many geojson files.

    positional arguments:
    geojson               filename of geojson file to split

    optional arguments:
    -h, --help            show this help message and exit
    -l GEOMETRY_COUNT, --geometry-count GEOMETRY_COUNT
                            the number of features to be distributed to each file.
    -a SUFFIX_LENGTH, --suffix-length SUFFIX_LENGTH
                            number of characters in the suffix length for split
                            geojsons
    -o OUTPUT, --output OUTPUT
                            output directory to save split geojsons
    -n LIMIT, --limit LIMIT
                            limit number of split geojson file to at most LIMIT,
                            with GEOMETRY_COUNT number of features.
    -v, --verbose         increase output verbosity
    -d, --dry-run         see output without actually writing to file
    --version             show geojsplit version number

By default splitted GeoJSON files are saved as ``filename_x<SUFFIX_LENGTH characters
long>.geojson``. Default SUFFIX_LENGTH is 4, meaning that 456976 unique files can be
generated. If you need more use ``-a`` or ``--suffix-length`` to increase this value
appropriately.

The ``--geometry-count`` flag corresponds to the ``batch`` keyword argument for
``GeoJSONBatchStreamer.stream`` method. Note that if GEOMETRY_COUNT does not divide
equally into the number of features in the Feature Collection, the last batch of features
will be < GEOMETRY_COUNT.

Finally, to only iterate over the the first n elements of a GeoJSON document, use ``--limit``.