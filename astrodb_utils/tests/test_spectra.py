import os

import pytest
from specutils import Spectrum1D

from astrodb_utils import AstroDBError
from astrodb_utils.spectra import (
    check_spectrum_class,
    check_spectrum_flux_units,
    check_spectrum_not_nans,
    check_spectrum_plottable,
    check_spectrum_wave_units,
)


@pytest.fixture(scope="module")
def good_spectrum_path():
    return "./astrodb_utils/tests/data/2MASS+J21442847+1446077.fits"


@pytest.fixture(scope="module")
def good_spectrum(good_spectrum_path):
    return Spectrum1D.read(good_spectrum_path)


@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less.*"
)
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


@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less.*"
)
def test_spectrum_not_nans(good_spectrum):
    check = check_spectrum_not_nans(good_spectrum)
    assert check is True


def test_check_spectrum_wave_units(good_spectrum):
    check = check_spectrum_wave_units(good_spectrum)
    assert check is True


def test_check_spectrum_flux_units(good_spectrum):
    check = check_spectrum_flux_units(good_spectrum)
    assert check is True


@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less.*"
)
def test_check_spectrum_plottable(good_spectrum, good_spectrum_path):
    check = check_spectrum_plottable(good_spectrum, show_plot=False)
    assert check is True

    check = check_spectrum_plottable(good_spectrum_path, show_plot=False)
    assert check is True



# TODO: Find spectra which have these problems    
# def test_check_spectrum_wave_units_errors(t_spectrum):
#     t_spectrum.spectral_axis = t_spectrum.spectral_axis * u.m  # Set incorrect units
#     with pytest.raises(AstroDBError) as error_message:
#         check_spectrum_units(t_spectrum, raise_error=True)
#         assert "Unable to convert spectral axis to microns" in str(error_message)
#
#
# def test_check_spectrum_flux_units_errors(t_spectrum):