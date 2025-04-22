"""
Channel for sending push notifications using braze.
"""
import logging

from django.conf import settings

from edx_ace.channel import Channel, ChannelType
from edx_ace.message import Message
from edx_ace.renderers import RenderedPushNotification
from edx_ace.utils.braze import get_braze_client

LOG = logging.getLogger(__name__)


class BrazePushNotificationChannel(Channel):
    """
    A channel for sending push notifications using braze.
    """
    channel_type = ChannelType.BRAZE_PUSH
    _CAMPAIGNS_SETTING = 'ACE_CHANNEL_BRAZE_PUSH_CAMPAIGNS'

    @classmethod
    def enabled(cls):
        """
        Returns: True iff braze client is available.
        """
        return bool(get_braze_client())

    def deliver(self, message: Message, rendered_message: RenderedPushNotification) -> None:
        """
        Transmit a rendered message to a recipient.

        Args:
            message: The message to transmit.
            rendered_message: The rendered content of the message that has been personalized
                for this particular recipient.
        """
        braze_campaign = message.options['braze_campaign']
        emails = message.options.get('emails') or [message.recipient.email_address]
        campaign_id = self._campaign_id(braze_campaign)
        if not campaign_id:
            LOG.info('Could not find braze campaign for notification %s', braze_campaign)
            return

        try:
            braze_client = get_braze_client()
            braze_client.send_campaign_message(
                campaign_id=campaign_id,
                trigger_properties=message.context['post_data'],
                emails=emails
            )
            LOG.info('Sent push notification for %s with Braze', braze_campaign)
        except Exception as exc:  # pylint: disable=broad-except
            LOG.error(
                'Unable to send push notification for %s with Braze. Reason: %s',
                braze_campaign,
                str(exc)
            )

    @classmethod
    def _campaign_id(cls, braze_campaign):
        """Returns the campaign ID for a given ACE message name or None if no match is found"""
        return getattr(settings, cls._CAMPAIGNS_SETTING, {}).get(braze_campaign)
