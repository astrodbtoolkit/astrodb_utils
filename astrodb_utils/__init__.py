import logging
import sys
import warnings

from .utils import (  # noqa: F401
    AstroDBError,
    exit_function,
    internet_connection,
    load_astrodb,
)
from .version import version as __version__

__all__ = ["__version__"]



logger = logging.getLogger(__name__) # Sets up the parent "astrodb_utils" logger

LOGFORMAT = logging.Formatter(
    "%(levelname)-8s - %(name)-15s - %(message)s")

# To prevent duplicate handlers, clear all existing handlers and re-add them
# Keeping this here in case we need it
# for handler in logger.handlers:
#    logger.removeHandler(handler)
# logger.addHandler(ch)

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(LOGFORMAT)
logger.addHandler(handler)

logger.setLevel(logging.INFO)  # Set the default logging level to INFO
logger.debug(f"Logger level: {logging.getLevelName(logger.getEffectiveLevel()) }")

warnings.filterwarnings("ignore", module="astroquery.simbad")
