# pylint: disable=missing-docstring
from __future__ import absolute_import

import ddt
from mock import patch

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
            app_label=u'testapp',
            name=u'testmessage',
            options={},
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )

        rendered_email = render(self.channel, message)

        assert u'{beacon_src}' in rendered_email.body_html
        assert u'{view_url}' in rendered_email.body_html
        assert u'{optout_confirm_url}' in rendered_email.body_html

    @override_settings(
        ACE_CHANNEL_SAILTHRU_DEBUG=False,
    )
    @ddt.data(
        ({u'from_address': 'custom@example.com'}, {u'behalf_email': 'custom@example.com'}),
        ({u'irrelevant': 'test'}, {}),
        ({}, {}),
    )
    @ddt.unpack
    def test_on_behalf_option_with_sailthru(self, message_options, expected_options):
        """
        Tests sailthru send API is called with on_behalf option
        """
        from_address = 'custom@example.com'
        message = Message(
            app_label=u'testapp',
            name=u'testmessage',
            options=message_options,
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )
        rendered_email = render(self.channel, message)

        with patch('edx_ace.channel.sailthru.SailthruClient.send') as mock_send:
            deliver(self.channel, rendered_email, message)
            self.assertEqual(mock_send.call_args_list[0][1]['options'], expected_options)
