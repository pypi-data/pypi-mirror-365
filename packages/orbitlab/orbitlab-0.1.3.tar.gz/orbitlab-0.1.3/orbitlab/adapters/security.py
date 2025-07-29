# orbitlab/adapters/security.py

from typing import Dict, Any, cast
from Crypto.PublicKey import RSA
from orbitlab.adapters.base import BaseProjectAdapter
from cross_crypto_py.encrypt import encryptHybrid  # type: ignore
from cross_crypto_py.decrypt import decryptHybrid  # type: ignore
from orbitlab.core.utils import log_message


class HybridSecurityAdapter(BaseProjectAdapter):
    """
    Adaptador de cifrado híbrido usando cross-crypto.
    Utiliza claves desde settings heredados (PUBLIC_KEY, PRIVATE_KEY).
    """

    def encrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        key = getattr(self.settings, "PUBLIC_KEY", None)
        if not key:
            raise ValueError("🔐 Clave pública no encontrada en settings")

        log_message(f"🔐 [encrypt] Clave pública: {key[:40]}...", scope="encrypt", level="debug")
        try:
            return cast(Dict[str, Any], encryptHybrid(data, key, mode="dill"))
        except Exception as e:
            log_message(f"Error en encryptHybrid: {e}", scope="encrypt", level="error")
            raise

    def decrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        key = getattr(self.settings, "PRIVATE_KEY", None)
        if not key:
            raise ValueError("🔐 Clave privada no encontrada en settings")

        log_message(f"🔓 [decrypt] Clave privada: {key[:40]}...", scope="decrypt", level="debug")
        try:
            return cast(Dict[str, Any], decryptHybrid(data, key, mode="dill"))
        except Exception as e:
            log_message(f"Error en decryptHybrid: {e}", scope="decrypt", level="error")
            raise

    def public_key(self) -> RSA.RsaKey:
        key = getattr(self.settings, "PUBLIC_KEY", None)
        if not key:
            raise ValueError("Clave pública no encontrada para import_key()")
        try:
            return RSA.import_key(key)
        except Exception as e:
            raise ValueError(f"Error al cargar la clave pública: {e}")

    def private_key(self) -> RSA.RsaKey:
        key = getattr(self.settings, "PRIVATE_KEY", None)
        if not key:
            raise ValueError("Clave privada no encontrada para import_key()")
        try:
            return RSA.import_key(key)
        except Exception as e:
            raise ValueError(f"Error al cargar la clave privada: {e}")
