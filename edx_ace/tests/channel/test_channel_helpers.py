"""
Tests of :mod:`edx_ace.channel`.
"""
from unittest.mock import patch

from django.test import TestCase, override_settings

from edx_ace.channel import ChannelMap, ChannelType, get_channel_for_message
from edx_ace.channel.file import FileEmailChannel
from edx_ace.channel.sailthru import SailthruEmailChannel
from edx_ace.errors import UnsupportedChannelError
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.utils.date import get_current_time


class TestChannelMap(TestCase):
    """
    Tests for the channels().
    """

    def setUp(self):
        self.msg_kwargs = {
            'app_label': 'test_app_label',
            'name': 'test_message',
            'expiration_time': get_current_time(),
            'context': {
                'key1': 'value1',
                'key2': 'value2',
            },
            'recipient': Recipient(
                lms_user_id=123,
            )
        }

    def test_get_channel_for_message(self):
        channel_map = ChannelMap([
            ['file_email', FileEmailChannel],
            ['sailthru_email', SailthruEmailChannel],
        ])

        transactional_msg = Message(options={'transactional': True}, **self.msg_kwargs)
        info_msg = Message(options={}, **self.msg_kwargs)

        with patch('edx_ace.channel.channels', return_value=channel_map):
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

        message = Message(options={'transactional': True}, **self.msg_kwargs)

        with patch('edx_ace.channel.channels', return_value=channel_map):
            channel = get_channel_for_message(ChannelType.EMAIL, message)
            assert channel is SailthruEmailChannel
