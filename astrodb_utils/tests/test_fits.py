import astropy.units as u
import numpy as np
import pytest

from astrodb_utils.fits import (
    add_missing_keywords,
    add_observation_date,
    add_wavelength_keywords,
    check_header,
    get_keywords,
)


def test_add_missing_keywords():
    result = add_missing_keywords() # default is simple-spectrum
    keywords = get_keywords(format='simple-spectrum')
    assert len(result) == len(keywords)
    for keyword, comment in keywords:
        value = result.get(keyword)
        assert value is None

def test_add_wavelength_keywords():
    header = add_missing_keywords()
    wavelength = np.arange(5100, 5300)*u.AA
    add_wavelength_keywords(header, wavelength)
    assert header['SPECBAND'] == 'em.opt.V'
    assert header['SPEC_VAL'] == 5199.5
    assert header['SPEC_BW'] == 199
    assert header['TDMIN1'] == 5100.0
    assert header['TDMAX1'] == 5299.0

@pytest.mark.parametrize("input_date,obs_date", [('2021/01/01','2021-01-01'), ('1995-05-30','1995-05-30'), ('12/15/78','1978-12-15')])
def test_add_obs_date(input_date, obs_date):
    header = add_missing_keywords()
    add_observation_date(header, input_date)
    assert header['DATE-OBS'] == obs_date

@pytest.mark.parametrize("input_date,obs_date", [('20210101','2021-01-01')])
def test_add_obs_date_fails(input_date, obs_date):
    header = add_missing_keywords()
    with pytest.raises(ValueError) as error_message:
        add_observation_date(header, input_date)
    assert "Date could not be parsed by dateparser.parse" in str(error_message.value)


def test_check_header():
    header = add_missing_keywords()
    assert check_header(header) is False

    header.set('RA_TARG',"63.831417")
    assert check_header(header) is False
    header.set('DEC_TARG',"-9.585167")
    assert check_header(header) is False
    header.set('OBJECT', "WISE J041521.21-093500.6")
    assert check_header(header) is False
    header.set('DATE-OBS', "2021-01-01")
    assert check_header(header) is True
