import sched
from abc import abstractmethod, ABC
from threading import Thread
from time import sleep, time
from typing import Any, Optional


class CacheableData(ABC):
    def __init__(self):
        self._data_cache: dict[str, Any] = {}

    @abstractmethod
    def _read_data(self) -> dict[str, Any]:
        raise NotImplementedError('Please Implement this method')

    def clear(self) -> None:
        del self._data_cache

    def data(self) -> dict[str, Any]:
        if not self._data_cache:
            self._data_cache = self._read_data()
            scheduler = sched.scheduler(time, sleep)
            scheduler.enter(5 * 60, 0, lambda: self.clear(), ())
            Thread(target=scheduler.run).start()
        return self._data_cache

    def __contains__(self, name: str) -> bool:
        return name in self.data()

    @abstractmethod
    def __getitem__(self, path: str) -> Optional[Any]:
        pass
