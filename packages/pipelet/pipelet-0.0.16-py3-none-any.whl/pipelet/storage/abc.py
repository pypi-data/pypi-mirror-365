from abc import ABC, abstractmethod
from typing import Any


class TempStorage(ABC):
    """
    Abstract base class for implementing temporary data storage.
    """

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Store data in the storage.

        Args:
            key (str): The key for the data.
            value (Any): The data to be stored.
        """
        pass

    @abstractmethod
    def get(self, key: str, default_value: Any | None = None) -> Any:
        """
        Retrieve data from the storage by key.

        Args:
            key (str): The key to search for the data.

        Returns:
            Any: The retrieved data.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Remove data from the storage by key.

        Args:
            key (str): The key for the data to be removed.
        """
        pass
