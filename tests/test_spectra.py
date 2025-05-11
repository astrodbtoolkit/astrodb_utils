import pytest
from specutils import Spectrum

from astrodb_utils.spectra import (
    _check_spectrum_flux_units,
    _check_spectrum_not_nans,
    _check_spectrum_wave_units,
    check_spectrum_plottable,
)


@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less.*"
)
@pytest.mark.parametrize(
    "spectrum_path",
    [
        ("tests/data/2MASS+J21442847+1446077.fits"),
        ("tests/data/WISEAJ2018-74MIRI.fits"),
    ],
)
def test_spectrum_not_nans(spectrum_path):
    spectrum = Spectrum.read(spectrum_path, format='tabular-fits')
    check = _check_spectrum_not_nans(spectrum)
    assert check is True


@pytest.mark.parametrize(
    "spectrum_path",
    [
        ("tests/data/2MASS+J21442847+1446077.fits"),
        ("tests/data/WISEAJ2018-74MIRI.fits"),
    ],
)
def test_check_spectrum_wave_units(spectrum_path):
    spectrum = Spectrum.read(spectrum_path, format='tabular-fits')
    check = _check_spectrum_wave_units(spectrum)
    assert check is True


@pytest.mark.parametrize(
    "spectrum_path",
    [
        ("tests/data/2MASS+J21442847+1446077.fits"),
        ("tests/data/WISEAJ2018-74MIRI.fits"),
    ],
)
def test_check_spectrum_flux_units(spectrum_path):
    spectrum = Spectrum.read(spectrum_path, format='tabular-fits')
    check = _check_spectrum_flux_units(spectrum)
    assert check is True


@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less.*"
)
@pytest.mark.parametrize(
    ("spectrum_path","result"),
    [
        ("tests/data/U50184_1022+4114_HD89744B_BUR08B.fits", False),
        ("tests/data/2MASS+J21442847+1446077.fits", True),
        ("tests/data/WISEAJ2018-74MIRI.fits", True),
    ],
)
def test_check_spectrum_plottable(spectrum_path, result):
    try:
        spectrum = Spectrum.read(spectrum_path, format='tabular-fits')
        check = check_spectrum_plottable(spectrum, show_plot=False)
    except IndexError: # Index error expected for U50184_1022+4114_HD89744B_BUR08B
        check = False
        
    assert check is result



# TODO: Find spectra which have these problems    
# def test_check_spectrum_wave_units_errors(t_spectrum):
#     t_spectrum.spectral_axis = t_spectrum.spectral_axis * u.m  # Set incorrect units
#     with pytest.raises(AstroDBError) as error_message:
#         check_spectrum_units(t_spectrum, raise_error=True)
#         assert "Unable to convert spectral axis to microns" in str(error_message)
#
#
# def test_check_spectrum_flux_units_errors(t_spectrum):