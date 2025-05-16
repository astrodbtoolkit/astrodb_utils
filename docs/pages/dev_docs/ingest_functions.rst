Ingest functions
================

Ingest functions: 
- only ingest one thing. E.g., one parameter, or one spectrum.
- use raise_error = True/False. If True, raise an error if the ingest fails. If False, return None if the ingest fails and log warning.
- use helper functions to get constrained values from the database such as regime, instrument, etc.

Need to decide:
- ways to accept input. E.g, parameter= parameter, value=value, OR paramet dict = {parameter: value}. See https://github.com/astrodbtoolkit/astrodb_utils/issues/13
- 
- 