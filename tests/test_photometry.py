import astropy.units as u
import pytest

from astrodb_utils import AstroDBError
from astrodb_utils.photometry import (
    assign_ucd,
    fetch_svo,
    ingest_photometry,
    ingest_photometry_filter,
)


def test_ingest_photometry(db):
    ingest_photometry(
        db,
        source="Crab Nebula",
        band="Generic/Johnson.V",
        regime="optical",
        magnitude=10,
        reference="Rubin80",
    )
    ingest_photometry(
        db,
        source="WASP-76b",
        band="Generic/Cousins.R",
        regime="optical",
        magnitude=10,
        reference="Riess98",
        telescope="Generic",
    )


@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.parametrize(
    "kwargs, expected_error",
    [
        ({"source": "test"}, "are required"),
        ({"source": "test", "band": "V"}, "are required"),
        ({"source": "test", "band": "V", "magnitude": 10}, "are required"),
        (
            {"source": "test", "band": "V", "magnitude": 10, "reference": "ref"},
            "No unique source match",
        ),
        (
            {
                "source": "Crab Nebula",
                "band": "2MASS/2MASS.J",
                "magnitude": 10,
                "reference": "ref",
            },
            "not found in Publications table",
        ),
        (
            {
                "source": "Crab Nebula",
                "band": "Generic/Cousins.R",
                "magnitude": 10,
                "reference": "Rubin80",
                "telescope": "Fake HST",
            },
            "not found in Telescopes table",
        ),
    ],
)
def test_ingest_photometry_fails(db, kwargs, expected_error):
    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(db, **kwargs)
    assert expected_error in str(error_message.value)

    result = ingest_photometry(db, **kwargs, raise_error=False)
    assert result["added"] is False


@pytest.mark.dependency()
@pytest.mark.xfail(reason="Test may fail due to SVO being down")
def test_svo_up():
    """
    Test if the SVO is reachable
    """
    filter_id, wave, fwhm, width = fetch_svo("HST", "WFC3_IR", "F140W")
    assert filter_id == "HST/WFC3_IR.F140W"


@pytest.mark.dependency(depends=["test_svo_up"])
@pytest.mark.parametrize(
    "telescope, instrument, filter_name, wavelength",
    [("HST", "WFC3_IR", "F140W", 13734.66)],
)
def test_fetch_svo(telescope, instrument, filter_name, wavelength):
    filter_id, wave, fwhm, width = fetch_svo(telescope, instrument, filter_name)
    assert wave.unit == "Angstrom"
    assert wave.value == pytest.approx(wavelength)
    assert filter_id == "HST/WFC3_IR.F140W"
    assert width.unit == u.Angstrom


@pytest.mark.dependency(depends=["test_svo_up"])
def test_fetch_svo_fail():
    with pytest.raises(AstroDBError) as error_message:
        fetch_svo("HST", "WFC3", "F140W")
    assert "not found in SVO" in str(error_message.value)

    # TODO: Simulate no internet connection with pytest-socket


@pytest.mark.parametrize(
    "wave, ucd",
    [
        (100, None),
        (3001, "em.opt.U"),
        (4500, "em.opt.B"),
        (5500, "em.opt.V"),
        (6500, "em.opt.R"),
        (8020, "em.opt.I"),
        (12000, "em.IR.J"),
        (16000, "em.IR.H"),
        (22000, "em.IR.K"),
        (35000, "em.IR.3-4um"),
        (45000, "em.IR.4-8um"),
        (85000, "em.IR.8-15um"),
        (100000, "em.IR.8-15um"),
        (200000, "em.IR.15-30um"),
        (500000, None),
    ],
)
def test_assign_ucd(wave, ucd):
    assert assign_ucd(wave * u.Angstrom) == ucd

@pytest.mark.dependency(depends=["test_svo_up"])
def test_ingest_photometry_filter(db):
    ingest_photometry_filter(
        db, telescope="SLOAN", instrument="SDSS", filter_name="zprime_filter"
    )
    assert (
        db.query(db.PhotometryFilters)
        .filter(db.PhotometryFilters.c.band == "SLOAN/SDSS.zprime_filter")
        .count()
        == 1
    )


@pytest.mark.dependency(depends=["test_svo_up"])
def test_ingest_photometry_filter_errors(db):
    # Filter already ingested
    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry_filter(
            db, telescope="SLOAN", instrument="SDSS", filter_name="u"
        )
    assert "already exists" in str(error_message.value)

    # Telescope not in the SVO
    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry_filter(
            db, telescope="Rainbow", instrument="Pony", filter_name="BVRI"
        )
    assert "not found in SVO" in str(error_message.value)
