Installation and setup
===========================

Installing with pip
-----------------------
`astrodb_utils` is distributed on `PyPI <https://pypi.org/project/astrodb-scripts/>`_. It can be installed with

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


