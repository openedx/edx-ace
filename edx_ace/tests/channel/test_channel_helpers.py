u"""
Tests of :mod:`edx_ace.channel`.
"""
from __future__ import absolute_import

from mock import patch

from django.test import TestCase, override_settings

from edx_ace.channel import ChannelMap, ChannelType, get_channel_for_message
from edx_ace.channel.file import FileEmailChannel
from edx_ace.channel.sailthru import SailthruEmailChannel
from edx_ace.errors import UnsupportedChannelError
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.utils.date import get_current_time


class TestChannelMap(TestCase):
    u"""
    Tests for the channels().
    """

    def setUp(self):
        self.msg_kwargs = {
            u'app_label': u'test_app_label',
            u'name': u'test_message',
            u'expiration_time': get_current_time(),
            u'context': {
                u'key1': u'value1',
                u'key2': u'value2',
            },
            u'recipient': Recipient(
                username=u'me',
            )
        }

    def test_get_channel_for_message(self):
        channel_map = ChannelMap([
            [u'file_email', FileEmailChannel],
            [u'sailthru_email', SailthruEmailChannel],
        ])

        transactional_msg = Message(options={u'transactional': True}, **self.msg_kwargs)
        info_msg = Message(options={}, **self.msg_kwargs)

        with patch(u'edx_ace.channel.channels', return_value=channel_map):
            assert get_channel_for_message(ChannelType.EMAIL, transactional_msg) is FileEmailChannel
            assert get_channel_for_message(ChannelType.EMAIL, info_msg) is SailthruEmailChannel

            with self.assertRaises(UnsupportedChannelError):
                assert get_channel_for_message(ChannelType.PUSH, transactional_msg)

    @override_settings(
        ACE_CHANNEL_DEFAULT_EMAIL='sailthru_email',
        ACE_CHANNEL_TRANSACTIONAL_EMAIL='file_email',
    )
    def test_default_channel(self):
        channel_map = ChannelMap([
            ['sailthru', SailthruEmailChannel],
        ])

        message = Message(options={u'transactional': True}, **self.msg_kwargs)

        with patch(u'edx_ace.channel.channels', return_value=channel_map):
            channel = get_channel_for_message(ChannelType.EMAIL, message)
            assert channel is SailthruEmailChannel
