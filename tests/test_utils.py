import logging

import pytest

from astrodb_utils import AstroDBError
from astrodb_utils.utils import get_db_regime


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

    