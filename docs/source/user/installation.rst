.. _installation:

Installation of Geojsplit
=========================

**Geojsplit** is pure python, with no C dependencies. It does rely on a few useful third party packages

- ijson_ - Used for streaming JSON documents
- geojson_ - Used for serializing valid GeoJSON documents
- simplejson_ - Used for serializing ``decimal.Decimal`` objects as a result of ijson parsing.

With poetry
-----------
For an `introduction to poetry <https://dev.to/yukinagae/beginner-guide-on-poetry-new-python-dependency-management-tool-4327/>`_. ::

    $ poetry add geojsplit

will add geojsplit to your current virtual environment and update your poetry.lock file. If you would like to contribute or develop geojsplit::

    $ git clone https://github.com/underchemist/geojsplit.git
    $ cd geojsplit
    $ poetry install

.. note:: You may need some extra configuration to make poetry play nice with conda virtual environments.::

    $ poetry config settings.virtualenvs.path $CONDA_ENV_PATH
    $ poetry config settings.virtualenvs.create 0

    See https://github.com/sdispater/poetry/issues/105#issuecomment-498042062 for more info.

With pip
--------

Though **geojsplit** is developed using poetry_ (and as such
does not have a setup.py), pep517_
implementation in pip means we can install it directly.::

    $ pip install geojsplit

.. note:: Because there is no setup.py ``pip install -e .`` will not work. You can get similar behavior with ``poetry install``.

.. links
.. _ijson: https://github.com/ICRAR/ijson
.. _geojson: https://github.com/jazzband/geojson
.. _simplejson: https://github.com/simplejson/simplejson
.. _poetry: https://poetry.eustace.io/
.. _pep517: https://www.python.org/dev/peps/pep-0517/
