u"""
Tests of :mod:`edx_ace.ace`.
"""
from __future__ import absolute_import

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
        u'edx_ace.renderers.loader.get_template',
        side_effect=lambda t: TEMPLATES.setdefault(t, Mock(name=u'template {}'.format(t)))
    )
    def test_ace_send_happy_path(self, _mock_get_template):
        patch_policies(self, [StubPolicy([ChannelType.PUSH])])
        mock_channel = Mock(
            name=u'test_channel',
            channel_type=ChannelType.EMAIL
        )
        patch_channels(self, [mock_channel])

        recipient = Recipient(username=u'testuser')
        msg = Message(
            app_label=u'testapp',
            name=u'testmessage',
            recipient=recipient,
        )
        ace.send(msg)
        mock_channel.deliver.assert_called_once_with(
            msg,
            RenderedEmail(
                from_name=TEMPLATES[u'testapp/edx_ace/testmessage/email/from_name.txt'].render(),
                subject=TEMPLATES[u'testapp/edx_ace/testmessage/email/subject.txt'].render(),
                body_html=TEMPLATES[u'testapp/edx_ace/testmessage/email/body.html'].render(),
                head_html=TEMPLATES[u'testapp/edx_ace/testmessage/email/head.html'].render(),
                body=TEMPLATES[u'testapp/edx_ace/testmessage/email/body.txt'].render(),
            ),
        )
