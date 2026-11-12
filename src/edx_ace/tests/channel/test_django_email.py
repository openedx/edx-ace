# pylint: disable=missing-docstring
from smtplib import SMTPException
from unittest.mock import Mock, patch

from django.core import mail
from django.test import TestCase, override_settings

from edx_ace.channel.django_email import DjangoEmailChannel
from edx_ace.errors import FatalChannelDeliveryError
from edx_ace.message import Message
from edx_ace.presentation import render
from edx_ace.recipient import Recipient


class TestDjangoEmailChannel(TestCase):
    def setUp(self):
        super().setUp()

        self.channel = DjangoEmailChannel()
        self.message = Message(
            app_label='testapp',
            name='testmessage',
            options={
                'from_address': 'bulk@example.com',
            },
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )

        self.mock_rendered_message = Mock(
            subject='\n Hello from  \r\nRobot ! \n',
            body='Just trying to see what is like to talk to a human!',
            body_html="""
                <p>Just trying to see what is like to talk to a human!</p>

                <hr />
            """,
        )

    def _get_rendered_message(self):
        channel = DjangoEmailChannel()
        message = Message(
            app_label='testapp',
            name='testmessage',
            options={},
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )

        return render(channel, message)

    def test_enabled_method(self):
        assert self.channel.enabled()

    def test_happy_path(self):
        self.channel.deliver(self.message, self.mock_rendered_message)

        sent_email = mail.outbox[0]

        html_body, _ = sent_email.alternatives[0]

        assert sent_email.subject == 'Hello from Robot !'
        assert 'Just trying to see what' in sent_email.body
        assert sent_email.to == ['mr@robot.io']

        assert 'talk to a human!</p>' in html_body

    @patch('django.core.mail.EmailMultiAlternatives.send', side_effect=SMTPException)
    def test_smtp_failure(self, _send):
        with self.assertRaises(FatalChannelDeliveryError):
            self.channel.deliver(self.message, self.mock_rendered_message)

    @override_settings(DEFAULT_FROM_EMAIL=None)
    def test_with_no_from_address_without_default(self):
        message = Message(
            app_label='testapp',
            name='testmessage',
            options={},
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )

        with self.assertRaises(FatalChannelDeliveryError):
            self.channel.deliver(message, self.mock_rendered_message)

    @override_settings(DEFAULT_FROM_EMAIL='hello@edx.org')
    def test_with_no_from_address_with_default(self):
        message = Message(
            app_label='testapp',
            name='testmessage',
            options={},
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )

        self.channel.deliver(message, self.mock_rendered_message)
        assert len(mail.outbox) == 1, 'Should have one email'

    def test_render_email_with_django_channel(self):
        rendered_email = self._get_rendered_message()
        assert '{beacon_src}' not in rendered_email.body_html
        assert '{view_url}' not in rendered_email.body_html
        assert '{optout_confirm_url}' not in rendered_email.body_html

    def test_happy_sending_rendered_email(self):
        rendered_message = self._get_rendered_message()
        self.channel.deliver(self.message, rendered_message)

        assert mail.outbox, 'Should send the message'

        html_email = mail.outbox[0].alternatives[0][0]
        assert 'template head.html' in html_email
        assert 'template body.html' in html_email

    def test_happy_email_with_reply_to(self):
        rendered_message = self._get_rendered_message()
        self.message.options['reply_to'] = ['learner@example.com']
        self.channel.deliver(self.message, rendered_message)

        sent_email = mail.outbox[0]

        assert sent_email.reply_to == ['learner@example.com']
