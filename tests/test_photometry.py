import pytest
import astropy.units as u
from astrodb_scripts import AstroDBError
from astrodb_scripts.photometry import (
    ingest_photometry,
    ingest_photometry_filter,
    fetch_svo,
    assign_ucd,
)


def test_ingest_photometry(db):
    ingest_photometry(
        db,
        source="Dark energy source 1",
        band="Generic/Johnson.V",
        magnitude=10,
        reference="Rubin80",
    )
    ingest_photometry(
        db,
        source="Dark energy source 2",
        band="Generic/Cousins.R",
        magnitude=10,
        reference="Riess98",
        telescope="Generic",
    )


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_ingest_photometry_fails(db):
    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(db, source="test")
    assert "are required" in str(error_message.value)
    result = ingest_photometry(db, source="test", raise_error=False)
    assert result["added"] is False

    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(db, source="test", band="V")
    assert "are required" in str(error_message.value)
    result = ingest_photometry(db, source="test", band="V", raise_error=False)
    assert result["added"] is False

    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(db, source="test", band="V", magnitude=10)
    assert "are required" in str(error_message.value)
    result = ingest_photometry(
        db, source="test", band="V", magnitude=10, raise_error=False
    )
    assert result["added"] is False

    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(db, source="test", band="V", magnitude=10, reference="ref")
    assert "No unique source match" in str(error_message.value)
    result = ingest_photometry(
        db, source="test", band="V", magnitude=10, reference="ref", raise_error=False
    )
    assert result["added"] is False

    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(
            db,
            source="Dark energy source 1",
            band="2MASS/2MASS.J",
            magnitude=10,
            reference="ref",
        )
    assert "not found in Publications table" in str(error_message.value)
    result = ingest_photometry(
        db,
        source="Dark energy source 1",
        band="2MASS/2MASS.J",
        magnitude=10,
        reference="ref",
        raise_error=False,
    )
    assert result["added"] is False

    with pytest.raises(AstroDBError) as error_message:
        ingest_photometry(
            db,
            source="Dark energy source 1",
            band="Generic/Cousins.R",
            magnitude=10,
            reference="Rubin80",
            telescope="HST",
        )
    assert "not found in Telescopes table" in str(error_message.value)
    result = ingest_photometry(
        db,
        source="Dark energy source 1",
        band="Generic/Cousins.R",
        magnitude=10,
        reference="Rubin80",
        telescope="HST",
        raise_error=False,
    )
    assert result["added"] is False


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
