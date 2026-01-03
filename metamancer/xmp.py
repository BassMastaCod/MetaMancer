from typing import Optional

from cacheable_data import CacheableData


class XMP(CacheableData):
    def __init__(self, path):
        super().__init__()
        self._path = path

    def _read_data(self) -> dict[str, bytes]:
        with open(self._path, 'rb') as fh:
            raw = fh.read()
            xmp_start = raw.find(b'<x:xmpmeta')
            xmp_end = raw.find(b'</x:xmpmeta')
            xmp = raw[xmp_start:xmp_end+12]
            return {'raw xmp': xmp}

    def __getitem__(self, name: str) -> Optional[str]:
        return self.data()[name] if name in self else None
