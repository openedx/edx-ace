"""
Tests of :mod:`edx_ace.channel`.
"""
from unittest.mock import patch

from django.test import TestCase, override_settings

from edx_ace.channel import ChannelMap, ChannelType, get_channel_for_message
from edx_ace.channel.braze import BrazeEmailChannel
from edx_ace.channel.file import FileEmailChannel
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

    @override_settings(
        ACE_CHANNEL_BRAZE_CAMPAIGNS={
            'campaign_msg': 'campaign_id:variation_id',
        },
        ACE_CHANNEL_DEFAULT_EMAIL='braze_email',
        ACE_CHANNEL_TRANSACTIONAL_EMAIL='file_email',
    )
    def test_get_channel_for_message(self):
        channel_map = ChannelMap([
            ['file_email', FileEmailChannel()],
            ['braze_email', BrazeEmailChannel()],
        ])

        transactional_msg = Message(options={'transactional': True}, **self.msg_kwargs)
        info_msg = Message(options={}, **self.msg_kwargs)

        # A transactional message which the default channel wants to handle and thus should be directed appropriately
        transactional_campaign_msg = Message(options={'transactional': True}, **self.msg_kwargs)
        transactional_campaign_msg.name = 'campaign_msg'

        with patch('edx_ace.channel.channels', return_value=channel_map):
            assert isinstance(get_channel_for_message(ChannelType.EMAIL, transactional_msg), FileEmailChannel)
            assert isinstance(get_channel_for_message(ChannelType.EMAIL, transactional_campaign_msg), BrazeEmailChannel)
            assert isinstance(get_channel_for_message(ChannelType.EMAIL, info_msg), BrazeEmailChannel)

            with self.assertRaises(UnsupportedChannelError):
                assert get_channel_for_message(ChannelType.PUSH, transactional_msg)

    @override_settings(
        ACE_CHANNEL_DEFAULT_EMAIL='braze_email',
        ACE_CHANNEL_TRANSACTIONAL_EMAIL='file_email',
    )
    def test_default_channel(self):
        channel_map = ChannelMap([
            ['braze', BrazeEmailChannel()],
        ])

        message = Message(options={'transactional': True}, **self.msg_kwargs)

        with patch('edx_ace.channel.channels', return_value=channel_map):
            channel = get_channel_for_message(ChannelType.EMAIL, message)
            assert isinstance(channel, BrazeEmailChannel)
