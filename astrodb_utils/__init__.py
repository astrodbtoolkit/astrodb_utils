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
logger.setLevel(logging.INFO)

LOGFORMAT = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S%p"
)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(LOGFORMAT)
logger.addHandler(handler)

warnings.filterwarnings("ignore", module="astroquery.simbad")
