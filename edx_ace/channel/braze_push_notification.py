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
    braze_client = get_braze_client()
    _CAMPAIGNS_SETTING = 'ACE_CHANNEL_BRAZE_PUSH_CAMPAIGNS'

    @classmethod
    def enabled(cls):
        """
        Returns: True iff braze client is available.
        """
        return bool(cls.braze_client)

    def deliver(self, message: Message, rendered_message: RenderedPushNotification) -> None:
        """
        Transmit a rendered message to a recipient.

        Args:
            message: The message to transmit.
            rendered_message: The rendered content of the message that has been personalized
                for this particular recipient.
        """
        notification_type = message.context['post_data']['notification_type']
        campaign_id = self._campaign_id(notification_type)
        if not campaign_id:
            LOG.info('Could not find braze campaign for notification %s', notification_type)
            return

        emails = message.context['emails']

        try:
            self.braze_client.send_campaign_message(
                campaign_id=campaign_id,
                trigger_properties=message.context['post_data'],
                emails=emails
            )
            LOG.info('Sent mobile notification for %s with Braze', notification_type)
        except Exception as exc:  # pylint: disable=broad-except
            LOG.error(
                'Unable to send mobile notification for %s with Braze. Reason: %s',
                notification_type,
                str(exc)
            )

    @classmethod
    def _campaign_id(cls, name):
        """Returns the campaign ID for a given ACE message name or None if no match is found"""
        return getattr(settings, cls._CAMPAIGNS_SETTING, {}).get(name)
