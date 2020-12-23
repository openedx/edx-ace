# pylint: disable=missing-docstring
from unittest.mock import patch

import ddt

from django.test import TestCase, override_settings

from edx_ace.channel.sailthru import SailthruEmailChannel
from edx_ace.delivery import deliver
from edx_ace.message import Message
from edx_ace.presentation import render
from edx_ace.recipient import Recipient


@ddt.ddt
class TestSailthruChannel(TestCase):

    def setUp(self):
        self.channel = SailthruEmailChannel()

    def test_render_email_with_sailthru(self):
        message = Message(
            app_label='testapp',
            name='testmessage',
            options={},
            recipient=Recipient(username='Robot', email_address='mr@robot.io'),
        )

        rendered_email = render(self.channel, message)

        assert '{beacon_src}' in rendered_email.body_html
        assert '{view_url}' in rendered_email.body_html
        assert '{optout_confirm_url}' in rendered_email.body_html

    @override_settings(
        ACE_CHANNEL_SAILTHRU_DEBUG=False,
    )
    @ddt.data(
        ({'from_address': 'custom@example.com'}, {'behalf_email': 'custom@example.com'}),
        ({'reply_to': 'student@example.com'}, {'behalf_email': 'student@example.com'}),
        ({'irrelevant': 'test'}, {}),
        ({}, {}),
    )
    @ddt.unpack
    def test_on_behalf_option_with_sailthru(self, message_options, expected_options):
        """
        Tests sailthru send API is called with on_behalf option
        """
        message = Message(
            app_label='testapp',
            name='testmessage',
            options=message_options,
            recipient=Recipient(username='Robot', email_address='mr@robot.io'),
        )
        rendered_email = render(self.channel, message)

        with patch('edx_ace.channel.sailthru.SailthruClient.send') as mock_send:
            deliver(self.channel, rendered_email, message)
            self.assertEqual(mock_send.call_args_list[0][1]['options'], expected_options)
