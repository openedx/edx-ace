from datetime import datetime
from unittest import TestCase
from hypothesis import strategies as st
from hypothesis import given, example
from hypothesis.extra.pytz import timezones
import pytz

from edx_ace.utils.date import serialize, deserialize

class TestDateSerialization(TestCase):

    @given(st.datetimes(timezones=st.none() | timezones()))
    @example(datetime(16, 1, 1, 0, 0, 16))
    def test_roundtrip(self, d):
        serialized = serialize(d)
        parsed = deserialize(serialized)
        self.assertEqual(d, parsed)
