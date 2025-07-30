from threading import Lock
from typing import Any

from pipelet.storage.abc import TempStorage


class StorageManager:
    """
    A singleton class for managing interaction with a temporary storage system.
    Ensures thread safety and provides an interface for storing, retrieving,
    and deleting data using both attribute-like and method-based access.
    """

    _instance = None
    _instance_lock = Lock()

    def __new__(cls, storage: TempStorage) -> "StorageManager":
        """
        Creates a single instance of StorageManager with thread safety.

        Args:
            storage (TempStorage): The storage backend to use.

        Returns:
            StorageManager: The singleton instance.
        """
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._storage = storage
                cls._instance._lock = Lock()
        return cls._instance

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Stores a value in the storage system using attribute-style access.

        Args:
            name (str): The key to store the value under.
            value (Any): The value to store.
        """
        if name in ("_storage", "_lock"):
            super().__setattr__(name, value)
        else:
            self.set(name, value)

    def __getattr__(self, name: str) -> Any:
        """
        Retrieves a value from the storage system using attribute-style access.

        Args:
            name (str): The key to retrieve the value for.

        Returns:
            Any: The stored value.

        Raises:
            KeyError: If the key is not found in the storage.
        """
        return self.get(name)

    def __delattr__(self, name: str) -> None:
        """
        Deletes a value from the storage system using attribute-style access.

        Args:
            name (str): The key to delete.

        Raises:
            KeyError: If the key is not found in the storage.
        """
        self.delete(name)

    def set(self, name: str, value: Any) -> None:
        """
        Stores a value in the storage system.

        Args:
            name (str): The key to store the value under.
            value (Any): The value to store.
        """
        with self._lock:
            self._storage.set(name, value)

    def get(self, name: str) -> Any:
        """
        Retrieves a value from the storage system.

        Args:
            name (str): The key to retrieve the value for.

        Returns:
            Any: The stored value.

        Raises:
            KeyError: If the key is not found in the storage.
        """
        with self._lock:
            value = self._storage.get(name)
            if value is None:
                raise KeyError(f"'{name}' not found in the storage.")
            return value

    def delete(self, name: str) -> None:
        """
        Deletes a value from the storage system.

        Args:
            name (str): The key to delete.

        Raises:
            KeyError: If the key is not found in the storage.
        """
        with self._lock:
            if self._storage.get(name) is None:
                raise KeyError(f"'{name}' not found in the storage.")
            self._storage.delete(name)
