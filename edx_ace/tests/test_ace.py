try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from stevedore.extension import Extension
from django.test import TestCase, override_settings

from edx_ace import ace
from edx_ace.channel import ChannelType, CHANNEL_EXTENSION_NAMESPACE
from edx_ace.message import Message
from edx_ace.policy import POLICY_PLUGIN_NAMESPACE
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedEmail
from edx_ace.tests.test_policy import StubPolicy
from edx_ace.utils.plugins import get_manager


TEMPLATES = {}


@override_settings(ACE_ENABLED_POLICIES=['test_policy'])
class TestAce(TestCase):
    def setUp(self):
        self.mock_email_channel = Mock(
            name='mock_email_channel',
            channel_type=ChannelType.EMAIL
        )

        self.policy_manager = get_manager(
            POLICY_PLUGIN_NAMESPACE,
            'test_policy'
        ).make_test_instance([
            Extension('test_policy', None, lambda: StubPolicy({ChannelType.PUSH}), None)
        ])

        self.channel_manager = get_manager(
            CHANNEL_EXTENSION_NAMESPACE,
            'test_channel'
        ).make_test_instance([
            Extension(
                'test_channel',
                None,
                self.mock_email_channel,
                None,
            )
        ])

        patcher = patch('edx_ace.utils.plugins.get_manager', self._get_manager)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _get_manager(self, namespace, names=None, instantiate=False):
        if namespace == POLICY_PLUGIN_NAMESPACE:
            return self.policy_manager
        elif namespace == CHANNEL_EXTENSION_NAMESPACE:
            return self.channel_manager


    @patch(
        'edx_ace.renderers.loader.get_template',
        side_effect=lambda t: TEMPLATES.setdefault(t, Mock(name='template {}'.format(t)))
    )
    def test_ace_send_happy_path(self, mock_get_template):
        recipient = Recipient(username='testuser')
        msg = Message(
            app_label='testapp',
            name='testmessage',
            recipient=recipient,
        )
        ace.send(msg)
        self.mock_email_channel().deliver.assert_called_once_with(
            msg,
            RenderedEmail(
                from_name=TEMPLATES['testapp/edx_ace/testmessage/email/from_name.txt'].render(),
                subject=TEMPLATES['testapp/edx_ace/testmessage/email/subject.txt'].render(),
                body_html=TEMPLATES['testapp/edx_ace/testmessage/email/body.html'].render(),
                head_html=TEMPLATES['testapp/edx_ace/testmessage/email/head.html'].render(),
                body_text=TEMPLATES['testapp/edx_ace/testmessage/email/body.txt'].render(),
            ),
        )
