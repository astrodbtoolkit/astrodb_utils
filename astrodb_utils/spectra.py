import importlib.util
import logging
import sys

import astropy.units as u
import numpy as np
from specutils import Spectrum1D

from astrodb_utils import AstroDBError

matplotlib_check = importlib.util.find_spec("matplotlib")
if matplotlib_check is not None:
    import matplotlib.pyplot as plt


__all__ = ["check_spectrum_class", "check_spectrum_not_nans", "check_spectrum_units", "check_spectrum_plottable"]


logger = logging.getLogger("AstroDB")


def check_spectrum_class(spectrum, raise_error=True):
    try:
        Spectrum1D.read(spectrum)
        return True
    except Exception as error_message:
        msg = f"Unable to load file as Spectrum1D object:{spectrum}"
        logger.debug(f"{error_message}")
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
        msg = f"{e} \n" f"Unable to convert spectral axis to microns:  {spectrum_path}"
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
    if "matplotlib" in sys.modules:
        plt.plot(spectrum.spectral_axis, spectrum.flux)
        plt.xlabel("Dispersion ({spectrum.spectral_axis.unit})")
        plt.ylabel("Flux ({spectrum.flux.unit})")
        plt.show()
    else:
        msg = "To display the spectrum, matplotlib most be installed."
        logger.warning(msg)        


def check_spectrum_plottable(spectrum_path, raise_error=True, show_plot=False):
    """
    Check if spectrum is plottable

    show_plot only works if matplotlib is installed. matplotlib is not installed with astrodb_utils. 

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
