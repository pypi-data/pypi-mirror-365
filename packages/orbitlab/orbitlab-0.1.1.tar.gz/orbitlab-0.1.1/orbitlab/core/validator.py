# orbitlab/core/validator.py

import dill # type: ignore
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List, Union
from orbitlab.core.crypto import decrypt_hybrid, validar_firma
from orbitlab.core.utils import log_message

class OrbitValidator:
    """
    Valida un archivo .dill asegurando:
    - Firma válida.
    - Correcta deserialización.
    - Presencia de claves estándar de Orbit: folders, archivos, code.
    - Validación externa opcional.
    """

    def __init__(
        self,
        dill_path: Union[str, Path],
        external_schema: Optional[Callable[[Dict[str, Any]], bool]] = None
    ):
        self.dill_path = Path(dill_path)
        self.external_schema = external_schema
        self.errors: List[str] = []
        self.payload: Dict[str, Any] = {}

    def validate_firma(self) -> bool:
        if not validar_firma(self.dill_path):
            self.errors.append(f"❌ Firma inválida o no encontrada para {self.dill_path}")
            return False
        log_message(f"Firma válida confirmada", emoji="🔏")
        return True

    def validate_estructura(self) -> bool:
        try:
            with self.dill_path.open("rb") as f:
                data = dill.load(f) # type: ignore
        except Exception as e:
            self.errors.append(f"❌ Error al deserializar .dill: {e}")
            return False

        if not isinstance(data, dict):
            self.errors.append("❌ El contenido no es un diccionario.")
            return False

        if data.get("secure") and "encrypted" in data: # type: ignore
            log_message("Contenido cifrado detectado. Intentando desencriptar...", emoji="🔐")
            try:
                self.payload = decrypt_hybrid(data["encrypted"]) # type: ignore
                log_message("Contenido desencriptado exitosamente", emoji="✅")
            except Exception as e:
                self.errors.append(f"❌ Error desencriptando: {e}")
                return False
        elif "payload" in data:
            self.payload = data["payload"]
        else:
            self.errors.append("❌ No se encontró clave 'payload' o 'encrypted'.")
            return False

        for key in ["folders", "archivos", "code"]:
            if key not in self.payload: # type: ignore
                self.errors.append(f"❌ Falta la clave obligatoria: {key}")

        return not self.errors

    def validate_externo(self) -> bool:
        if self.external_schema:
            log_message("Ejecutando validador externo...", emoji="🧪")
            try:
                if not self.external_schema(self.payload):
                    self.errors.append("❌ Validador externo retornó False.")
                    return False
            except Exception as e:
                self.errors.append(f"❌ Excepción en validador externo: {e}")
                return False
        return True

    def run_all(self) -> bool:
        log_message(f"Validando archivo: {self.dill_path}", emoji="📍")
        if not self.dill_path.exists():
            self.errors.append(f"❌ Archivo no encontrado: {self.dill_path}")
            return False
        return (
            self.validate_firma()
            and self.validate_estructura()
            and self.validate_externo()
        )

    def report(self) -> None:
        if self.errors:
            for error in self.errors:
                log_message(error, level="error")
        else:
            log_message("Validación completada sin errores", emoji="✅")

__all__ = ["OrbitValidator"]
