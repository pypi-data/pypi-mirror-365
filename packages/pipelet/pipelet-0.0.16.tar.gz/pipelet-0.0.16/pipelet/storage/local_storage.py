from typing import Any, Dict, Hashable

from pipelet.storage.abc import TempStorage


class LocalStorage(TempStorage):
    """
    Implementation of a local storage for storing data in memory.
    """

    def __init__(self):
        self._storage: Dict[Hashable, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store data in the local storage."""
        self._storage[key] = value

    def get(self, key: str, default_value: Any | None = None) -> Any:
        """Retrieve data from the local storage."""
        return self._storage.get(key, default_value)

    def delete(self, key: str) -> None:
        """Remove data from the local storage."""
        if key in self._storage:
            del self._storage[key]
