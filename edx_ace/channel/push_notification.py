"""
Channel for sending push notifications.
"""
import logging
import re

from firebase_admin.messaging import APNSConfig, APNSPayload, Aps, ApsAlert
from push_notifications.gcm import dict_to_fcm_message, send_message
from push_notifications.models import GCMDevice

from django.conf import settings

from edx_ace.channel import Channel, ChannelType
from edx_ace.errors import FatalChannelDeliveryError
from edx_ace.message import Message
from edx_ace.renderers import RenderedPushNotification

LOG = logging.getLogger(__name__)
APNS_DEFAULT_PRIORITY = '5'
APNS_DEFAULT_PUSH_TYPE = 'alert'


class PushNotificationChannel(Channel):
    """
    A channel for sending push notifications.
    """

    channel_type = ChannelType.PUSH

    @classmethod
    def enabled(cls):
        """
        Returns true if the push notification settings are configured.
        """
        return bool(getattr(settings, 'PUSH_NOTIFICATIONS_SETTINGS', None))

    def deliver(self, message: Message, rendered_message: RenderedPushNotification) -> None:
        """
        Transmit a rendered message to a recipient.

        Args:
            message: The message to transmit.
            rendered_message: The rendered content of the message that has been personalized
                for this particular recipient.
        """
        device_tokens = self.get_user_device_tokens(message.recipient.lms_user_id)
        if not device_tokens:
            LOG.info(
                'Recipient with ID %s has no push token. Skipping push notification.',
                message.recipient.lms_user_id
            )
            return

        for token in device_tokens:
            self.send_message(message, token, rendered_message)

    def send_message(self, message: Message, token: str, rendered_message: RenderedPushNotification) -> None:
        """
        Send a push notification to a device by token.
        """
        notification_data = {
            'title': self.compress_spaces(rendered_message.title),
            'body': self.compress_spaces(rendered_message.body),
            'notification_key': token,
            **message.context.get('push_notification_extra_context', {}),
        }
        message = dict_to_fcm_message(notification_data)
        # Note: By default dict_to_fcm_message does not support APNS configuration,
        #   only Android configuration, so we need to collect and set it manually.
        apns_config = self.collect_apns_config(notification_data)
        message.apns = apns_config
        try:
            send_message(token, message, settings.FCM_APP_NAME)
        except Exception as e:
            LOG.exception('Failed to send push notification to %s', token)
            raise FatalChannelDeliveryError(f'Failed to send push notification to {token}') from e

    @staticmethod
    def collect_apns_config(notification_data: dict) -> APNSConfig:
        """
        Collect APNS configuration with payload for the push notification.

        This APNSConfig must be set to notifications for Firebase to send push notifications to iOS devices.
        Notification has default priority and visibility settings, described in Apple's documentation.
        (https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns)
        """
        apns_alert = ApsAlert(title=notification_data['title'], body=notification_data['body'])
        aps = Aps(alert=apns_alert, sound='default')
        return APNSConfig(
            headers={'apns-priority': APNS_DEFAULT_PRIORITY, 'apns-push-type': APNS_DEFAULT_PUSH_TYPE},
            payload=APNSPayload(aps)
        )

    @staticmethod
    def get_user_device_tokens(user_id: int) -> list:
        """
        Get the device tokens for a user.
        """
        return list(GCMDevice.objects.filter(
            user_id=user_id,
            cloud_message_type='FCM',
            active=True,
        ).values_list('registration_id', flat=True))

    @staticmethod
    def compress_spaces(html_str: str) -> str:
        """
        Compress spaces and remove newlines to make it easier to author templates.
        """
        return re.sub('\\s+', ' ', html_str, re.UNICODE).strip()
