import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import SkyCoord

from astrodb_utils.fits import (
    add_missing_keywords,
    add_observation_date,
    add_wavelength_keywords,
    check_header,
    get_keywords,
    make_skycoord,
)


@pytest.mark.parametrize("format", ["ivoa-spectrum-dm-1.2", "simple-spectrum"])
def test_add_missing_keywords(format):
    result = add_missing_keywords(format=format)
    keywords = get_keywords(format=format)
    assert len(result) == len(keywords)

    # most keywords should be None
    if format == "ivoa-spectrum-dm-1.2":
        for keyword, comment in keywords:
            value = result.get(keyword)
            if keyword == "VOCLASS":
                assert value.startswith("Spectrum-1.")
            else:
                assert value is None
    elif format == "simple-spectrum":
        for keyword, comment in keywords:
            value = result.get(keyword)
            assert value is None


def test_add_wavelength_keywords():
    header = add_missing_keywords()
    wavelength = np.arange(5100, 5300) * u.AA
    add_wavelength_keywords(header, wavelength)
    assert header["SPECBAND"] == "em.opt.V"
    assert header["SPEC_VAL"] == 5199.5
    assert header["SPEC_BW"] == 199
    assert header["TDMIN1"] == 5100.0
    assert header["TDMAX1"] == 5299.0


@pytest.mark.parametrize(
    "input_date,obs_date",
    [
        ("2021/01/01", "2021-01-01"),
        ("1995-05-30", "1995-05-30"),
        ("12/15/78", "1978-12-15"),
    ],
)
def test_add_obs_date(input_date, obs_date):
    header = add_missing_keywords()
    add_observation_date(header, input_date)
    assert header["DATE-OBS"] == obs_date


@pytest.mark.parametrize("input_date,obs_date", [("20210101", "2021-01-01")])
def test_add_obs_date_fails(input_date, obs_date):
    header = add_missing_keywords()
    with pytest.raises(ValueError) as error_message:
        add_observation_date(header, input_date)
    assert "Date could not be parsed by dateparser.parse" in str(error_message.value)


def test_check_header():
    header = add_missing_keywords()
    assert check_header(header) is False

    header.set("RA_TARG", "63.831417")
    assert check_header(header) is False
    header.set("DEC_TARG", "-9.585167")
    assert check_header(header) is False
    header.set("OBJECT", "WISE J041521.21-093500.6")
    assert check_header(header) is False
    header.set("DATE-OBS", "2021-01-01")
    assert check_header(header) is True


def test_make_skycoord():
    header = add_missing_keywords()
    header.set("RA", "63.831417")
    assert make_skycoord(header) is None  # missing DEC
    header.set("DEC", "-9.585167")
    assert isinstance(make_skycoord(header), SkyCoord)

    header2 = add_missing_keywords()
    header2.set("RA_TARG", "63.831417")
    header2.set("DEC_TARG", "-90.585167")
    assert make_skycoord(header2) is None  # Dec out of range
    header2.set("DEC_TARG", "89.585167")
    assert isinstance(make_skycoord(header2), SkyCoord)
