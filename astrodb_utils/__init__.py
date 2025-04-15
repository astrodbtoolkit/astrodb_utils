import logging
import sys
import warnings

from .utils import (  # noqa: F401
    AstroDBError,
    exit_function,
    ingest_instrument,
    internet_connection,
    load_astrodb,
)

logger = logging.getLogger(__name__)


LOGFORMAT = logging.Formatter(
    "%(name)-12s: %(levelname)-8s %(message)s")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(LOGFORMAT)
logger.addHandler(handler)

logger.info("astrodb_utils logger initialized")
logger.info(f"Logger level: {logging.getLevelName(logger.getEffectiveLevel()) }")

warnings.filterwarnings("ignore", module="astroquery.simbad")
