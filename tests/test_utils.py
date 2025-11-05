import logging
import os

import pytest

from astrodb_utils import AstroDBError, build_db_from_json, read_db_from_file
from astrodb_utils.utils import get_db_regime, load_astrodb


@pytest.mark.parametrize(
    ("input", "db_regime"),
    [
        ("gamma-ray", "gamma-ray"),
        ("X-ray", "x-ray"),
        ("Optical", "optical"),
    ],
)
def test_get_db_regime(db, caplog, input, db_regime):   
    regime = get_db_regime(db, input)
    assert regime == db_regime


def test_get_db_regime_hyphens(db, caplog):
    with caplog.at_level(logging.WARNING):
        regime = get_db_regime(db, "xray")
        assert regime == "x-ray"
        assert 'Regime xray matched to x-ray' in caplog.text


def test_get_db_regime_errors(db, caplog):
    with pytest.raises(AstroDBError) as error_message:
        get_db_regime(db, "notaregime")
    assert "Regime not found in database" in str(error_message.value)


def test_load_astrodb_deprecated(db, caplog):
    with caplog.at_level(logging.WARNING):
        _ = load_astrodb(
                db_file="astrodb-template-tests",
                data_path="tests/astrodb-template-db/data",
                felis_schema='tests/astrodb-template-db/schema.yaml'
                )
        assert "load_astrodb is deprecated" in caplog.text


def test_build_db_from_json():
    db = build_db_from_json(
        toml_file='database.toml',
        db_path='tests/astrodb-template-db',
        db_name='astrodb-template-tests',
    )
    assert db is not None

    # Clean up
    del db


def test_read_db_from_file():
    db = read_db_from_file(
        db_name="astrodb-template-tests"
    )
    assert db is not None

    # Clean up
    del db
    os.remove('tests/astrodb-template-tests.sqlite')



