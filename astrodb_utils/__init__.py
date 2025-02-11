import logging
import sys
import warnings

from .utils import (
    AstroDBError,  # noqa: F401
    find_publication,  # noqa: F401
    find_source_in_db,  # noqa: F401
    ingest_instrument,  # noqa: F401
    ingest_names,  # noqa: F401
    ingest_publication,  # noqa: F401
    ingest_source,  # noqa: F401
    internet_connection,  # noqa: F401
    load_astrodb,  # noqa: F401
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
