# orbitlab/core/mutator.py

from typing import Callable, Dict, Any, Optional

class OrbitMutator:
    def __init__(self):
        self._mutators: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register(self, name: str):
        def wrapper(fn: Callable[[Dict[str, Any]], Dict[str, Any]]):
            if not callable(fn):
                raise ValueError(f"El mutador '{name}' no es una función válida.")
            self._mutators[name] = fn
            return fn
        return wrapper

    def apply(self, data: Dict[str, Any], only: Optional[list[str]] = None):
        if not isinstance(data, dict):
            raise TypeError("El objeto a mutar debe ser un diccionario.")
        for name, fn in self._mutators.items():
            if only and name not in only:
                continue
            try:
                data = fn(data)
            except Exception as e:
                raise RuntimeError(f"Error aplicando mutador '{name}': {e}")
        return data

# ✅ Objeto único compartido por todo Orbit
global_mutator = OrbitMutator()

__all__ = ["OrbitMutator", "global_mutator"]
