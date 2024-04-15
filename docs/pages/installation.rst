wouInstallation and setup
===========================

Installing with pip
-----------------------
`astrodb_utils` is distributed on `PyPI <https://pypi.org/>`_. It can be installed with

.. code-block:: bash

    pip install astrodb_utils

Installing from source
-----------------------

We develop `astrodb_utils` on `GitHub <https://github.com/astrodbtoolkit/astrodb_utils>`_.
If you received the code as a tarball or zip, feel free to skip the first three lines; they essentially download the source code.
We recommend running the below lines in a fresh `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_ environment
to avoid package dependency isues.

.. code-block:: bash

    python3 -m pip install -U pip
    python3 -m pip install -U setuptools setuptools_scm pep517
    git clone https://github.com/astrodbtoolkit/astrodb_utils.git
    cd astrodb_utils
    python3 -m pip install -e .


Set up ADS token
-----------------------
`astrodb_utils` can query the `NASA Astrophysics Data System <https://ui.adsabs.harvard.edu/>`_ with the `ingest_publications` function.
To use this feature, you'll need to set up an ADS token and add it to your environment.

1. Make an ADS account at `https://ui.adsabs.harvard.edu/help/api/`.
2. Go to `https://ui.adsabs.harvard.edu/user/settings/token`.
3. Copy the token generated on the package.
4. Add the token to your environment by running

    .. code-block:: bash

        export ADS_TOKEN=<your token>

replacing <your token> with the token you copied.


Test the installation
---------------------

If you'd like to run tests, make sure to install the package with the optional test dependencies. E.g.,

.. code-block:: bash

    pip install -e ".[test]"

Then, in the tests directory, run

.. code-block:: bash

    git clone git@github.com:astrodbtoolkit/astrodb-template-db.git

This step installs a template repository. Tests can then be run in the top-level directory.
