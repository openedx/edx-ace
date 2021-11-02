"""
:mod:`edx_ace.channel.braze` implements a Braze-based email delivery channel for ACE.
"""
import logging
import random
import warnings
from datetime import timedelta
from gettext import gettext as _

import requests

from django.conf import settings

from edx_ace.channel import Channel
from edx_ace.channel.django_email import DjangoEmailChannel
from edx_ace.channel.mixins import EmailChannelMixin
from edx_ace.errors import FatalChannelDeliveryError, RecoverableChannelDeliveryError
from edx_ace.utils.date import get_current_time

LOG = logging.getLogger(__name__)

NEXT_ATTEMPT_DELAY_SECONDS = 30


class BrazeEmailChannel(EmailChannelMixin, Channel):
    """
    An email channel for delivering messages to users using Braze.

    This channel makes use of the Braze REST API to send messages. It is designed for "at most once" delivery of
    messages. It will make a reasonable attempt to deliver the message and give up if it can't. It also only confirms
    that Braze has received the request to send the email, it doesn't actually confirm that it made it to the
    recipient.

    See the Braze documentation for message sending, for more information:
    https://www.braze.com/docs/api/endpoints/messaging/send_messages/post_send_messages/

    The recipient email address is ignored, instead Braze uses its stored email address for the recipient. Although,
    if the lms_user_id is not valid, this channel falls back to the Django email channel and then the address will
    be used.

    The integration with Braze requires several Django settings to be defined.

    The ACE_CHANNEL_BRAZE_CAMPAIGNS setting is optional, but if it is defined, it should be a mapping of ACE message
    names to campaign ids. And optionally a message variation id, separated by a colon. See the example below.

    Example:

        Sample settings::

            .. settings_start
            ACE_CHANNEL_BRAZE_API_KEY = "1c304d0d-c800-4da3-bfaa-41b1189b34cb"
            ACE_CHANNEL_BRAZE_APP_ID = "f6232495-6ad6-4310-bab5-5673768856aa"
            ACE_CHANNEL_BRAZE_FROM_EMAIL = "Open edX <openedx@example.com>"
            ACE_CHANNEL_BRAZE_REST_ENDPOINT = "rest.iad-01.braze.com"
            ACE_CHANNEL_BRAZE_CAMPAIGNS = {
                "deletionnotificationmessage": "campaign_id:variation_id"
            }
            .. settings_end
    """

    _API_KEY_SETTING = 'ACE_CHANNEL_BRAZE_API_KEY'
    _APP_ID_SETTING = 'ACE_CHANNEL_BRAZE_APP_ID'
    _CAMPAIGNS_SETTING = 'ACE_CHANNEL_BRAZE_CAMPAIGNS'  # optional
    _ENDPOINT_SETTING = 'ACE_CHANNEL_BRAZE_REST_ENDPOINT'
    _FROM_EMAIL_SETTING = 'ACE_CHANNEL_BRAZE_FROM_EMAIL'  # optional

    @classmethod
    def enabled(cls):
        """
        Returns: True iff all required settings are not empty and the Braze client library is installed.
        """
        ok = True

        for setting in (
            cls._API_KEY_SETTING,
            cls._APP_ID_SETTING,
            cls._ENDPOINT_SETTING,
        ):
            if not getattr(settings, setting, None):
                ok = False
                LOG.warning('%s is not set, Braze email channel is disabled.', setting)

        return ok

    @property
    def action_links(self):
        """
        This method is now deprecated in favor of get_action_links,
        but will continue to work for the time being as it calls get_action_links under the hood.
        """
        warnings.warn("This method is now deprecated in favor of get_action_links")
        return self.get_action_links()

    def get_action_links(self, **kwargs):
        """
        Provides list of action links, called by templates directly.
        Supported kwargs:
            omit_unsubscribe_link (bool): Removes the unsubscribe link from the email.
                DO NOT send emails with no unsubscribe link unless you are sure it will not violate the CANSPAM act.
        """
        omit_unsubscribe_link = kwargs.get('omit_unsubscribe_link')
        action_links = []
        if not omit_unsubscribe_link:
            action_links += [('{{${set_user_to_unsubscribed_url}}}', _('Unsubscribe from this list'))]
        return action_links

    @property
    def tracker_image_sources(self):
        """Provides list of trackers, called by templates directly"""
        return []  # not needed

    def deliver(self, message, rendered_message):
        if not self.enabled():
            raise FatalChannelDeliveryError('Braze channel is disabled, unable to send')

        if not message.recipient.lms_user_id:
            # This channel assumes that you have Braze configured with LMS user_ids as your external_user_id in Braze.
            # Unfortunately, that means that we can't send emails to users that aren't registered with the LMS,
            # which some callers of ACE may attempt to do (despite the lms_user_id being a required Recipient field).
            # In these cases, we fall back to a simple Django smtp email.
            DjangoEmailChannel().deliver(message, rendered_message)
            return

        transactional = message.options.get('transactional', False)
        body_html = self.make_simple_html_template(rendered_message.head_html, rendered_message.body_html)

        # Allow our settings to override the from address, because Braze requires specific configured from addresses,
        # which are tied to specific ip addresses that are "ip warmed" to help delivery of the emails not get sent
        # to promotional/spam inboxes.
        from_address = getattr(settings, self._FROM_EMAIL_SETTING, None) or self.get_from_address(message)

        logger = message.get_message_specific_logger(LOG)
        logger.debug('Sending to Braze')

        # https://www.braze.com/docs/api/endpoints/messaging/send_messages/post_send_messages/
        # https://www.braze.com/docs/api/objects_filters/email_object/
        response = requests.post(
            self._send_url(),
            headers=self._auth_headers(),
            json={
                'external_user_ids': [str(message.recipient.lms_user_id)],
                'recipient_subscription_state': 'all' if transactional else 'subscribed',
                'campaign_id': self._campaign_id(message.name),
                'messages': {
                    'email': {
                        'app_id': getattr(settings, self._APP_ID_SETTING),
                        'subject': self.get_subject(rendered_message),
                        'from': from_address,
                        'reply_to': message.options.get('reply_to'),
                        'body': body_html,
                        'plaintext_body': rendered_message.body,
                        'message_variation_id': self._variation_id(message.name),
                        'should_inline_css': False,  # this feature messes with inline CSS already in ACE templates
                    },
                },
            },
        )

        try:
            response.raise_for_status()
            logger.debug('Successfully sent to Braze (dispatch ID %s)', response.json()['dispatch_id'])

        except requests.exceptions.HTTPError as exc:
            # https://www.braze.com/docs/api/errors/
            message = response.json().get('message', 'Unknown error')
            logger.debug('Failed to send to Braze: %s', message)
            self._handle_error_response(response, message, exc)

    def overrides_delivery_for_message(self, message):
        # If we have a campaign configured for this message, let's deliver it ourselves, even if it's a transactional
        # message. Presumably that campaign is set up to ignore global delivery caps so that we don't drop such a
        # transactional message on the floor. This kind of configuration could be done to get nice email metrics.
        return self._campaign_id(message.name) is not None

    def _handle_error_response(self, response, message, exception):
        """
        Handle an error response from Braze, either by retrying or failing
        with an appropriate exception.

        Arguments:
            response: The HTTP response received from Braze.
            message: An error message from Braze.
            exception: The exception that triggered this error.
        """
        if response.status_code == 429 or 500 <= response.status_code < 600:
            next_attempt_time = get_current_time() + timedelta(
                seconds=NEXT_ATTEMPT_DELAY_SECONDS + random.uniform(-2, 2)
            )
            raise RecoverableChannelDeliveryError(
                f'Recoverable Braze error (status_code={response.status_code}): {message}',
                next_attempt_time
            ) from exception

        raise FatalChannelDeliveryError(
            f'Fatal Braze error (status_code={response.status_code}): {message}'
        ) from exception

    @classmethod
    def _auth_headers(cls):
        """Returns authorization headers suitable for passing to the requests library"""
        return {
            'Authorization': 'Bearer ' + getattr(settings, cls._API_KEY_SETTING),
        }

    @classmethod
    def _send_url(cls):
        """Returns the send-message API URL"""
        endpoint = getattr(settings, cls._ENDPOINT_SETTING)
        return f'https://{endpoint}/messages/send'

    @classmethod
    def _campaign_id(cls, name):
        """Returns the campaign ID for a given ACE message name or None if no match is found"""
        campaign = getattr(settings, cls._CAMPAIGNS_SETTING, {}).get(name)
        if campaign:
            return campaign.split(':')[0]
        return None

    @classmethod
    def _variation_id(cls, name):
        """Returns the variation ID for a given ACE message name or None if no match is found"""
        campaign = getattr(settings, cls._CAMPAIGNS_SETTING, {}).get(name)
        if campaign:
            campaign_parts = campaign.split(':')
            if len(campaign_parts) > 1:
                return campaign_parts[1]
        return None
