# pylint: disable=missing-docstring
from __future__ import absolute_import

from smtplib import SMTPException

from mock import Mock, patch

from django.core import mail
from django.test import TestCase, override_settings

from edx_ace.channel.django_email import DjangoEmailChannel
from edx_ace.errors import FatalChannelDeliveryError
from edx_ace.message import Message
from edx_ace.presentation import render
from edx_ace.recipient import Recipient


class TestDjangoEmailChannel(TestCase):
    def setUp(self):
        super(TestDjangoEmailChannel, self).setUp()

        self.channel = DjangoEmailChannel()
        self.message = Message(
            app_label=u'testapp',
            name=u'testmessage',
            options={
                u'from_address': u'bulk@example.com',
            },
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )

        self.mock_rendered_message = Mock(
            subject=u'\n Hello from  \r\nRobot ! \n',
            body=u'Just trying to see what is like to talk to a human!',
            body_html=u"""
                <p>Just trying to see what is like to talk to a human!</p>

                <hr />
            """,
        )

    def _get_rendered_message(self):
        channel = DjangoEmailChannel()
        message = Message(
            app_label=u'testapp',
            name=u'testmessage',
            options={},
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )

        return render(channel, message)

    def test_enabled_method(self):
        assert self.channel.enabled()

    def test_happy_path(self):
        self.channel.deliver(self.message, self.mock_rendered_message)

        sent_email = mail.outbox[0]

        assert sent_email.subject == u'Hello from Robot !'
        assert u'Just trying to see what' in sent_email.body
        assert sent_email.to == [u'mr@robot.io']

        html_body, _ = sent_email.alternatives[0]

        assert u'talk to a human!</p>' in html_body

    @patch(u'django.core.mail.send_mail', side_effect=SMTPException)
    def test_smtp_failure(self, _send_mail):
        with self.assertRaises(FatalChannelDeliveryError):
            self.channel.deliver(self.message, self.mock_rendered_message)

    @override_settings(DEFAULT_FROM_EMAIL=None)
    def test_with_no_from_address_without_default(self):
        message = Message(
            app_label=u'testapp',
            name=u'testmessage',
            options={},
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )

        with self.assertRaises(FatalChannelDeliveryError):
            self.channel.deliver(message, self.mock_rendered_message)

    @override_settings(DEFAULT_FROM_EMAIL=u'hello@edx.org')
    def test_with_no_from_address_with_default(self):
        message = Message(
            app_label=u'testapp',
            name=u'testmessage',
            options={},
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )

        self.channel.deliver(message, self.mock_rendered_message)
        assert len(mail.outbox) == 1, u'Should have one email'

    def test_render_email_with_django_channel(self):
        rendered_email = self._get_rendered_message()
        assert u'{beacon_src}' not in rendered_email.body_html
        assert u'{view_url}' not in rendered_email.body_html
        assert u'{optout_confirm_url}' not in rendered_email.body_html

    def test_happy_sending_rendered_email(self):
        rendered_message = self._get_rendered_message()
        self.channel.deliver(self.message, rendered_message)

        assert mail.outbox, u'Should send the message'
        html_email = mail.outbox[0].alternatives[0][0]
        assert u'template head.html' in html_email
        assert u'template body.html' in html_email
