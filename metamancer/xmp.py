from typing import Optional

from metamancer.metadata import Metadata


class XMP(Metadata):
    def _read_data(self) -> dict[str, bytes]:
        with open(self._path, 'rb') as fh:
            raw = fh.read()
            xmp_start = raw.find(b'<x:xmpmeta')
            xmp_end = raw.find(b'</x:xmpmeta')
            xmp = raw[xmp_start:xmp_end+12]
            return {'raw xmp': xmp}

    def __getitem__(self, name: str) -> Optional[str]:
        return self.data()[name] if name in self else None
