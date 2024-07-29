import os

import pytest
from specutils import Spectrum1D

from astrodb_utils import AstroDBError
from astrodb_utils.spectra import (
    check_spectrum_class,
    check_spectrum_not_nans,
    check_spectrum_plottable,
    check_spectrum_units,
    plot_spectrum,
)


@pytest.fixture(scope="module")
def t_spectrum():
    path = "./astrodb_utils/tests/data/2MASS+J21442847+1446077.fits"
    spectrum = Spectrum1D.read(path)
    return spectrum


@pytest.mark.parametrize(
    "spectrum_path, result",
    [
        ("./astrodb_utils/tests/data/2MASS+J21442847+1446077.fits", True),
        ("./astrodb_utils/tests/data/U50184_1022+4114_HD89744B_BUR08B.fits", False),
    ],
)
def test_check_spectrum_class(spectrum_path, result):
    assert os.path.exists(spectrum_path) is True
    check = check_spectrum_class(spectrum_path, raise_error=False)
    assert check == result


@pytest.mark.parametrize(
    "spectrum_path",
    [
        ("./astrodb_utils/tests/data/U50184_1022+4114_HD89744B_BUR08B.fits"),
    ],
)
def test_check_spectrum_class_errors(spectrum_path):
    with pytest.raises(AstroDBError) as error_message:
        check_spectrum_class(spectrum_path, raise_error=True)
        assert "Unable to load file as Spectrum1D object" in str(error_message)


def test_spectrum_not_nans(t_spectrum):
    check = check_spectrum_not_nans(t_spectrum)
    assert check is True