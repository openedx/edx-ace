# -*- coding: utf-8 -*-
"""
:mod:`edx_ace.channel.django_email` implements a Django `send_mail()` email
delivery channel for ACE.
"""
import logging
import re
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from edx_ace.channel import Channel, ChannelType
from edx_ace.errors import FatalChannelDeliveryError

LOG = logging.getLogger(__name__)

TEMPLATE = """\
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
    """
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
        """
        Returns: True always!
        """
        return True

    def deliver(self, message, rendered_message):
        # Compress spaces and remove newlines to make it easier to author templates.
        subject = re.sub('\\s+', ' ', rendered_message.subject, re.UNICODE).strip()
        default_from_address = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        reply_to = message.options.get('reply_to', None)
        from_address = message.options.get('from_address', default_from_address)
        if not from_address:
            raise FatalChannelDeliveryError(
                'from_address must be included in message delivery options or as the DEFAULT_FROM_EMAIL settings'
            )

        rendered_template = TEMPLATE.format(
            head_html=rendered_message.head_html,
            body_html=rendered_message.body_html,
        )
        try:
            mail = EmailMultiAlternatives(
                subject=subject,
                body=rendered_message.body,
                from_email=from_address,
                to=[message.recipient.email_address],
                reply_to=reply_to,
            )

            mail.attach_alternative(rendered_template, 'text/html')
            mail.send()
        except SMTPException as e:
            LOG.exception(e)
            raise FatalChannelDeliveryError('An SMTP error occurred (and logged) from Django send_email()')
