import importlib.util
import logging
import sys

import astropy.units as u
import numpy as np
from specutils import Spectrum

from astrodb_utils import AstroDBError, exit_function

matplotlib_check = importlib.util.find_spec("matplotlib")
if matplotlib_check is not None:
    import matplotlib.pyplot as plt


__all__ = ["check_spectrum_plottable"]

logger = logging.getLogger(__name__)


def check_spectrum_plottable(
    spectrum_path: str | Spectrum, raise_error: bool = True, show_plot: bool = False, format: str = None
):
    """
    Check if spectrum is readable and plottable with specutils.
    show_plot = True requires matplotlib to be installed.

    Parameters
    ----------
    spectrum_path : str or Spectrum
        Path to spectrum file or Spectrum object

    raise_error : bool. Default=True
        True: Raise error if spectrum is not plottable
        False: Do not raise error if spectrum is not plottable. Log warning instead.

    show_plot : bool. Default=False
        True: Show plot of spectrum. Matplotlib must be installed.

    format : str, optional
        Format of the spectrum file. If not provided, the format will be inferred by specutils.

    Returns
    -------
    bool
        True: Spectrum is plottable
        False: Spectrum is not plottable

    """
    # check if spectrum is a Spectrum object or a file path
    # if it's a file path, check if it can be read as a Spectrum object    
    if isinstance(spectrum_path, Spectrum):
        spectrum = spectrum_path
    elif isinstance(spectrum_path, str):
        try:
            spectrum = Spectrum.read(spectrum_path, format=format)
        except Exception as error_message:
            msg = f"Unable to load file as Spectrum object:{spectrum_path}:\n{error_message}"
            exit_function(msg, raise_error=raise_error)
    else:
        msg = f"Input is not a valid path or Spectrum object: {spectrum_path}"
        exit_function(msg, raise_error=raise_error)

    # checking spectrum has good units
    wave_unit_check = _check_spectrum_wave_units(spectrum, raise_error=raise_error)
    if not wave_unit_check:
        return False

    flux_unit_check = _check_spectrum_flux_units(spectrum, raise_error=raise_error)
    if not flux_unit_check:
        return False

    # check for NaNs
    nan_check = _check_spectrum_not_nans(spectrum, raise_error=raise_error)
    if not nan_check:
        return False

    if show_plot:
        _plot_spectrum(spectrum)

    return True
    

def _check_spectrum_not_nans(spectrum, raise_error=True):
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


def _check_spectrum_wave_units(spectrum, raise_error=True):
    try:
        spectrum.spectral_axis.to(u.micron).value
        return True
    except AttributeError as e:
        logger.debug(f"{e}")
        msg = f"Unable to parse spectral axis: {spectrum}"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    except u.UnitConversionError as e:
        logger.debug(f"{e}")
        msg = f"Unable to convert spectral axis to microns:  {spectrum}"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    except ValueError as e:
        logger.debug(f"{e}")
        msg = f"Value error: {spectrum}:"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False


def _check_spectrum_flux_units(spectrum, raise_error=True):
    expected_units = [
        u.get_physical_type(u.erg / u.s / u.cm**2 / u.AA),
        u.get_physical_type(u.Jy),
    ]

    unit_type = u.get_physical_type(spectrum.flux.unit)

    if unit_type in expected_units:
        return True
    else:
        msg = f"flux units are not expected: {spectrum.flux.unit}. Expecting {expected_units}."
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False


def _plot_spectrum(spectrum):
    if "matplotlib" in sys.modules:
        plt.plot(spectrum.spectral_axis, spectrum.flux)
        plt.xlabel(f"Dispersion ({spectrum.spectral_axis.unit})")
        plt.ylabel(f"Flux ({spectrum.flux.unit})")
        plt.show()
    else:
        msg = "To display the spectrum, matplotlib most be installed."
        logger.warning(msg)
