import io
from typing import Optional, Union

import piexif
from PIL import Image
from PIL.Image import Transpose
from piexif import TYPES

from cacheable_data import CacheableData


class Exif(CacheableData):
    def __init__(self, path):
        super().__init__()
        self._path = path

    def _read_data(self) -> dict[str, Optional[Union[dict, bytes]]]:
        return piexif.load(str(self._path))

    def __contains__(self, path: str) -> bool:
        ifd, tag = split(path)
        return ifd in self.data() and tag in self.data()[ifd]

    def __getitem__(self, path: str) -> Optional[Union[list, str, int, float]]:
        if path in self:
            ifd, tag = split(path)
            value = self.data()[ifd][tag]
            data_type = get_type(ifd, tag)
            if data_type == TYPES.Byte:
                encoding = 'utf-16le' if tag in (40091, 40092, 40093, 40094, 40095) else 'utf-8'
                return value.decode(encoding)
            elif data_type == TYPES.Ascii:
                return value.decode('ascii').rstrip('\x00')
            elif data_type == TYPES.Short:
                return int(value)
            elif data_type == TYPES.Rational:
                degrees_fraction, minutes_fraction, seconds_fraction = value
                degrees_num, degrees_den = degrees_fraction
                degrees = degrees_num / degrees_den
                minutes_num, minutes_den = minutes_fraction
                minutes = minutes_num / minutes_den
                seconds_num, seconds_den = seconds_fraction
                seconds = seconds_num / seconds_den
                return degrees + minutes / 60 + seconds / 3600
            else:
                raise NotImplementedError(f'Failed to fetch tag {path}: data type {data_type} is not yet supported')

        return None

    def has_thumbnail(self) -> bool:
        return self.data()['thumbnail'] is not None

    def get_thumbnail(self) -> bytes:
        orientation = self['Image.Orientation']
        buf = io.BytesIO()
        with Image.open(io.BytesIO(self.data()['thumbnail'])) as thumb:
            if orientation == 3:
                thumb = thumb.transpose(Transpose.ROTATE_180)
            elif orientation == 4:
                thumb = thumb.transpose(Transpose.FLIP_TOP_BOTTOM)
            elif orientation == 6:
                thumb = thumb.transpose(Transpose.ROTATE_270)
            elif orientation == 8:
                thumb = thumb.transpose(Transpose.ROTATE_90)
            thumb.save(buf, format='JPEG')
        return buf.getvalue()

    def set(self, tags: dict[int, str]):
        exif_dict = piexif.load(self._path)
        #for key, value in tags.items():
        #    if key in (40091, 40092, 40093, 40094, 40095):
        #        value = value.encode('utf-16le')
        #    exif_dict['0th'][key] = value
        #exif_dict['Exif'][42044] = 'Photos Photos'
        #piexif.insert(piexif.dump(exif_dict), self._path)
        piexif.insert(piexif.dump(exif_dict), 'Z:/test/keep/frank.jpg')
        piexif.transplant(self._path, 'Z:/test/keep/frank.jpg')
        self.clear()


def split(path: str) -> (str, int):
    ifd, name = path.split('.', 2)
    if ifd == 'Image':
        ifd = '0th'
    tag = -1
    for k, v in piexif.TAGS[ifd].items():
        if v['name'] == name:
            tag = k
            break
    return ifd, tag


def get_type(ifd: str, tag: int) -> int:
    return piexif.TAGS[ifd][tag]['type']


def add_tag(index: int, path: str, data_type: piexif.TYPES) -> None:
    ifd, tag = path.split('.', 2)
    piexif.TAGS[ifd][index] = {'name': tag, 'type': data_type}


#add_tag(42044, 'Exif.MetadataEditingSoftware', piexif.TYPES.Ascii)
