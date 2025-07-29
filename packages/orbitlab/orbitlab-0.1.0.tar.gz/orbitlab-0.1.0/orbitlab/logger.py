# orbitlab/logger.py
import sys
import logging
import structlog
from orbitlab.config import OrbitSettings

settings = OrbitSettings()

LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=LOG_LEVEL
)

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),
    processors=[
        structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False),
        structlog.processors.KeyValueRenderer(key_order=["event"]) 
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(settings.PROJECT_NAME)
