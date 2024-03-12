# astrodb-scripts
[![Test astrodb-utils](https://github.com/astrodbtoolkit/astrodb-scripts/actions/workflows/run_tests.yml/badge.svg)](https://github.com/astrodbtoolkit/astrodb-scripts/actions/workflows/run_tests.yml)
[![Documentation Status](https://readthedocs.org/projects/astrodb-scripts/badge/?version=latest)](https://astrodb-scripts.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/astrodb-scripts.svg)](https://badge.fury.io/py/astrodb-scripts)

# Developer Setup Instructions
- Make new environment with Python=3.10
- Install dependencies using an editable install:
  ```
  pip install -e ".[test]"
  ```
- In the `tests/` directory, clone the `astrodb-template` repo:
  ```
  git clone git@github.com:astrodbtoolkit/astrodb-template-db.git
  ```
- Be sure to run tests from the top level directory.
