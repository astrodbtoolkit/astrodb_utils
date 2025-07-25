Documentation
=============

Build the Docs
--------------
The documentation is built using files in the `astrodb-template-db` submodule.
Be sure to update the submodule before building the docs.

.. code-block:: bash

    git submodule update --init --recursive


To build the docs, use `sphinx-autobuild <https://pypi.org/project/sphinx-autobuild/>`_.

.. code-block:: bash

    pip install -e ".[docs]"
    sphinx-autobuild docs docs/_build/html --ignore=docs/pages/template_schema/astrodb-template-db/.git/

The docs will then be available locally at <http://127.0.0.1:8000>.
