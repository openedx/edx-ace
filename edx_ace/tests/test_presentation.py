u"""
Tests of :mod:`edx_ace.presentation`.
"""
from __future__ import absolute_import

from unittest import TestCase

from mock import Mock

from edx_ace.channel import ChannelType
from edx_ace.errors import UnsupportedChannelError
from edx_ace.presentation import render


class TestRender(TestCase):
    u"""
    Tests for unsupported rendering for a channel.
    """

    def test_missing_renderer(self):
        channel = Mock(
            channel_type=ChannelType.PUSH,
        )

        message = Mock()

        with self.assertRaises(UnsupportedChannelError):
            render(channel, message)
