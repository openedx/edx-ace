# pylint: disable=missing-docstring
from __future__ import absolute_import

from smtplib import SMTPException

from mock import Mock, patch

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
            from_name=u'Robot',
            head_html=u'<img src="https://tracker/.img" />',
            subject=u'\n Hello from  \r\nRobot ! \n',
            body=u'Just trying to see what is like to talk to a human!',
            body_html=u"""
                <p>Just trying to see what is like to talk to a human!</p>

                <hr />
            """,
        )

        with NamedTemporaryFile('r+') as f:
            message = Message(
                app_label=u'testapp',
                name=u'testmessage',
                options={
                    u'from_address': u'bulk@example.com',
                    PATH_OVERRIDE_KEY: f.name,
                },
                recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
            )

            channel.deliver(message, rendered_message)

            contents = f.read()
            assert u'subject: Hello from' in contents
            assert u'to: mr@robot.io' in contents
            assert u'body: Just trying to see what' in contents
            assert u'talk to a human!</p>' in contents
