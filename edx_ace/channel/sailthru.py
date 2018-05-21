# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.channel.sailthru` implements a SailThru-based email delivery
channel for ACE.
"""
from __future__ import absolute_import, division, print_function

import logging
import random
import textwrap
from datetime import datetime, timedelta
from enum import Enum
from gettext import gettext as _

import attr
import six
from dateutil.tz import tzutc

from django.conf import settings

from edx_ace.channel import Channel, ChannelType
from edx_ace.errors import FatalChannelDeliveryError, InvalidMessageError, RecoverableChannelDeliveryError
from edx_ace.utils.date import get_current_time

LOG = logging.getLogger(__name__)

try:
    from sailthru import SailthruClient, SailthruClientError

    CLIENT_LIBRARY_INSTALLED = True
except ImportError:
    LOG.warning(u'Sailthru client not installed. The Sailthru delivery channel is disabled.')
    CLIENT_LIBRARY_INSTALLED = False


class RecoverableErrorCodes(Enum):
    u"""
    These `error codes`_ are present in responses to requests that can (and should) be retried after waiting for a bit.

    .. _error codes:
        https://getstarted.sailthru.com/developers/api-basics/responses/
    """
    INTERNAL_ERROR = 9
    u"""
    Something's gone wrong on Sailthru's end. Your request was probably not saved - try waiting a moment and trying
    again.
    """

    RATE_LIMIT = 43
    u"""
    Too many [type] requests this minute to /[endpoint] API: You have exceeded the limit of requests per minute for the
    given type (GET or POST) and endpoint. For limit details, see the Rate Limiting section on the API Technical Details
    page.
    """


NEXT_ATTEMPT_DELAY_SECONDS = 10

# TODO(later): Should we do something different with these responses?
# OPT_OUT_ERROR_CODES = frozenset([
#     32,  # Email has opted out of delivery from client: This email has opted out of delivery from any emails coming
#          # from your site and should not be emailed.
#     33,  # Email has opted out of delivery from template: This email has opted out of delivery from the specific
#          # template you are sending, and should not be sent this type of email.
#     34,  # Email may not be emailed: This email has been identified as an email that should never be emailed.
#     35,  # Email is a known hardbounce: This email has been previously identified as a hardbounce, so should not be
#          # emailed.
#     37,  # Email will only accept basic templates: The user has opted out of delivery from all templates except basic
#          # templates.
# ])


class ResponseHeaders(Enum):
    u"""
    These are `special headers`_ returned in responses from the Sailthru REST API.

    .. _special headers:
        https://getstarted.sailthru.com/developers/api-basics/technical/#HTTP_Response_Headers
    """

    RATE_LIMIT_REMAINING = u'X-Rate-Limit-Remaining'
    RATE_LIMIT_RESET = u'X-Rate-Limit-Reset'


class SailthruEmailChannel(Channel):
    u"""
    An email channel for delivering messages to users using Sailthru.

    This channel makes use of the Sailthru REST API to send messages. It is designed for "at most once" delivery of
    messages. It will make a reasonable attempt to deliver the message and give up if it can't. It also only confirms
    that Sailthru has received the request to send the email, it doesn't actually confirm that it made it to the
    recipient.

    The integration with Sailthru requires several Django settings to be defined.

    Example:

        Sample settings::

            .. settings_start
            ACE_CHANNEL_SAILTHRU_DEBUG = False
            ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME = "Some template name"
            ACE_CHANNEL_SAILTHRU_API_KEY = "1234567890"
            ACE_CHANNEL_SAILTHRU_API_SECRET = "this is secret"
            .. settings_end

    The named template in Sailthru should be minimal, most of the rendering happens within ACE. The "From Name" field
    should be set to ``{{ace_template_from_name}}``. The "Subject" field should be set to ``{{ace_template_subject}}``.
    The "Code" for the template should be::

        <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
            <head>
                {{ace_template_head_html}}
            </head>
            <body>
                {body_html = replace(ace_template_body_html, '{view_url}', view_url)}
                {body_html = replace(body_html, '{optout_confirm_url}', optout_confirm_url)}
                {body_html = replace(body_html, '{forward_url}', forward_url)}
                {body_html = replace(body_html, '{beacon_src}', beacon_src)}
                {body_html}
                <span id="sailthru-message-id" style="display: none;">{message_id()}</span>
                <a href="{optout_confirm_url}" style="display: none;"></a>
            </body>
        </html>

    """

    channel_type = ChannelType.EMAIL

    @classmethod
    def enabled(cls):
        u"""
        Returns: True iff all required settings are not empty and the Sailthru client library is installed.
        """
        required_settings = (
            u'ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME',
            u'ACE_CHANNEL_SAILTHRU_API_KEY',
            u'ACE_CHANNEL_SAILTHRU_API_SECRET',
        )

        for setting in required_settings:
            if not hasattr(settings, setting):
                LOG.warning(u'%s is not set, Sailthru email channel is disabled.', setting)

        if not CLIENT_LIBRARY_INSTALLED:
            LOG.warning(u'The Sailthru API client is not installed, so the Sailthru email channel is disabled.')

        return CLIENT_LIBRARY_INSTALLED and all(
            hasattr(settings, required_setting)
            for required_setting in required_settings
        )

    @property
    def action_links(self):
        # Note that these variables are evaluated by Sailthru, not the Django template engine
        return [
            (u'{view_url}', _(u'View on Web')),
            (u'{optout_confirm_url}', _(u'Unsubscribe from this list')),
        ]

    @property
    def tracker_image_sources(self):
        # Note {beacon_src} is not a template variable that is evaluated by the Django template engine.
        # It is evaluated by Sailthru when the email is sent.
        return [u'{beacon_src}']

    def __init__(self):
        if not self.enabled():
            self.sailthru_client = None
        else:
            self.sailthru_client = SailthruClient(
                settings.ACE_CHANNEL_SAILTHRU_API_KEY,
                settings.ACE_CHANNEL_SAILTHRU_API_SECRET,
            )

        self.template_name = settings.ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME

    def deliver(self, message, rendered_message):
        if message.recipient.email_address is None:
            raise InvalidMessageError(
                u'No email address specified for recipient %s while sending message %s',
                message.recipient,
                message.log_id
            )

        template_vars, options = {}, {}
        for key, value in six.iteritems(attr.asdict(rendered_message)):
            if value is not None:
                # Sailthru will silently fail to send the email if the from name or subject line contain new line
                # characters at the beginning or end of the string
                template_vars[u'ace_template_' + key] = value.strip()

        if u'from_address' in message.options:
            options[u'behalf_email'] = message.options.get(u'from_address')

        logger = message.get_message_specific_logger(LOG)

        if getattr(settings, u'ACE_CHANNEL_SAILTHRU_DEBUG', False):
            logger.info(
                # TODO(later): Do our splunk parsers do the right thing with multi-line log messages like this?
                textwrap.dedent(u"""\
                    Would have emailed using:
                        template: %s
                        recipient: %s
                        variables: %s
                        options: %s
                """),
                self.template_name,
                message.recipient.email_address,
                six.text_type(template_vars),
                six.text_type(options),
            )
            return

        if not self.enabled():
            raise FatalChannelDeliveryError(
                textwrap.dedent(u"""\
                    Sailthru channel is disabled, unable to send:
                        template: %s
                        recipient: %s
                        variables: %s
                        options: %s
                """),
                self.template_name,
                message.recipient.email_address,
                six.text_type(template_vars),
                six.text_type(options),
            )

        try:
            logger.debug(u'Sending to Sailthru')

            response = self.sailthru_client.send(
                self.template_name,
                message.recipient.email_address,
                _vars=template_vars,
                options=options,
            )

            if response.is_ok():
                logger.debug(u'Successfully send to Sailthru')
                # TODO(later): emit some sort of analytics event?
                return
            else:
                logger.debug(u'Failed to send to Sailthru')
                self._handle_error_response(response)

        except SailthruClientError as exc:
            raise FatalChannelDeliveryError(u'Unable to communicate with the Sailthru API: ' + six.text_type(exc))

    def _handle_error_response(self, response):
        u"""
        Handle an error response from SailThru, either by retrying or failing
        with an appropriate exception.

        Arguments:
            response: The HTTP response recieved from SailThru.
        """
        error = response.get_error()
        error_code = error.get_error_code()
        error_message = error.get_message()
        http_status_code = response.get_status_code()
        if error_code in RecoverableErrorCodes:
            next_attempt_time = None
            if error_code == RecoverableErrorCodes.RATE_LIMIT:
                next_attempt_time = self._get_rate_limit_reset_time(sailthru_response=response)

            if next_attempt_time is None:
                # Sailthru advises waiting "a moment" and then trying again.
                next_attempt_time = get_current_time() + timedelta(
                    seconds=NEXT_ATTEMPT_DELAY_SECONDS + random.uniform(-2, 2)
                )

            raise RecoverableChannelDeliveryError(
                u'Recoverable Sailthru error (error_code={error_code} status_code={http_status_code}): '
                u'{message}'.format(
                    error_code=error_code,
                    http_status_code=http_status_code,
                    message=error_message
                ),
                next_attempt_time
            )
        else:
            raise FatalChannelDeliveryError(
                u'Fatal Sailthru error (error_code={error_code} status_code={http_status_code}): '
                u'{message}'.format(
                    error_code=error_code,
                    http_status_code=http_status_code,
                    message=error_message
                )
            )

    @staticmethod
    def _get_rate_limit_reset_time(sailthru_response):
        u"""
        Given a response from the Sailthru API, check to see if our requests are being rate limited.

        If so, return a timestamp indicating when the limit will reset.

        Args:
            sailthru_response (SailthruResponse):

        Returns:
            datetime: The time at which delivery can be re-attempted because the rate limit will be reset.
        """
        response = sailthru_response.response
        headers = response.headers

        try:
            remaining = int(headers[ResponseHeaders.RATE_LIMIT_REMAINING])
            if remaining > 0:
                return None

            reset_timestamp = int(headers[ResponseHeaders.RATE_LIMIT_RESET])
            return datetime.utcfromtimestamp(reset_timestamp).replace(tzinfo=tzutc())
        except ValueError:
            return None
