import logging

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from specutils import Spectrum1D

from astrodb_utils import AstroDBError


__all__ = []


logger = logging.getLogger("AstroDB")


def check_spectrum_class(spectrum, raise_error=True):
    try:
        Spectrum1D.read(spectrum)
        return True
    except Exception as e:
        msg = (
            f"{e} \n Unable to load file as Spectrum1D object:{spectrum}"  
        )
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False


def check_spectrum_not_nans(spectrum, raise_error=True):
    nan_check: np.ndarray = ~np.isnan(spectrum.flux) & ~np.isnan(spectrum.spectral_axis)
    wave = spectrum.spectral_axis[nan_check]
    if not len(wave):
        msg = "Spectrum is all NaNs"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    else: 
        return True


def check_spectrum_units(spectrum, raise_error=True):

    try:
        wave: np.ndarray = spectrum.spectral_axis.to(u.micron).value
        flux: np.ndarray = spectrum.flux.value
    except AttributeError as e:
        msg = str(e) + f"Unable to parse spectral axis: {spectrum_path}"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    except u.UnitConversionError as e:
        msg = (
            f"{e} \n"
            f"Unable to convert spectral axis to microns:  {spectrum_path}"
        )
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    except ValueError as e:
        msg = f"{e} \n Value error: {spectrum_path}:"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False


def plot_spectrum(spectrum):
    plt.plot(spectrum.spectral_axis, spectrum.flux)
    plt.show()
    # TODO: add labels with spectral axis units


def check_spectrum_plottable(spectrum_path, raise_error=True, show_plot=False):
    """
    Check if spectrum is plottable
    """
    # load the spectrum and make sure it's readable as a Spectrum1D object, has units, is not all NaNs.
    class_check = check_spectrum_class(spectrum_path, raise_error=raise_error)
    if not class_check:
        return False    
    else:
        spectrum = Spectrum1D.read(spectrum_path)

    # checking spectrum has good units
    unit_check = check_spectrum_units(spectrum, raise_error=raise_error)
    if not unit_check:
        return False

    # check for NaNs
    nan_check = check_spectrum_not_nans(spectrum, raise_error=raise_error)
    if not nan_check:
        return False

    if show_plot:
        plot_spectrum(spectrum)

    return True