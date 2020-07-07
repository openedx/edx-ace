"""
Tests of :mod:`edx_ace.utils.date`.
"""
from datetime import datetime
from unittest import TestCase

from hypothesis import example, given
from hypothesis import strategies as st
from hypothesis.extra.pytz import timezones

from edx_ace.utils.date import deserialize, serialize


class TestDateSerialization(TestCase):
    """ Test Date Serialization. """
    @given(st.one_of(st.datetimes(timezones=st.none() | timezones()), st.none()))
    @example(datetime(16, 1, 1, 0, 0, 16))
    def test_round_trip(self, date):
        serialized = serialize(date)
        parsed = deserialize(serialized)
        self.assertEqual(date, parsed)
