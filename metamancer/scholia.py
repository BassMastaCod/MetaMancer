from datetime import datetime
from typing import Any, Optional

from piexif import ImageIFD

from metamancer.apparatus import extract_date
from metamancer.exif_base import Exif
from metamancer.iptc import IPTC
from metamancer.xmp import XMP


gps = {
    'lat': {
        'num': 'GPS.GPSLatitude',
        'ref': 'GPS.GPSLatitudeRef',
        'neg': 'S'
    },
    'lng': {
        'num': 'GPS.GPSLongitude',
        'ref': 'GPS.GPSLongitudeRef',
        'neg': 'W'
    }
}


class Scholia:
    def __init__(self, path):
        self.exif = Exif(path)
        self.iptc = IPTC(path)
        self.xmp = XMP(path)

    def data(self) -> dict[str, Any]:
        data = self.exif.data()
        data.update(self.iptc.data())
        data.update(self.xmp.data())
        return data

    def __contains__(self, name: str) -> bool:
        if name.startswith('IPTC'):
            return name in self.iptc
        else:
            return name in self.exif

    def __getitem__(self, name: str) -> Any:
        if name.startswith('IPTC'):
            return self.iptc[name]
        else:
            return self.exif[name]

    @property
    def date(self) -> Optional[datetime]:
        return extract_date(self['Exif.DateTimeOriginal'])

    @date.setter
    def date(self, date_taken: datetime) -> None:
        self['Exif.DateTimeOriginal'] = date_taken.strftime('%Y:%m:%d %H:%M:%S')

    def earliest_recorded_date(self) -> Optional[datetime]:
        dates = set()
        for field in ['Exif.DateTimeOriginal', 'Image.DateTimeOriginal', 'Exif.DateTimeDigitized',  # 'XMP.DateCreated',
                      'IPTC.DateCreated', 'Exif.CreateDate', 'Image.DateTime', 'Exif.ModifyDate']:
            dates.add(extract_date(self[field]))
        dates.discard(None)
        return min(date for date in dates) if dates else None

    @property
    def did_flash(self) -> bool:
        return ((self['Exif.Flash'] or 0) & 1) != 0

    def has_location(self) -> bool:
        return ('GPS.GPSLatitude' in self and 'GPS.GPSLatitudeRef' in self
                and 'GPS.GPSLongitude' in self and 'GPS.GPSLongitudeRef' in self)

    def get_gps_url(self) -> str:
        latitude, longitude = self.get_gps_coords()
        location = f'{latitude},{longitude}'
        return f'https://www.google.com/maps/@{location},17z?q={location}'

    def get_gps_coords(self) -> tuple[float, float]:
        coords = {}
        for measurement in ('lat', 'lng'):
            coords[measurement] = self[gps[measurement]['num']]
            if self[gps[measurement]['ref']] == gps[measurement]['neg']:
                coords[measurement] = -coords[measurement]
        return coords['lat'], coords['lng']

    @property
    def speed(self) -> Optional[str]:
        speed = self['GPS.GPSSpeed']
        ref = self['GPS.GPSSpeedRef']
        if ref == 'K':
            speed = speed * 0.6214
        elif ref == 'N':
            speed = speed * 1.150779
        elif ref == 'M':
            speed = speed
        elif ref is None:
            return None

        speed = speed * 4
        return str(int(speed)) + ' mph'

    def has_direction(self) -> bool:
        return 'GPS GPSDestBearing' in self

    @property
    def direction(self) -> str:
        direction = self['GPS.GPSDestBearing']
        return f'display: inline-block; transform: rotate({int(direction)}deg)' if direction else 'display: none'

    @property
    def title(self) -> Optional[str]:
        title = None
        for name in ['Image.ImageDescription', 'Image.XPTitle', 'Exif.ImageTitle']:
            value = self[name]
            if value:
                title = value if not title else title + '{' + value + '}'
        return title

    @title.setter
    def title(self, title: str):
        self.exif.set_title(title)
        # EXIF: ImageDescription
        # EXIF: XPTitle
        # IPTC: Caption - Abstract
        # XMP - dc: Description
        # XMP - dc: Title

    @property
    def subject(self) -> str:
        return self['Image.XPSubject']

    @subject.setter
    def subject(self, subject: str):
        # EXIF:XPSubject
        pass

    @property
    def rating(self) -> int:
        return self['Image.Rating']
        # return self.get_tag_value('Image RatingPercent')

    @rating.setter
    def rating(self, value: int):
        # EXIF:Rating
        # EXIF:RatingPercent
        # XMP-microsoft:RatingPercent
        # XMP-xmp:Rating
        pass

    @property
    def keywords(self) -> set[str]:
        keywords = set()
        keywords_str = self['Image.XPKeywords']
        if keywords_str:
            keywords.update(keywords_str.split(';'))
        keywords_list = self['IPTC Keywords']
        if keywords_list:
            keywords.update(keywords_list)
        return keywords

    def add_keyword(self, *to_add: str):
        keywords = self.keywords
        modified = False
        for keyword in to_add:
            if keyword not in keywords:
                keywords.add(keyword)
                modified = True
        if modified:
            self.keywords = keywords

    @keywords.setter
    def keywords(self, keywords: list[str]):
        self.exif.set({ImageIFD.XPKeywords: ';'.join(keywords)})

    @property
    def comments(self) -> Optional[str]:
        for name in ['Image.XPComment', 'Exif.UserComment']:
            value = self[name]
            if value:
                return value
        return None

    @property
    def camera(self) -> Optional[str]:
        make = self['Image.Make']
        model = self['Image.Model']
        return f'{make} {model}' if make and model else None

    @property
    def photographer(self) -> Optional[str]:
        for name in ['Image.Artist', 'Image.XPAuthor', 'Exif.CameraOwnerName', 'Exif.Photographer']:
            value = self[name]
            if value:
                return value
        return None

    @photographer.setter
    def photographer(self, photographer: str):
        # EXIF:Artist
        # EXIF:XPAuthor
        # IPTC:By-line
        # XMP-dc:Creator
        pass

    def set_faces(self):
        pass

    def set_source(self):
        pass

    @property
    def og_image(self) -> str:
        return self['Image.ReelName']
        # return self.get_tag_value('Image ImageID')

    @property
    def sequence(self) -> int:
        return self['Image.ImageNumber']

    @property
    def location(self) -> str:
        pass

    @location.setter
    def location(self, value: str):
        pass

    @property
    def profile_group(self) -> str:
        return self['Image.ProfileGroupName']

    @property
    def motion_file(self) -> str:
        return self['Exif.RelatedSoundFile']

    @property
    def image_uid(self) -> str:
        # hash of image bytes (excluding metadata)
        return self['Exif.ImageUniqueID']

    @image_uid.setter
    def image_uid(self, value: str):
        # EXIF:ImageUniqueID
        pass

    @property
    def software(self) -> str:
        return self['Exif.MetadataEditingSoftware']
        # return self.get_tag_value('Photo ImageEditingSoftware')

    def set(self, tags: dict[int, str]):
        self.exif.set(tags)

    def compare(self, other) -> dict[str, tuple]:
        ignore = ['Interop.InteroperabilityOffset', 'Thumbnail.JPEGInterchangeFormat', 'Image.ExifOffset']
        diff = {}
        for name in self.data() | other.data():
            if name not in ignore:
                value = self[name]
                other_value = other[name]
                if value != other_value:
                    diff[name] = (value, other_value)
        return diff
