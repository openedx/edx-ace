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


EMAIL_TEMPLATE_LABELS = [u'ACE']

# Note: Some of these values are only known by Sailthru. It generates the beacon image URL (for example) so at python
# template rendering time we don't actually know the value of these variables in order to render them into the template.
# This forces us to delay substitution of these variables until the point where we are rendering the template using
# Sailthru's template engine.

# Note: The <a href="{optout_confirm_url}"></a> tag is required to appear in the template. Presumably Sailthru doesn't
# want you sending email without an unsubscribe link. However, we are embedding that link elsewhere in our body HTML, so
# we just tack on the obligatory link and style it with "display:none" to ensure it's not user visible.

# Note: Sailthru doesn't appear to offer a way to perform substitution on the value of a variable. We are passing in our
# rendered body in "ace_template_body_html" and we want to do something like "render(ace_template_body_html)", but we
# couldn't find any such function in Zephyr.
EMAIL_TEMPLATE_HTML = u"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
""".strip()

EMAIL_TEMPLATE_TXT = u"""
{body_text = replace(ace_template_body, '{view_url}', view_url)}
{body_text = replace(body_text, '{optout_confirm_url}', optout_confirm_url)}
{body_text = replace(body_text, '{forward_url}', forward_url)}
{body_text = replace(body_text, '{beacon_src}', beacon_src)}
{body_text}

If you believe this has been sent to you in error, please click <{optout_confirm_url}> to safely unsubscribe.
""".strip()


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

    TEMPLATE_DOES_NOT_EXIST = 14
    u"""
    This template does not exist in Sailthru.
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
            ACE_CHANNEL_SAILTHRU_FROM_ADDRESS = "verified_email@example.com"
            ACE_CHANNEL_SAILTHRU_API_KEY = "1234567890"
            ACE_CHANNEL_SAILTHRU_API_SECRET = "this is secret"
            .. settings_end

    It will create a minimal template in Sailthru for this message type if it doesn't already exist. The template name
    used will be the `unique_name` of the message. For example: "schedules.recurringnudge3".

    Messages are also expected to include a "template_public_name" option which is displayed on the opt-out form.
    This will be injected into a sentence like this: "You have followed a link to opt out of {template_public_name}
    emails from {platform_name}." If the user opts out they will not receive any more messages from that template.
    """

    channel_type = ChannelType.EMAIL

    @classmethod
    def enabled(cls):
        u"""
        Returns: True iff all required settings are not empty and the Sailthru client library is installed.
        """
        required_settings = (
            u'ACE_CHANNEL_SAILTHRU_API_KEY',
            u'ACE_CHANNEL_SAILTHRU_API_SECRET',
            u'ACE_CHANNEL_SAILTHRU_FROM_ADDRESS',
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

    def __init__(self):
        if not self.enabled():
            self.sailthru_client = None
        else:
            self.sailthru_client = SailthruClient(
                settings.ACE_CHANNEL_SAILTHRU_API_KEY,
                settings.ACE_CHANNEL_SAILTHRU_API_SECRET,
            )

    def deliver(self, message, rendered_message):
        if message.recipient.email_address is None:
            raise InvalidMessageError(
                u'No email address specified for recipient %s while sending message %s',
                message.recipient,
                message.log_id
            )

        template_vars = {}
        for key, value in six.iteritems(attr.asdict(rendered_message)):
            if value is not None:
                # Sailthru will silently fail to send the email if the from name or subject line contain new line
                # characters at the beginning or end of the string
                var_name = self._get_template_var_name_for_field(key)
                template_vars[var_name] = value.strip()

        logger = message.get_message_specific_logger(LOG)
        template_name = self._get_template_name_for_message(message)

        if getattr(settings, u'ACE_CHANNEL_SAILTHRU_DEBUG', False):
            logger.info(
                # TODO(later): Do our splunk parsers do the right thing with multi-line log messages like this?
                textwrap.dedent(u"""\
                    Would have emailed using:
                        template: %s
                        recipient: %s
                        variables: %s
                """),
                template_name,
                message.recipient.email_address,
                six.text_type(template_vars),
            )
            return

        if not self.enabled():
            raise FatalChannelDeliveryError(
                textwrap.dedent(u"""\
                    Sailthru channel is disabled, unable to send:
                        template: %s
                        recipient: %s
                        variables: %s
                """),
                template_name,
                message.recipient.email_address,
                six.text_type(template_vars),
            )

        try:
            logger.debug(u'Sending to Sailthru')

            response = self.sailthru_client.send(
                template_name,
                message.recipient.email_address,
                _vars=template_vars,
            )

            if response.is_ok():
                logger.debug(u'Successfully send to Sailthru')
                # TODO(later): emit some sort of analytics event?
                return
            else:
                logger.debug(u'Failed to send to Sailthru')
                self._handle_error_response(message, response)

        except SailthruClientError as exc:
            raise FatalChannelDeliveryError(u'Unable to communicate with the Sailthru API: ' + six.text_type(exc))

    def _handle_error_response(self, message, response):
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
            elif error_code == RecoverableErrorCodes.TEMPLATE_DOES_NOT_EXIST:
                self._create_sailthru_template_for_message(message)
                next_attempt_time = get_current_time()

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

    @staticmethod
    def _get_template_name_for_message(message):
        return message.unique_name

    @staticmethod
    def _get_template_var_name_for_field(message_field_name):
        return u'ace_template_' + message_field_name

    @staticmethod
    def _get_sailthru_template_var_for_field(message_field_name):
        return u'{{' + SailthruEmailChannel._get_template_var_name_for_field(message_field_name) + u'}}'

    def _create_sailthru_template_for_message(self, message):
        u"""
        Create a template in Sailthru for this message.

        Args:
            message (Message): The message being sent.

        Raises:
            RecoverableChannelDeliveryError: If we couldn't create the template but suspect we could if we tried again.
            FatalChannelDeliveryError: If we can't create the template and should not bother trying again.
        """
        template_name = self._get_template_name_for_message(message)
        template_spec = {
            u'labels': EMAIL_TEMPLATE_LABELS,
            u'subject': self._get_sailthru_template_var_for_field(u'subject'),
            u'from_email': settings.ACE_CHANNEL_SAILTHRU_FROM_ADDRESS,
            u'public_name': message.options.get(u'template_public_name', u'course'),
            u'is_google_analytics': True,
            u'from_name': self._get_sailthru_template_var_for_field(u'from_name'),
            u'is_link_tracking': True,
            u'content_html': EMAIL_TEMPLATE_HTML,
            u'content_text': EMAIL_TEMPLATE_TXT,
        }

        logger = message.get_message_specific_logger(LOG)
        try:
            logger.debug(u'Creating a new template in Sailthru: %s', template_name)

            response = self.sailthru_client.save_template(template_name, template_spec)

            if response.is_ok():
                logger.debug(u'Successfully created a new template called %s', template_name)
                return
            else:
                logger.debug(u'Failed to create a new template in Sailthru')
                self._handle_error_response(message, response)

        except SailthruClientError as exc:
            raise FatalChannelDeliveryError(u'Unable to communicate with the Sailthru API: ' + six.text_type(exc))
