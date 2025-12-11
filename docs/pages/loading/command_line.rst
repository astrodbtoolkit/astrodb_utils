Command-Line Interface
======================

The ``build_db_from_json`` command allows you to create and populate an
SQLite database from JSON data files without writing Python code.

Basic Usage
-----------

The simplest way to build your database is to use the
``build_db_from_json`` command with your ``database.toml``
configuration file:

.. code-block:: bash

   build_db_from_json database.toml

This command will:

* Read the database configuration from ``database.toml``
* Load the Felis schema from the path specified in the TOML
  file
* Create a new SQLite database file
* Ingest all JSON data from the data directory

Command-Line Options
---------------------

You can override settings from the TOML file using
command-line arguments:

.. code-block:: bash

   build_db_from_json database.toml \
     --base-path /path/to/data \
     --db-name my_database \
     --data-path custom_data/ \
     --felis-path custom_schema.yaml \
     --lookup-tables Publications Telescopes Instruments \
     --verbose

Arguments
^^^^^^^^^

``settings_file``
    Name of the TOML file containing database settings.

    * Default: ``database.toml``
    * Example: ``build_db_from_json my_config.toml``

``--base-path PATH``
    Path to the directory containing the TOML file.

    * Default: current directory (``.``)
    * Useful when your configuration is in a different
      directory
    * Example: ``--base-path /home/user/database-repo``

``--db-name NAME``
    Override the database name from the TOML file.

    * Default: None (reads from TOML)
    * Useful for creating multiple databases from the same
      configuration
    * Example: ``--db-name production_db``
    * Note: Do not include the ``.sqlite`` extension

``--felis-path PATH``
    Override the schema file path.

    * Default: None (reads from TOML)
    * Path can be relative or absolute
    * Example: ``--felis-path schema/v2.yaml``

``--data-path PATH``
    Override the data directory path.

    * Default: None (reads from TOML)
    * Directory should contain JSON files for ingestion
    * Example: ``--data-path /data/2025-01-01``

``--lookup-tables TABLE1 TABLE2 ...``
    Override lookup tables (space-separated list).

    * Default: None (uses TOML or built-in defaults)
    * Must be a space-separated list of table names
    * Example: ``--lookup-tables Publications Telescopes
      Instruments``

``-v, --verbose``
    Enable verbose logging output.

    * Default: disabled (INFO level logging)
    * Useful for debugging database creation issues
    * Shows detailed information about the ingestion
      process
    * Example: ``build_db_from_json database.toml --verbose``

``-h, --help``
    Display help message and exit.

    * Shows all available options and their descriptions
    * Example: ``build_db_from_json --help``

Troubleshooting
---------------

**File not found error:**

Make sure the TOML file and all paths (schema, data
directory) exist and are accessible. Use ``--verbose`` to see
exactly which paths are being accessed.

**Permission denied:**

Ensure you have read permissions for the data files and
write permissions for the output directory.

**Schema validation error:**

Check that your Felis schema file is valid YAML and matches
the expected format. See the `Felis documentation
<https://felis.lsst.io/>`_ for more information.

**No data ingested:**

Verify that:

* The data directory path is correct
* JSON files follow the expected schema
* JSON files are properly formatted
* Use ``--verbose`` to see detailed ingestion logs
