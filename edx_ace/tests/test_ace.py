u"""
Tests of :mod:`edx_ace.ace`.
"""
from __future__ import absolute_import

from mock import Mock, patch

from django.test import TestCase

from edx_ace import ace
from edx_ace.channel import ChannelMap, ChannelType
from edx_ace.errors import UnsupportedChannelError
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedEmail
from edx_ace.test_utils import StubPolicy, patch_policies


class TestAce(TestCase):
    u"""
    Tests for the send method.
    """
    def test_ace_send_happy_path(self):
        patch_policies(self, [StubPolicy([ChannelType.PUSH])])
        mock_channel = Mock(
            channel_type=ChannelType.EMAIL,
            action_links=[],
            tracker_image_sources=[],
        )

        recipient = Recipient(username=u'testuser')
        msg = Message(
            app_label=u'testapp',
            name=u'testmessage',
            recipient=recipient,
        )

        channel_map = ChannelMap([
            [u'sailthru_email', mock_channel],
        ])

        with patch(u'edx_ace.channel.channels', return_value=channel_map):
            ace.send(msg)

        mock_channel.deliver.assert_called_once_with(
            msg,
            RenderedEmail(
                from_name=u'template from_name.txt',
                subject=u'template subject.txt',
                # The new lines are needed because the template has some tags, which means leftover newlines
                body_html=u'template body.html\n\n\n\n\n',
                head_html=u'template head.html\n',
                body=u'template body.txt',
            ),
        )

    @patch(u'edx_ace.ace.get_channel_for_message', side_effect=UnsupportedChannelError)
    def test_ace_send_unsupported_channel(self, *_args):
        recipient = Recipient(username=u'testuser')
        msg = Message(
            app_label=u'testapp',
            name=u'testmessage',
            recipient=recipient,
        )

        ace.send(msg)  # UnsupportedChannelError shouldn't throw UnsupportedChannelError
