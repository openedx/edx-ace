# pylint: disable=missing-docstring
from smtplib import SMTPException
from unittest.mock import Mock, patch

from django.core import mail
from django.core.files.temp import NamedTemporaryFile
from django.test import TestCase

from edx_ace.channel.file import PATH_OVERRIDE_KEY, FileEmailChannel
from edx_ace.errors import FatalChannelDeliveryError
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedEmail


class TestFilesEmailChannel(TestCase):
    def test_enabled_method(self):
        channel = FileEmailChannel()
        assert channel.enabled()

    def test_happy_path(self):
        channel = FileEmailChannel()
        rendered_message = RenderedEmail(
            from_name='Robot',
            head_html='<img src="https://tracker/.img" />',
            subject='\n Hello from  \r\nRobot ! \n',
            body='Just trying to see what is like to talk to a human!',
            body_html="""
                <p>Just trying to see what is like to talk to a human!</p>

                <hr />
            """,
        )

        with NamedTemporaryFile('r+') as f:
            message = Message(
                app_label='testapp',
                name='testmessage',
                options={
                    'from_address': 'bulk@example.com',
                    PATH_OVERRIDE_KEY: f.name,
                },
                recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
            )

            channel.deliver(message, rendered_message)

            contents = f.read()
            assert 'subject: Hello from' in contents
            assert 'to: mr@robot.io' in contents
            assert 'body: Just trying to see what' in contents
            assert 'talk to a human!</p>' in contents
