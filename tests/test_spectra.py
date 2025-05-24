import pytest
from specutils import Spectrum

from astrodb_utils import AstroDBError
from astrodb_utils.spectra import (
    _check_spectrum_flux_units,
    _check_spectrum_not_nans,
    _check_spectrum_wave_units,
    check_spectrum_plottable,
    ingest_spectrum,
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


@pytest.mark.filterwarnings(
    "ignore",
    message=".*SAWarning: Column 'Spectra.reference' is marked as a member of the primary key for table 'Spectra'.*",
)
@pytest.mark.filterwarnings(
    "ignore", message=".*'kiwi': No known catalog could be found.*"
)
@pytest.mark.parametrize(
    "test_input, message",
    [
        (
            {
                "source": "apple",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
            },
            "Observation date is not valid",
        ),  # missing regime
        (
            {
                "source": "apple",
                "regime": "nir",
                "instrument": "SpeX",
                "obs_date": "2020-01-01",
            },
            "Reference is required",
            # "Value required for telescope",
        ),  # missing telescope
        (
            {
                "source": "apple",
                "regime": "nir",
                "telescope": "IRTF",
                "obs_date": "2020-01-01",
            },
            "Reference is required",
            # "Value required for instrument",
        ),  # missing instrument
        (
            {
                "source": "apple",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "obs_date": "2020-01-01",
            },
            "Reference is required",
            # "NOT NULL constraint failed: Spectra.reference",
        ),  # missing reference
        (
            {
                "source": "apple",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "obs_date": "2020-01-01",
                "reference": "Ref 5",
            },
            "Reference not found",
        ),  # invalid reference
        (
            {
                "source": "kiwi",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "obs_date": "2020-01-01",
                "reference": "Ref 1",
            },
            "No unique source match",
        ),  # invalid source
        (
            {
                "source": "apple",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "reference": "Ref 1",
            },
            "Observation date is not valid",
        ),  # missing date
        (
            {
                "source": "apple",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "fake regime",
                "obs_date": "2020-01-01",
                "reference": "Ref 1",
            },
            "Regime not found",
        ),  # invalid regime
    ],
)
def test_ingest_spectrum_errors(temp_db, test_input, message):
    # Test for ingest_spectrum that is expected to return errors

    # Prepare parameters to send to ingest_spectrum
    spectrum = "https://bdnyc.s3.amazonaws.com/IRS/2MASS+J03552337%2B1133437.fits"
    parameters = {"db": temp_db, "spectrum": spectrum}
    parameters.update(test_input)

    # Check that error was raised
    with pytest.raises(AstroDBError) as error_message:
        _ = ingest_spectrum(**parameters)
        assert message in str(error_message.value)

    # Suppress error but check that it was still captured
    result = ingest_spectrum(**parameters, raise_error=False)
    assert result["added"] is False
    assert message in result["message"]


def test_ingest_spectrum_works(temp_db):
    spectrum = "https://bdnyc.s3.amazonaws.com/IRS/2MASS+J03552337%2B1133437.fits"
    result = ingest_spectrum(
        temp_db,
        source="banana",
        regime="nir",
        spectrum=spectrum,
        reference="Ref 1",
        obs_date="2020-01-01",  # needs to be a datetime object
        telescope="IRTF",
        instrument="SpeX",
        mode="Prism",
    )
    assert result["added"] is True
