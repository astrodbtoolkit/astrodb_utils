import os

import pytest

from astrodb_utils.spectra import (
    check_spectrum_class,
    check_spectrum_not_nans,
    check_spectrum_plottable,
    check_spectrum_units,
    plot_spectrum,
)


@pytest.mark.parametrize(
    "spectrum_path, result",
    [
        ("./astrodb_utils/tests/data/2MASS+J21442847+1446077.fits", True),
        ("./astrodb_utils/tests/data/U50184_1022+4114_HD89744B_BUR08B.fits", False),
        ("./astrodb_utils/tests/data/U50185_GJ1048B_0235-2331_BUR08B.fits", False),
    ],
)
def test_check_spectrum_class(spectrum_path, result):
    assert os.path.exists(spectrum_path) == True
    check = check_spectrum_class(spectrum_path, raise_error=False)
    assert check == result
