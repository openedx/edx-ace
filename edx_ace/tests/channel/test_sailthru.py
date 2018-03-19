# pylint: disable=missing-docstring
from __future__ import absolute_import

from django.test import TestCase

from edx_ace.channel.sailthru import SailthruEmailChannel
from edx_ace.message import Message
from edx_ace.presentation import render
from edx_ace.recipient import Recipient


class TestSailthruChannel(TestCase):
    def test_render_email_with_sailthru(self):
        channel = SailthruEmailChannel()
        message = Message(
            app_label=u'testapp',
            name=u'testmessage',
            options={},
            recipient=Recipient(username=u'Robot', email_address=u'mr@robot.io'),
        )

        rendered_email = render(channel, message)

        assert u'{beacon_src}' in rendered_email.body_html
        assert u'{view_url}' in rendered_email.body_html
        assert u'{optout_confirm_url}' in rendered_email.body_html
