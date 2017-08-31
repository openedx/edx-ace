
from datetime import datetime
from unittest import TestCase

from hypothesis import strategies as st
from hypothesis import example, given
from hypothesis.extra.pytz import timezones

from edx_ace.utils.date import deserialize, serialize


class TestDateSerialization(TestCase):

    @given(st.datetimes(timezones=st.none() | timezones()))
    @example(datetime(16, 1, 1, 0, 0, 16))
    def test_round_trip(self, d):
        serialized = serialize(d)
        parsed = deserialize(serialized)
        self.assertEqual(d, parsed)
