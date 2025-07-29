import os
import time
import uuid
import dill
from pathlib import Path
from filelock import FileLock
from typing import Any, List, Optional

from orbitlab.core.crypto import firmar_dill, validar_firma, encrypt_hybrid, decrypt_hybrid

class TrackedDict(dict):
    def __init__(self, parent=None, key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        self._key = key

    def __setitem__(self, k, v):
        if isinstance(v, dict) and not isinstance(v, TrackedDict):
            v = TrackedDict(self._parent, self._key, v)
        super().__setitem__(k, v)
        self._trigger()

    def __delitem__(self, k):
        super().__delitem__(k)
        self._trigger()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._trigger()

    def _trigger(self):
        if getattr(self, "_parent", None) and getattr(self, "_key", None):
            self._parent._store[self._key] = self
            if self._parent.auto_save:
                self._parent._save()
            self._parent._auto_commit_if_needed(self._key)

    def __getstate__(self):
        return {"_data": dict(self), "_key": self._key}

    def __setstate__(self, state):
        dict.update(self, state["_data"])
        self._key = state.get("_key")
        self._parent = None

    def __repr__(self):
        return f"TrackedDict({dict.__repr__(self)})"


def to_plain_dict(d):
    if isinstance(d, TrackedDict):
        return {k: to_plain_dict(v) for k, v in d.items()}
    elif isinstance(d, dict):
        return {k: to_plain_dict(v) for k, v in d.items()}
    return d


class DynamicDillStore:
    def __init__(self, path: str, auto_reload=True, auto_save=True, auto_commit_interval: Optional[float] = None, secure: bool = False):
        self.path = path
        self.lock = FileLock(self.path + ".lock")
        self.auto_reload = auto_reload
        self.auto_save = auto_save
        self.auto_commit_interval = auto_commit_interval
        self.secure = secure
        self._last_commit_times = {}
        self._last_mtime = None
        self._store = {}
        self._versions_path = self.path + ".versions"
        os.makedirs(self._versions_path, exist_ok=True)

        if os.path.exists(self.path):
            self._reload()
        else:
            self._save()

        if self.auto_save:
            try:
                import atexit
                atexit.register(self._save)
            except Exception:
                pass

    def _wrap_nested_dicts(self, data, key):
        if isinstance(data, dict) and not isinstance(data, TrackedDict):
            td = TrackedDict(self, key)
            for k, v in data.items():
                td[k] = self._wrap_nested_dicts(v, key)
            return td
        return data

    def _reattach_tracked_dicts(self):
        for k, v in self._store.items():
            self._store[k] = self._wrap_nested_dicts(v, k)

    def _reload(self):
        try:
            if not os.path.exists(self.path):
                return
            mtime = os.path.getmtime(self.path)
            if self._last_mtime is None or mtime > self._last_mtime:
                with self.lock:
                    with open(self.path, "rb") as f:
                        contenido = dill.load(f)
                        if isinstance(contenido, dict) and contenido.get("secure") and "encrypted" in contenido:
                            self._store = decrypt_hybrid(contenido["encrypted"])
                        else:
                            self._store = contenido
                self._last_mtime = mtime
                self._reattach_tracked_dicts()
        except Exception as e:
            print(f"[DynamicDillStore] Reload error: {e}")

    def _save(self):
        try:
            with self.lock:
                with open(self.path, "wb") as f:
                    if self.secure:
                        encrypted = encrypt_hybrid(self._store)
                        dill.dump({"secure": True, "encrypted": encrypted}, f)
                    else:
                        dill.dump(self._store, f)
                self._last_mtime = os.path.getmtime(self.path)
        except Exception as e:
            print(f"[DynamicDillStore] Save error: {e}")

    def _auto_commit_if_needed(self, key: str):
        if self.auto_commit_interval is None:
            return
        now = time.time()
        last = self._last_commit_times.get(key, 0)
        if now - last >= self.auto_commit_interval:
            self.commit(key)

    def set(self, key: str, value: Any):
        if self.auto_reload:
            self._reload()
        wrapped = self._wrap_nested_dicts(value, key)
        with self.lock:
            self._store[key] = wrapped
            if self.auto_save:
                self._save()
            self._auto_commit_if_needed(key)

    def get(self, key: str, default=None) -> Any:
        if self.auto_reload:
            self._reload()
        with self.lock:
            val = self._store.get(key, default)
            val = self._wrap_nested_dicts(val, key)
            self._store[key] = val
            return val

    def delete(self, key: str):
        if self.auto_reload:
            self._reload()
        with self.lock:
            if key in self._store:
                del self._store[key]
                if self.auto_save:
                    self._save()

    def keys(self):
        if self.auto_reload:
            self._reload()
        with self.lock:
            return list(self._store.keys())

    def values(self):
        if self.auto_reload:
            self._reload()
        with self.lock:
            return list(self._store.values())

    def items(self):
        if self.auto_reload:
            self._reload()
        with self.lock:
            return self._store.items()

    def clear(self):
        with self.lock:
            self._store = {}
            if self.auto_save:
                self._save()

    def commit(self, key: str):
        if key not in self._store:
            raise KeyError(f"Key '{key}' not found for commit")
        ts = time.strftime("%Y%m%d-%H%M%S")
        uid = uuid.uuid4().hex[:6]
        version_file = os.path.join(self._versions_path, f"{key}@{ts}_{uid}.dill")
        with open(version_file, "wb") as f:
            dill.dump(self._store[key], f)
        firmar_dill(Path(version_file))
        self._last_commit_times[key] = time.time()

    def history(self, key: str) -> List[str]:
        prefix = f"{key}@"
        return sorted(
            f.split("@", 1)[-1].replace(".dill", "")
            for f in os.listdir(self._versions_path)
            if f.startswith(prefix) and f.endswith(".dill")
        )

    def rollback(self, key: str, timestamp: str):
        matches = [f for f in os.listdir(self._versions_path) if f.startswith(f"{key}@{timestamp}") and f.endswith(".dill")]
        if not matches:
            raise FileNotFoundError(f"No version found for '{key}' at {timestamp}")
        version_file = os.path.join(self._versions_path, matches[0])
        if not validar_firma(Path(version_file)):
            raise ValueError(f"Firma inválida para la versión {matches[0]}")
        with open(version_file, "rb") as f:
            value = dill.load(f)
        self.set(key, value)

    def __repr__(self):
        return f"<DynamicDillStore path={self.path} keys={list(self._store.keys())}>"
