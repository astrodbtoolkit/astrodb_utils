Documentation
=============

Build the Docs
--------------
The documentation is built using files in the `astrodb-template-db` repo.
If it's not already located in your working directory, it will be cloned into it.

To build the docs, use `sphinx-autobuild <https://pypi.org/project/sphinx-autobuild/>`_.

.. code-block:: bash

    pip install -e ".[docs]"
    sphinx-autobuild docs docs/_build/html --ignore=docs/pages/getting_started/template_schema/astrodb-template-db/

The docs will then be available locally at <http://127.0.0.1:8000>.
