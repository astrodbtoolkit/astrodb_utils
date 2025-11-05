import logging
import os

from astrodb_utils import build_db_from_json, read_db_from_file
from astrodb_utils.utils import load_astrodb


def test_load_astrodb_deprecated(db, caplog):
    with caplog.at_level(logging.WARNING):
        _ = load_astrodb(
                db_file="astrodb-template-tests",
                data_path="tests/astrodb-template-db/data",
                felis_schema='tests/astrodb-template-db/schema.yaml'
                )
        assert "load_astrodb is deprecated" in caplog.text


def test_build_db_from_json():
    _ = build_db_from_json(
        toml_file='database.toml',
        db_path='tests/astrodb-template-db',
        db_name='astrodb-template-tests',
    )
    assert _ is not None


def test_read_db_from_file():
    _ = read_db_from_file(
        db_name="astrodb-template-tests"
    )
    assert _ is not None
