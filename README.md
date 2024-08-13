# astrodb_utils
[![Test astrodb-utils](https://github.com/astrodbtoolkit/astrodb-scripts/actions/workflows/run_tests.yml/badge.svg)](https://github.com/astrodbtoolkit/astrodb-scripts/actions/workflows/run_tests.yml)
[![Documentation Status](https://readthedocs.org/projects/astrodb-scripts/badge/?version=latest)](https://astrodb-scripts.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/astrodb-scripts.svg)](https://badge.fury.io/py/astrodb-utils)

The following tables are expected by AstroDB Toolkit and the `astrodb_utils` package:
- Sources
- Publications
- Names
- Telescopes
- Instruments

You may modify these tables, but doing so may decrease the interoperability of your database with other tools.

# Developer Setup Instructions
- Make new environment with Python=3.10
- Install dependencies using an editable install:
  ```
  pip install -e ".[test]"
  ```
- In the `astrodb_utils/tests/` directory, clone the `astrodb-template-db` repo:
  ```
  git clone https://github.com/astrodbtoolkit/astrodb-template-db.git
  ```
- Be sure to run tests from the top level directory.
