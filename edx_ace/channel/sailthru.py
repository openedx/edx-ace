from __future__ import absolute_import, print_function, division

from datetime import datetime, timedelta
import logging
import random
import textwrap

import attr
from dateutil.tz import tzutc
from django.conf import settings
import six

from edx_ace.channel import Channel, ChannelType
from edx_ace.errors import RecoverableChannelDeliveryError, FatalChannelDeliveryError, InvalidMessageError
from edx_ace.utils.date import get_current_time

LOG = logging.getLogger(__name__)

try:
    from sailthru import SailthruClient, SailthruClientError
    CLIENT_LIBRARY_INSTALLED = True
except ImportError:
    LOG.warning('Sailthru client not installed. The Sailthru delivery channel is disabled.')
    CLIENT_LIBRARY_INSTALLED = False


RATE_LIMIT_ERROR_CODE = 43
# Reference: https://getstarted.sailthru.com/developers/api-basics/responses/
RECOVERABLE_ERROR_CODES = frozenset([
    9,   # Internal error: Something's gone wrong on Sailthru's end. Your request was probably not saved - try waiting a
         # moment and trying again.
    RATE_LIMIT_ERROR_CODE,  # Too many [type] requests this minute to /[endpoint] API: You have exceeded the limit of
                            # requests per minute for the given type (GET or POST) and endpoint. For limit details, see
                            # the Rate Limiting section on the API Technical Details page.
])
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

RESPONSE_HEADER_RATE_LIMIT_REMAINING = 'X-Rate-Limit-Remaining'
RESPONSE_HEADER_RATE_LIMIT_RESET = 'X-Rate-Limit-Reset'


class SailthruEmailChannel(Channel):

    channel_type = ChannelType.EMAIL

    @classmethod
    def enabled(cls):
        required_settings = (
            'ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME',
            'ACE_CHANNEL_SAILTHRU_API_KEY',
            'ACE_CHANNEL_SAILTHRU_API_SECRET',
        )

        for setting in required_settings:
            if not hasattr(settings, setting):
                LOG.warning("%s is not set, Sailthru email channel is disabled.", setting)

        return CLIENT_LIBRARY_INSTALLED and all(
            hasattr(settings, required_setting)
            for required_setting in required_settings
        )

    def __init__(self):
        if not self.enabled:
            self.sailthru_client = None
            LOG.warning('The Sailthru API client is not installed, so the Sailthru email channel is disabled.')
        elif (
            getattr(settings, 'ACE_CHANNEL_SAILTHRU_API_KEY', None) and
            getattr(settings, 'ACE_CHANNEL_SAILTHRU_API_SECRET', None)
        ):
            self.sailthru_client = SailthruClient(
                settings.ACE_CHANNEL_SAILTHRU_API_KEY,
                settings.ACE_CHANNEL_SAILTHRU_API_SECRET,
            )
        else:
            LOG.info("Unable to read ACE_CHANNEL_SAILTHRU_API_KEY or ACE_CHANNEL_SAILTHRU_API_SECRET")
            self.sailthru_client = None

        self.template_name = getattr(settings, 'ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME', None)
        if self.template_name is None:
            LOG.warning('ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME is unset, the Sailthru email channel is disabled')

    def deliver(self, message, rendered_message):
        template_vars = {}
        for key, value in six.iteritems(attr.asdict(rendered_message)):
            if value is not None:
                template_vars['ace_template_' + key] = value

        if message.recipient.email_address is None:
            raise InvalidMessageError(
                "No email address specified for recipient %s while sending message %s.%s",
                message.recipient,
                message.app_label,
                message.name,
            )

        if getattr(settings, 'ACE_CHANNEL_SAILTHRU_DEBUG', False):
            LOG.info(
                # TODO(later): Do our splunk parsers do the right thing with multi-line log messages like this?
                textwrap.dedent("""\
                    Would have emailed using:
                        template: %s
                        recipient: %s
                        variables: %s
                """),
                self.template_name,
                message.recipient.email_address,
                six.text_type(template_vars),
            )
            return

        if self.sailthru_client is None:
            raise FatalChannelDeliveryError(
                textwrap.dedent("""\
                    No sailthru client available to send:
                        template: %s
                        recipient: %s
                        variables: %s
                """),
                self.template_name,
                message.recipient.email_address,
                six.text_type(template_vars),
            )

        if self.template_name is None:
            raise FatalChannelDeliveryError(
                textwrap.dedent("""\
                    No template set when sending to:
                        recipient: %s
                        variables: %s
                """),
                message.recipient.email_address,
                six.text_type(template_vars),
            )

        try:
            # TODO(later): Log message send attempt using uuid
            response = self.sailthru_client.send(
                self.template_name,
                message.recipient.email_address,
                _vars=template_vars,
            )

            if response.is_ok():
                LOG.debug('Sailthru message sent')
                # TODO(later): emit some sort of analytics event?
                return True
            else:
                error = response.get_error()
                error_code = error.get_error_code()
                error_message = error.get_message()
                http_status_code = response.get_status_code()

                if error_code in RECOVERABLE_ERROR_CODES:
                    next_attempt_time = None
                    if error_code == RATE_LIMIT_ERROR_CODE:
                        next_attempt_time = self.get_rate_limit_reset_time(sailthru_response=response)

                    if next_attempt_time is None:
                        # Sailthru advises waiting "a moment" and then trying again.
                        next_attempt_time = get_current_time() + timedelta(
                            seconds=NEXT_ATTEMPT_DELAY_SECONDS + random.uniform(-2, 2)
                        )

                    raise RecoverableChannelDeliveryError(
                        'Recoverable Sailthru error (error_code={error_code} status_code={http_status_code}): {message}'.format(
                            error_code=error_code,
                            http_status_code=http_status_code,
                            message=error_message
                        ),
                        next_attempt_time
                    )
                else:
                    raise FatalChannelDeliveryError(
                        'Fatal Sailthru error (error_code={error_code} status_code={http_status_code}): {message}'.format(
                            error_code=error_code,
                            http_status_code=http_status_code,
                            message=error_message
                        )
                    )
        except SailthruClientError as exc:
            LOG.exception('Unable to communicate with the Sailthru API')
            raise FatalChannelDeliveryError(str(exc))

    @staticmethod
    def get_rate_limit_reset_time(sailthru_response):
        response = sailthru_response.response
        headers = response.headers

        # TODO(later): what if they don't send us back an int?
        remaining = int(headers[RESPONSE_HEADER_RATE_LIMIT_REMAINING])
        if remaining > 0:
            return None

        reset_timestamp = int(headers[RESPONSE_HEADER_RATE_LIMIT_RESET])
        reset_time_datetime = datetime.utcfromtimestamp(reset_timestamp).replace(tzinfo=tzutc())

        return reset_time_datetime
