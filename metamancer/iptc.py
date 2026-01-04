from typing import Optional, Union

from iptcinfo3 import IPTCInfo, IPTCData

from metamancer.metadata import Metadata


class IPTC(Metadata):
    def _read_data(self) -> dict[str, Union[str, list[str]]]:
        info = {}
        for k, v in IPTCInfo(self._path)._data.items():
            info['IPTC ' + IPTCData._key_as_str(k)] = v
        return info

    def __getitem__(self, name: str) -> Optional[Union[str, list[str]]]:
        return self.data()[name] if name in self else None
