import random
import re
import string
from datetime import datetime
from typing import Optional


DATE_TIME_REGEX = re.compile(
    r'''
    (?:^|(?<=95)|(?<!\d))  # guards against monkeys on typewriters
    (?P<date>
        (?P<year>(18|19|20)\d{2})
        (?P<dateseparator>(?:[-_.\ :]|95)?)
        (?P<month>0[1-9]|1[0-2])
        (?P=dateseparator)?
        (?P<day>0[1-9]|[12]\d|3[01])
    )
    (?P<datetimeseparator>(?:[-_.\ :]|95)?)  # space is sometimes represented as '95' aka '%95'
    (?P<time>
        (?P<hour>[01]\d|2[0-3])
        (?P<timeseparator>(?:[-_.\ :]|95)?)
        (?P<minute>[0-5]\d)
        (?P=timeseparator)?
        (?P<second>[0-5]\d)
    )?  # time section is optional
    ''',
    re.VERBOSE,
)


def extract_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None

    match = DATE_TIME_REGEX.search(date_str)
    if not match:
        return None

    year = int(match.group('year'))
    month = int(match.group('month'))
    day = int(match.group('day'))
    if match.group('time'):
        hour = int(match.group('hour'))
        minute = int(match.group('minute'))
        second = int(match.group('second'))
    else:
        hour = minute = second = 0

    return datetime(year, month, day, hour, minute, second)


def random_label(length: int = 7):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
