from django.test import TestCase
from edx_ace.message import Message
from freezegun import freeze_time

from edx_ace.channel import ChannelType
from edx_ace.delivery import deliver
from edx_ace.recipient import Recipient
from edx_ace.test_utils import patch_channels, sentinel, Mock


class TestDelivery(TestCase):

    def test_happy_path(self):
        mock_channel = Mock(
            name='test_channel',
            channel_type=ChannelType.EMAIL
        )
        patch_channels(self, [mock_channel])
        recipient = Recipient(
            username=str(sentinel.username)
        )
        message = Message(
            app_label=str(sentinel.app_label),
            name=str(sentinel.name),
            recipient=recipient,
        )
        deliver(ChannelType.EMAIL, sentinel.rendered_email, message)
        mock_channel.deliver.assert_called_once_with(message, sentinel.rendered_email)
