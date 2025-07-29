# OrbitLab 🛰️

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/) [![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](LICENSE) [![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen.svg)]() [![Made with ♥](https://img.shields.io/badge/made%20with-%E2%99%A5-red.svg)]()

**Orbit Lab** es un motor avanzado para la ejecución segura de estructuras **.dill** en **Python**. Integra validación estructural, ejecución dinámica de funciones y clases, transformación del payload mediante mutaciones encadenadas, cacheo inteligente, cifrado híbrido (RSA + AES), firma digital, y un sistema de almacenamiento con versionado y rollback automático.

---

## 🚀 Características principales

- ✅ **Runner dinámico** para ejecutar funciones, clases o scripts desde `.dill`.
- 🔧 **Sistema de mutadores** encadenables para transformar payloads fácilmente.
- 🧠 **Validador estructural** extensible para asegurar integridad del payload.
- 🛡️ **Cifrado híbrido (RSA + AES)** con firmas digitales para máxima seguridad.
- 🧬 **Almacenamiento versiónado** vía `DynamicDillStore` con rollback.
- ♻️ **Cacheo inteligente** basado en hash para acelerar cargas repetidas.

---

## 📦 Estructura del Proyecto

```
📦orbitlab/
├── LICENSE
├── README.md
├── orbitlab/
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── security.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── crypto.py
│   │   ├── dynamic_store.py
│   │   ├── mutator.py
│   │   ├── registry.py
│   │   ├── runner.py
│   │   ├── utils.py
│   │   └── validator.py
│   └── logger.py
└── pyproject.toml
```

---

## 🧩 Componentes

| Módulo                  | Descripción |
|--------------------------|-------------|
| `orbit.core.runner`      | Ejecuta `.dill` como scripts, funciones o clases. |
| `orbit.core.mutator`     | Registra y aplica transformaciones al payload. |
| `orbit.core.validator`   | Valida estructura del `.dill` antes de ejecutar. |
| `orbit.core.crypto`      | Firma digital y cifrado híbrido. |
| `orbit.core.dynamic_store` | Almacenamiento tipo base de datos con rollback/versionado. |
| `orbit.core.cache`       | Mecanismo de cacheo basado en hash. |
| `orbit.core.registry`       | Registro de versiones .dill con metadatos como autor, hash, timestamp y etiquetas. |
| `orbit.core.validator`       | Valida firmas, claves mínimas del payload, y soporta validadores externos. |

---

## 🔐 Seguridad

- ✍️ Firmas digitales (`.dill.sig`)
- 📦 Validación automática de integridad
- 🔐 Desencriptado híbrido usando `cross-crypto-py`
- 🚫 Bloqueo de ejecución si el archivo fue alterado


---

## 🧩 Ejemplos de uso con `OrbitRunner`

### `Ejemplo 1`
```python
import dill
from pathlib import Path
from orbit.core.crypto import firmar_dill
from orbit.core.runner import OrbitRunner

print("🚀 Test 0: Ejecución de función serializada con OrbitRunner")

ruta = Path("mi_modelo.dill")

def hola_mundo():
    return "👋 Hola desde OrbitRunner"

payload = {
    "payload": {
        "function": hola_mundo,
        "folders": [],
        "archivos": [],
        "code": "",  
    }
}

with ruta.open("wb") as f:
    dill.dump(payload, f)

firmar_dill(ruta)

runner = OrbitRunner(str(ruta))
runner.run()
print("✅ Test 0 finalizado con ejecución directa exitosa")
```

### `Ejemplo 2 con una clase y mutaciones`
```python
import dill
from pathlib import Path
from orbit.core.crypto import firmar_dill
from orbit.core.runner import OrbitRunner, global_mutator

print("🔧 Test 0C: Clase + método + mutaciones encadenadas")

@global_mutator.register("inject_data")
def inject_data(payload):
    print("🔧 inject_data aplicado")
    payload.setdefault("data", {})["quien"] = "mutado"
    return payload

@global_mutator.register("normalize_data")
def normalize_data(payload):
    print("🔧 normalize_data aplicado")
    if "quien" in payload.get("data", {}):
        payload["data"]["quien"] = payload["data"]["quien"].capitalize()
    return payload

codigo = """
class Saludo:
    def __init__(self, data):
        self.quien = data.get("quien", "nadie")

    def saludo(self):
        return f"🌟 Hola desde mutación, {self.quien}!"
"""

ruta = Path("mi_modelo_mutado.dill")
payload = {
    "payload": {
        "code": codigo,
        "data": {},
        "expose": {
            "class_name": "Saludo",
            "methods": [{"name": "saludo"}]
        },
        "folders": [],
        "archivos": [],
    }
}

with ruta.open("wb") as f:
    dill.dump(payload, f)
firmar_dill(ruta)

runner = OrbitRunner(str(ruta), mutation_filter=["inject_data", "normalize_data"])
runner.run("saludo")
print("✅ Test 0C finalizado con mutaciones aplicadas antes de ejecutar método")
```

### `Ejemplo 3 con una clase y mutaciones y encriptación`
```python
import dill
from pathlib import Path
from cross_crypto_py.keygen import generateRSAKeys
from orbit.core.crypto import encrypt_hybrid, firmar_dill, _adapter
from orbit.core.runner import OrbitRunner, global_mutator
from orbit.config import OrbitSettings

print("🔐 Test 0D: Clase + mutaciones + ejecución desde .dill cifrado")

keys = generateRSAKeys()
_adapter.settings = OrbitSettings(
    PUBLIC_KEY=keys["publicKey"],
    PRIVATE_KEY=keys["privateKey"]
)

code = """
class Usuario:
    def __init__(self, data):
        self.nombre = data.get("nombre", "anon")

    def saluda(self):
        return f"👋 ¡Hola desde archivo cifrado, {self.nombre}!"
"""

payload = {
    "code": code,
    "data": {},
    "expose": {
        "class_name": "Usuario",
        "methods": [{"name": "saluda"}]
    },
    "folders": [],
    "archivos": []
}

encrypted_payload = {
    "secure": True,
    "encrypted": encrypt_hybrid(payload)
}

ruta = Path("test_0D_secure/entrada/mi_modelo_cifrado.dill")
ruta.parent.mkdir(parents=True, exist_ok=True)
with ruta.open("wb") as f:
    dill.dump(encrypted_payload, f)
firmar_dill(ruta)

@global_mutator.register("inject_name")
def inject_name(payload):
    print("🔧 inject_name aplicado")
    payload.setdefault("data", {})["nombre"] = "Zerina"
    return payload

@global_mutator.register("to_uppercase")
def to_uppercase(payload):
    print("🔧 to_uppercase aplicado")
    if "data" in payload and "nombre" in payload["data"]:
        payload["data"]["nombre"] = payload["data"]["nombre"].upper()
    return payload

print("🚀 Ejecutando OrbitRunner sobre archivo cifrado con mutaciones...")
runner = OrbitRunner(str(ruta), mutation_filter=["inject_name", "to_uppercase"])
runner.run(method_name="saluda")
print("✅ Test 0D completado con cifrado, mutaciones y ejecución de clase")
```


---

## 🧠 Uso con DynamicDillStore

```python
from orbit.core.dynamic_store import DynamicDillStore

store = DynamicDillStore("config.dill", auto_commit_interval=2.0)
store.set("params", {"lr": 0.01, "arch": [64, 128]})
store.commit("params")
```

---

## 📁 Formato esperado del `.dill`

```python
{
  "payload": {
    "code": "...",  # Código fuente
    "function": ...,  # (opcional) función serializada
    "data": {...},    # diccionario con datos
    "expose": {
      "class_name": "MyClass",
      "methods": [{"name": "do"}]
    },
    "folders": [],
    "archivos": []
  }
}
```

---

## ⚙️ Requisitos

- Python 3.10+
- `dill`, `filelock`, `cross-crypto-py`, `pydantic-settings`

---

## 🪪 Licencia

BSD 3-Clause License © 2025 Jose Fabian Soltero Escobar