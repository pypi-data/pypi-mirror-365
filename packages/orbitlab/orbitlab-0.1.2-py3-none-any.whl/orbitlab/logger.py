# orbitlab/logger.py
import logging
from orbitlab.config import OrbitSettings

settings = OrbitSettings()

logger = logging.getLogger("orbit")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

formatter = logging.Formatter("%(message)s")

# Opcional: evitar múltiples handlers en recarga
if not logger.handlers:
    if settings.DEBUG_TO_CONSOLE or settings.INFO_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if settings.DEBUG_TO_FILE or settings.INFO_TO_FILE:
        file_handler = logging.FileHandler(settings.LOGS_DIR, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
