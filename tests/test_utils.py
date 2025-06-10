import pytest

from astrodb_utils import AstroDBError
from astrodb_utils.utils import get_db_regime


@pytest.mark.parametrize(
    "input, db_regime",
    [
        ("gamma-ray", "gamma-ray"),
        ("X-ray", "x-ray"),
        ("Optical", "optical"),
    ],
)
def test_get_db_regime(db, input, db_regime):   
    #  TESTS WHICH SHOULD WORK
    regime = get_db_regime(db, input)
    assert regime == db_regime


def test_get_db_regime_errors(db):
    #  TESTS WHICH SHOULD FAIL
    with pytest.raises(AstroDBError) as error_message:
        get_db_regime(db, "not_a_regime")
    assert "Regime not_a_regime not found in database" in str(error_message.value)

    with pytest.raises(AstroDBError) as error_message:
        get_db_regime(db, "xray")
    assert "Regime xray not found in database" in str(error_message.value)
