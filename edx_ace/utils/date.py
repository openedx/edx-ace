from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc


def get_current_time():
    return datetime.now(tzutc())


def serialize(obj):
    assert isinstance(obj, datetime)

    if obj.tzinfo is not None and obj.utcoffset() is None:
        return obj.isoformat() + 'Z'
    else:
        return obj.isoformat()


def deserialize(value):
    return parse(value)
