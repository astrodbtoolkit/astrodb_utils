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
def test_spectrum_not_nans(spectrum_path: str):
    spectrum = Spectrum.read(spectrum_path, format="tabular-fits")
    check = _check_spectrum_not_nans(spectrum)
    assert check is True

@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less*"
)
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

@pytest.mark.filterwarnings(
    "ignore", message=".*Standard Deviation has values of 0 or less*"
)
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
    "ignore", message=".*Standard Deviation has values of 0 or less*"
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
        spectrum = Spectrum.read(spectrum_path, format="tabular-fits")
        check = check_spectrum_plottable(spectrum, show_plot=False)
    except IndexError:  # Index error expected for U50184_1022+4114_HD89744B_BUR08B
        check = False

    assert check is result


@pytest.mark.parametrize(
    ("test_input", "message"),
    [
        (
            {
                "source": "Gl 229b",
                "regime": "nir",
                "instrument": "SpeX",
                "obs_date": "2020-01-01",
            },
            "Reference is required",
        ),
        (
            {
                "source": "Gl 229b",
                "regime": "nir",
                "telescope": "IRTF",
                "obs_date": "2020-01-01",
                "reference": "Burg06"
            },
            "Instrument is required",
        ),
        (
            {
                "source": "Gl 229b",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "notarealregime",
                "obs_date": "2020-01-01",
                "reference": "Burg06"
            },
            "Regime not found in database",
        ),
        (
            {
                "source": "Gl 229b",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "obs_date": "2020-01-01",
                "reference": "NotARealReference",
            },
            "Reference not found",
        ),
        (
            {
                "source": "Gl 229b",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "reference": "Burg06"
            },
            "Observation date is not valid",),
        (
            {
                "source": "NotaRealSource",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "obs_date": "2020-01-01",
                "reference": "Burg06",
            },
            "Invalid source name",
        ),
        (
            {
                "source": "Gl 229b",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "nir",
                "reference": "Burg06",
            },
            "Observation date is not valid",
        ),
        (
            {
                "source": "Gl 229b",
                "telescope": "IRTF",
                "instrument": "SpeX",
                "mode": "Prism",
                "regime": "fake regime",
                "obs_date": "2020-01-01",
                "reference": "Burg06",
            },
            "Regime not found",
        ),
    ],
)
def test_ingest_spectrum_errors(db, test_input, message):
    # Test for ingest_spectrum that is expected to return errors

    # Prepare parameters to send to ingest_spectrum
    spectrum = "https://bdnyc.s3.amazonaws.com/IRS/2MASS+J03552337%2B1133437.fits"
    parameters = {"db": db, "spectrum": spectrum}
    parameters.update(test_input)

    # Check that error was raised
    with pytest.raises(AstroDBError) as error_message:
        _ = ingest_spectrum(**parameters)
    assert message in str(error_message.value)

    # Suppress error but check that it was still captured
    result = ingest_spectrum(**parameters, raise_error=False)
    assert result["added"] is False
    assert message in result["message"]


def test_ingest_spectrum_works(db):
    spectrum = "https://bdnyc.s3.amazonaws.com/IRS/2MASS+J03552337%2B1133437.fits"
    result = ingest_spectrum(
        db,
        source="TWA 26",
        regime="nir",
        spectrum=spectrum,
        reference="Burg06",
        obs_date="2020-01-01",  # needs to be a datetime object
        telescope="IRTF",
        instrument="SpeX",
        mode="Prism",
    )
    assert result["added"] is True
