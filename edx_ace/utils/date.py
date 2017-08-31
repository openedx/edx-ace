
from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import tzutc


def get_current_time():
    return datetime.now(tzutc())


def serialize(obj):
    # TODO(later): my understanding is that type checks like this are not pythonic.
    assert isinstance(obj, datetime)

    # TODO(later): what if utcoffset() returns 0?
    if obj.tzinfo is not None and obj.utcoffset() is None:
        return obj.isoformat() + 'Z'
    else:
        return obj.isoformat()


def deserialize(value):
    if value is None:
        return None
    return parse(value, yearfirst=True)
