# orbitlab/config.py
from typing import Optional, Literal
from pydantic_settings import BaseSettings

class OrbitSettings(BaseSettings):
    """
    Configuración por defecto de Orbit Lab, usada si no se detectan settings externos.
    Compatible con entornos personalizados.
    """

    PROJECT_NAME: str = "Orbit Lab"
    PUBLIC_KEY: Optional[str] = ""
    PRIVATE_KEY: Optional[str] = ""

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    DEBUG_TO_CONSOLE: Optional[bool] = True
    DEBUG_TO_FILE: Optional[bool] = False
    INFO_TO_CONSOLE: Optional[bool] = True
    INFO_TO_FILE: Optional[bool] = False
    LOGS_DIR: str = "./logs/orbitlab.log"
