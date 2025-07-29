# orbitlab/core/crypto.py

import json
import hashlib
import bcrypt
from pathlib import Path
from typing import Dict, Any
from Crypto.PublicKey import RSA
from orbitlab.adapters.security import HybridSecurityAdapter

# Instancia local del adaptador
_adapter = HybridSecurityAdapter()

def firmar_dill(dill_path: Path, hash_algoritmo: str = "blake2b") -> Path:
    """
    Genera una firma .sig basada en el hash del archivo .dill.
    """
    hash_func = getattr(hashlib, hash_algoritmo, hashlib.blake2b)
    contenido = dill_path.read_bytes()
    hash_val = hash_func(contenido).hexdigest()
    firma = {
        "file": dill_path.name,
        "hash": f"{hash_algoritmo}:{hash_val}"
    }
    sig_path = dill_path.with_suffix(".dill.sig")
    sig_path.write_text(json.dumps(firma, indent=2), encoding="utf-8")
    return sig_path

def validar_firma(dill_path: Path) -> bool:
    """
    Verifica la integridad de un archivo .dill usando su .sig asociado.
    """
    sig_path = dill_path.with_suffix(".dill.sig")
    if not sig_path.exists():
        return False

    try:
        firma = json.loads(sig_path.read_text(encoding="utf-8"))
        algoritmo, valor_firma = firma["hash"].split(":", 1)
        hash_func = getattr(hashlib, algoritmo, hashlib.blake2b)
        contenido = dill_path.read_bytes()
        hash_calculado = hash_func(contenido).hexdigest()
        return hash_calculado == valor_firma
    except Exception:
        return False

def encrypt_hybrid(data: Dict[str, Any]) -> Dict[str, Any]:
    return _adapter.encrypt(data)

def decrypt_hybrid(data: Dict[str, Any]) -> Dict[str, Any]:
    return _adapter.decrypt(data)

def load_public_key() -> RSA.RsaKey:
    return _adapter.public_key()

def load_private_key() -> RSA.RsaKey:
    return _adapter.private_key()

def hash_text(password: str, encoding: str = "utf-8") -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(encoding), salt).decode(encoding)

def verify_hash_text(text: str, hashed: str, encoding: str = "utf-8") -> bool:
    return bcrypt.checkpw(text.encode(encoding), hashed.encode(encoding))
