Developer Documentation
=======================

.. toctree::
    :glob:
    :maxdepth: 2
    :titlesonly:

    documentation
    ingest_functions


Installation
------------

If you'd like to run tests, make sure to install the package with the optional
test dependencies. E.g.,

.. code-block:: bash

    pip install -e ".[test]"

Make sure you get the `astrodb-template-db`` submodule. This is required for
running tests and building the documentation.

.. code-block:: bash

    git submodule update --init --recursive


Running Tests
-------------

All contributions should include tests. To run the tests, use the command

.. code-block:: bash

    pytest

Linting and Formatting
----------------------

Use `ruff <https://docs.astral.sh/ruff/>`_ for linting and formatting.
A pre-commit hook is provided for automatic linting and formatting with ruff.
To use it, run `pip install pre-commit` and then `pre-commit install --allow-missing-config`.

VSCode setup instructions: `Formatting Python in VSCode <https://code.visualstudio.com/docs/python/formatting>`_

