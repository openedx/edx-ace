# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.channel.django_email` implements a Django `send_mail()` email
delivery channel for ACE.
"""
from __future__ import absolute_import, division, print_function

import logging
import re
from smtplib import SMTPException

from django.conf import settings
from django.core import mail

from edx_ace.channel import Channel, ChannelType
from edx_ace.errors import FatalChannelDeliveryError

LOG = logging.getLogger(__name__)

TEMPLATE = u"""\
<!DOCTYPE html>
<html>
    <head>
        {head_html}
    </head>
    <body>
        {body_html}
    </body>
</html>
"""


class DjangoEmailChannel(Channel):
    u"""
    A `send_mail()` channel for edX ACE.

    This is both useful for providing an alternative to Sailthru and to debug ACE mail by
    inspecting `django.core.mail.outbox`.



    Example:

        Sample settings::

            .. settings_start
            EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
            EMAIL_HOST = 'localhost'
            DEFAULT_FROM_EMAIL = 'hello@example.org'

            ACE_CHANNEL_DEFAULT_EMAIL = 'sailthru_email'
            ACE_CHANNEL_TRANSACTIONAL_EMAIL = 'django_email'

            ACE_ENABLED_CHANNELS = [
                'sailthru_email',
                'django_email',
            ]
            .. settings_end
    """

    channel_type = ChannelType.EMAIL

    @classmethod
    def enabled(cls):
        u"""
        Returns: True always!
        """
        return True

    def deliver(self, message, rendered_message):
        # Compress spaces and remove newlines to make it easier to author templates.
        subject = re.sub(u'\\s+', u' ', rendered_message.subject, re.UNICODE).strip()
        default_from_address = getattr(settings, u'DEFAULT_FROM_EMAIL', None)
        from_address = message.options.get(u'from_address', default_from_address)
        if not from_address:
            raise FatalChannelDeliveryError(
                u'from_address must be included in message delivery options or as the DEFAULT_FROM_EMAIL settings'
            )

        rendered_template = TEMPLATE.format(
            head_html=rendered_message.head_html,
            body_html=rendered_message.body_html,
        )

        try:
            mail.send_mail(
                subject,
                rendered_message.body,
                from_address,
                [message.recipient.email_address],
                html_message=rendered_template,
            )
        except SMTPException as e:
            LOG.exception(e)
            raise FatalChannelDeliveryError(u'An SMTP error occurred (and logged) from Django send_email()')
