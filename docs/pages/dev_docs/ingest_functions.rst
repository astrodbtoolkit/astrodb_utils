Ingest functions
================

Ingest function design guidelines
--------------------------------- 
* ingest one thing. E.g., one parameter, or one spectrum.
* use `raise_error = True/False`. 
  * use :py:mod:`exit_function<astrodb_utils.utils.exit_function>` to help
  * If `True`, raise an error if the ingest fails. 
  * If `False`, return `None` and log warning if the ingest fails and log warning.

- use helper functions to get constrained values from the database such as regime, instrument, etc.
- * :py:mod:`astrodb_utils.utils.get_constrained_value`

Need to decide
--------------
- ways to accept input. E.g, parameter= parameter, value=value, OR paramet dict = {parameter: value}. See https://github.com/astrodbtoolkit/astrodb_utils/issues/13
  