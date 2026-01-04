from abc import abstractmethod, ABC
from typing import Any, Optional


class Metadata(ABC):
    def __init__(self, path):
        self._path = path
        self._data: dict[str, Any] = {}

    @abstractmethod
    def _read_data(self) -> dict[str, Any]:
        pass

    def clear(self) -> None:
        del self._data

    def data(self) -> dict[str, Any]:
        if not self._data:
            self._data = self._read_data()
        return self._data

    def __contains__(self, name: str) -> bool:
        return name in self.data()

    @abstractmethod
    def __getitem__(self, path: str) -> Optional[Any]:
        pass
