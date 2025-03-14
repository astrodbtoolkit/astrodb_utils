Developer Documentation
================================

Installation
---------------------

If you'd like to run tests, make sure to install the package with the optional test dependencies. E.g.,

.. code-block:: bash

    pip install -e ".[test]"

Then, in the `astrodb_utils/tests/` directory, run

.. code-block:: bash

    git clone git@github.com:astrodbtoolkit/astrodb-template-db.git

This step installs a template database repository. Tests can then be run in the top-level directory, with the command

Running Tests
---------------------

All contributions should include tests. To run the tests, use the command

.. code-block:: bash

    pytest

Linting
---------------------

Use Ruff and Black

Build the Docs
---------------------

We use sphinx.
To build the docs, use `sphinx-autobuild <https://pypi.org/project/sphinx-autobuild/>`_.
Also need to install `pandoc <https://pandoc.org/installing.html>'_.

.. code-block:: bash

    pip install sphinx-autobuild sphinx_pyproject nbsphinx pydata-sphinx-theme
    sphinx-autobuild docs docs/_build/html

The docs will be available at <http://127.0.0.1:8000> and watch docs/ for changes.
