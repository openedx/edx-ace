
from mock import Mock, patch

from django.test import TestCase

from edx_ace import ace
from edx_ace.channel import ChannelType
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedEmail
from edx_ace.test_utils import StubPolicy, patch_channels, patch_policies

TEMPLATES = {}


class TestAce(TestCase):
    @patch(
        'edx_ace.renderers.loader.get_template',
        side_effect=lambda t: TEMPLATES.setdefault(t, Mock(name='template {}'.format(t)))
    )
    def test_ace_send_happy_path(self, _mock_get_template):
        patch_policies(self, [StubPolicy([ChannelType.PUSH])])
        mock_channel = Mock(
            name='test_channel',
            channel_type=ChannelType.EMAIL
        )
        patch_channels(self, [mock_channel])

        recipient = Recipient(username='testuser')
        msg = Message(
            app_label='testapp',
            name='testmessage',
            recipient=recipient,
        )
        ace.send(msg)
        mock_channel.deliver.assert_called_once_with(
            msg,
            RenderedEmail(
                from_name=TEMPLATES['testapp/edx_ace/testmessage/email/from_name.txt'].render(),
                subject=TEMPLATES['testapp/edx_ace/testmessage/email/subject.txt'].render(),
                body_html=TEMPLATES['testapp/edx_ace/testmessage/email/body.html'].render(),
                head_html=TEMPLATES['testapp/edx_ace/testmessage/email/head.html'].render(),
                body=TEMPLATES['testapp/edx_ace/testmessage/email/body.txt'].render(),
            ),
        )
