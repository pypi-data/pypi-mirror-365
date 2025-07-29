# orbitlab/logger.py
import logging
from typing import Optional
from orbitlab.config import OrbitSettings

logger = logging.getLogger("orbit")
logger.propagate = False 
formatter = logging.Formatter("%(message)s")

def configurar_logger(settings: Optional[OrbitSettings] = None):
    """
    Configura el logger global según los OrbitSettings proporcionados.
    Puede ser invocado dinámicamente desde tests u otras partes.
    """
    global logger
    if settings is None:
        settings = OrbitSettings()

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Limpiar handlers previos para evitar duplicados
    if logger.hasHandlers():
        logger.handlers.clear()

    if settings.DEBUG_TO_CONSOLE or settings.INFO_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if settings.DEBUG_TO_FILE or settings.INFO_TO_FILE:
        file_handler = logging.FileHandler(settings.LOGS_DIR, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

# Inicialización por defecto al importar el módulo
configurar_logger()
