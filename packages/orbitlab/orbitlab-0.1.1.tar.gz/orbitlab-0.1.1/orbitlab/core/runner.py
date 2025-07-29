# orbitlab/core/runner.py

import sys
import dill
import traceback
import importlib.util
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Union, cast
from io import StringIO
from orbitlab.core.validator import OrbitValidator
from orbitlab.core.cache import OrbitCache
from orbitlab.adapters.base import BaseProjectAdapter
from orbitlab.core.crypto import decrypt_hybrid, validar_firma
from orbitlab.core.mutator import global_mutator  # 🔁 Cambio clave aquí
from orbitlab.core.utils import log_message

class OrbitRunner:
    def __init__(
        self,
        path: Union[str, Path],
        external_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        mutation_filter: Optional[list[str]] = None,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = False 
    ):
        self.dill_path = Path(path)
        self.external_validator = external_validator
        self.mutation_filter = mutation_filter
        self.enable_cache = enable_cache
        self.cache = OrbitCache(cache_dir) if enable_cache and cache_dir else None

        self.adapter = BaseProjectAdapter()
        self.obj: Dict[str, Any] = {}
        self.payload: Dict[str, Any] = {}
        self.source_code: Optional[str] = None

    def run(self, method_name: Optional[str] = None, arg: Optional[str] = None):
        log_message(f"Validando firma para: {self.dill_path}", emoji="🔍")
        if not validar_firma(self.dill_path):
            log_message(f"Firma inválida o inexistente para: {self.dill_path}", emoji="🚫", level="error")
            return

        if not self.load() or not self.validate():
            return

        self.mutate()
        if not self.enable_cache:
            self._create_structure()

        if method_name:
            self._run_method(method_name, arg)
        else:
            self._run_function()

    def load(self) -> bool:
        cache_key = str(self.dill_path.resolve())
        cached = self.cache.get(cache_key, validate_hash=True) if self.cache else None
        if cached:
            self.obj = cached
            self.payload = self._extract_payload(self.obj)
            log_message("Usando caché con firma válida", emoji="📦")
            return True

        try:
            with self.dill_path.open("rb") as f:
                self.obj = cast(Dict[str, Any], dill.load(f))
            self.payload = self._extract_payload(self.obj)
            return True
        except Exception as e:
            log_message(f"Error cargando .dill: {e}", level="error")
            return False

    def _extract_payload(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        if obj.get("secure") and "encrypted" in obj:
            try:
                decrypted = decrypt_hybrid(cast(Dict[str, Any], obj["encrypted"]))
                log_message("Payload desencriptado correctamente", emoji="🔐")
                return decrypted
            except Exception as e:
                log_message(f"Error desencriptando .dill: {e}", level="error")
                return {}
        elif "payload" in obj:
            return obj["payload"]
        else:
            log_message("El .dill no contiene ni 'payload' ni 'encrypted' válidos", level="error")
            return {}

    def validate(self) -> bool:
        validator = OrbitValidator(self.dill_path, external_schema=self.external_validator)
        if not validator.run_all():
            validator.report()
            return False
        return True

    def mutate(self):
        self._load_default_mutadores()
        self.payload = global_mutator.apply(self.payload, only=self.mutation_filter)
        self.obj["payload"] = self.payload
        if self.enable_cache and self.cache:
            self.cache.set(str(self.dill_path.resolve()), self.obj)

    def _load_default_mutadores(self):
        posibles = list(Path.cwd().rglob("mutadores.py"))
        for archivo in posibles:
            modulo_path = archivo.resolve()
            nombre_modulo = ".".join(archivo.with_suffix("").parts)

            if nombre_modulo not in sys.modules:
                try:
                    spec = importlib.util.spec_from_file_location(nombre_modulo, str(modulo_path))
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules[nombre_modulo] = mod
                        spec.loader.exec_module(mod)
                except Exception as e:
                    log_message(f"No se pudo cargar mutadores desde: {archivo} — {e}", level="warning")

    def _create_structure(self):
        for carpeta in self.payload.get("folders", []):
            try:
                Path(carpeta).mkdir(parents=True, exist_ok=True)
                log_message(f"Carpeta creada: {carpeta}", emoji="📁")
            except Exception as e:
                log_message(f"Error creando carpeta {carpeta}: {e}", level="error")

        for archivo in self.payload.get("archivos", []):
            try:
                ruta = Path(archivo["path"])
                ruta.parent.mkdir(parents=True, exist_ok=True)
                ruta.write_text(archivo.get("content", ""), encoding="utf-8")
                log_message(f"Archivo creado: {archivo['path']}", emoji="📄")
            except Exception as e:
                log_message(f"Error creando {archivo}: {e}", level="error")

    def _run_function(self):
        func = self.payload.get("function")
        if func and callable(func):
            log_message("Ejecutando función serializada desde .dill...", emoji="🧠")
            try:
                result = func()
                print(f"📤 Resultado directo: {result}")
                log_message("Función ejecutada con éxito", emoji="✅")
            except Exception as e:
                log_message(f"Error al ejecutar función: {e}", level="error")
            return

        source = self.payload.get("code", "")
        if not source:
            log_message("No se encontró código fuente para ejecutar", level="info")
            return

        contexto = {"__data__": self.payload.get("data", {})}
        sys.stdout = output = StringIO()
        try:
            exec(compile(source, "<entrypoint>", "exec"), contexto)
            sys.stdout = sys.__stdout__
            captured = output.getvalue().strip()
            if captured:
                print(f"📤 [entrypoint stdout]:\n{captured}")
            log_message("Código ejecutado con éxito como script", emoji="✅")
        except Exception as e:
            sys.stdout = sys.__stdout__
            traceback.print_exc()
            log_message(f"Error ejecutando entrypoint: {e}", level="error")

    def _run_method(self, method_name: str, arg: Optional[str]):
        expose = self.payload.get("expose", {})
        class_name = expose.get("class_name")
        if not class_name:
            log_message("No se definió 'expose.class_name'", level="error")
            return

        source = self.payload.get("code", "")
        if not source:
            log_message("No se encontró código fuente", level="error")
            return

        contexto = {"__data__": self.payload.get("data", {})}
        try:
            exec(source, contexto)
            cls = contexto.get(class_name)
            if not cls:
                log_message(f"Clase '{class_name}' no encontrada", level="error")
                return

            instance = cls(contexto["__data__"])
            if hasattr(instance, method_name):
                resultado = getattr(instance, method_name)(arg) if arg else getattr(instance, method_name)()
                if resultado is not None:
                    print(f"📤 Resultado: {resultado}")
                else:
                    print(f"✅ Método '{method_name}' ejecutado con éxito.")
            else:
                log_message(f"Método '{method_name}' no encontrado", level="error")
        except Exception as e:
            traceback.print_exc()
            log_message(f"Error ejecutando método '{method_name}': {e}", level="error")

__all__ = ["OrbitRunner"]
