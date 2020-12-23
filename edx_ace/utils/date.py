"""
:mod:`edx_ace.utils.date` contains utility functions used for
serializing and deserializing dates. It is intended for internal ACE
use.
"""
from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import tzutc


def get_current_time():
    """The current time in the UTC timezone as a timezone-aware datetime object."""
    return datetime.now(tzutc())


def serialize(timestamp_obj):
    """
    Serialize a datetime object to an ISO8601 formatted string.

    Args:
        timestamp_obj (datetime): The timestamp to serialize.

    Returns:
        basestring: A string representation of the timestamp in ISO8601 format.
    """
    if timestamp_obj is None:
        return None

    # TODO(later): my understanding is that type checks like this are not pythonic.
    assert isinstance(timestamp_obj, datetime)

    # TODO(later): what if utcoffset() returns 0?
    if timestamp_obj.tzinfo is not None and timestamp_obj.utcoffset() is None:
        return timestamp_obj.isoformat() + 'Z'
    else:
        return timestamp_obj.isoformat()


def deserialize(timestamp_iso8601_str):
    """
    Deserialize a datetime object from an ISO8601 formatted string.

    Args:
        timestamp_iso8601_str (basestring): A timestamp as an ISO8601 formatted string.

    Returns:
        datetime: A timezone-aware python datetime object.
    """
    if timestamp_iso8601_str is None:
        return None
    return parse(timestamp_iso8601_str, yearfirst=True)
