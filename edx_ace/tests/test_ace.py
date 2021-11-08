"""
Tests of :mod:`edx_ace.ace`.
"""
from unittest.mock import Mock, patch

from django.test import TestCase

from edx_ace import ace
from edx_ace.channel import ChannelMap, ChannelType
from edx_ace.errors import UnsupportedChannelError
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedEmail
from edx_ace.test_utils import StubPolicy, patch_policies


class TestAce(TestCase):
    """
    Tests for the send method.
    """
    def test_ace_send_happy_path(self):
        patch_policies(self, [StubPolicy([ChannelType.PUSH])])
        mock_channel = Mock(
            channel_type=ChannelType.EMAIL,
            action_links=[],
            get_action_links=[],
            tracker_image_sources=[],
        )

        recipient = Recipient(lms_user_id=123)
        msg = Message(
            app_label='testapp',
            name='testmessage',
            recipient=recipient,
        )

        channel_map = ChannelMap([
            ['sailthru_email', mock_channel],
        ])

        with patch('edx_ace.channel.channels', return_value=channel_map):
            ace.send(msg)

        mock_channel.deliver.assert_called_once_with(
            msg,
            RenderedEmail(
                from_name='template from_name.txt',
                subject='template subject.txt',
                # The new lines are needed because the template has some tags, which means leftover newlines
                body_html='template body.html\n\n\n\n\n',
                head_html='template head.html\n',
                body='template body.txt',
            ),
        )

    @patch('edx_ace.ace.get_channel_for_message', side_effect=UnsupportedChannelError)
    def test_ace_send_unsupported_channel(self, *_args):
        recipient = Recipient(lms_user_id=123)
        msg = Message(
            app_label='testapp',
            name='testmessage',
            recipient=recipient,
        )

        ace.send(msg)  # UnsupportedChannelError shouldn't throw UnsupportedChannelError
