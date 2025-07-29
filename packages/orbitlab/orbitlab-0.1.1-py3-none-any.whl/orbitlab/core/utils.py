# orbitlab/core/utils.py

import inspect
from pathlib import Path
from threading import Lock
from collections import defaultdict
from typing import Any, Optional, Literal, Dict

try:
    from orbitlab.logger import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("orbit")

LogLevel = Literal["info", "debug", "warning", "error", "critical"]

class ScopedAtomicCounter:
    def __init__(self) -> None:
        self._lock: Lock = Lock()
        self._counters: Dict[str, int] = defaultdict(int)

    def increment(self, scope: str = "global") -> int:
        with self._lock:
            self._counters[scope] += 1
            return self._counters[scope]

counter = ScopedAtomicCounter()

def log_message(
    message: Optional[str] = None,
    emoji: str = "🛰️",
    scope: str = "orbit",
    level: LogLevel = "info",
    **variables: Any
) -> None:
    count = counter.increment(scope)
    frame = inspect.currentframe()
    caller = frame.f_back if frame else None
    line = caller.f_lineno if caller else "?"
    file_path = Path(caller.f_code.co_filename).resolve() if caller else Path("?")
    try:
        relative_path = file_path.relative_to(Path.cwd().resolve())
    except ValueError:
        relative_path = file_path
    path = str(relative_path)

    header = f"{emoji} {count} [{scope}]"
    details = f" || Línea: {line}, Archivo: {path}"
    vars_string = " ".join(f"{k}={v}" for k, v in variables.items())
    full_message = f"{header} {message or ''}{details} {vars_string}".strip()

    getattr(logger, level)(full_message)
