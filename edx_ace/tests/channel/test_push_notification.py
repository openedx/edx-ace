"""
Tests for the PushNotificationChannel class.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from firebase_admin.messaging import APNSConfig
from push_notifications.models import GCMDevice

from django.contrib.auth import get_user_model
from django.test import override_settings

from edx_ace.channel.push_notification import PushNotificationChannel
from edx_ace.errors import FatalChannelDeliveryError
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedPushNotification
from edx_ace.utils.date import get_current_time

User = get_user_model()


@pytest.mark.django_db
class TestPushNotificationChannel(TestCase):
    """
    Tests for the PushNotificationChannel class.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='username', email='email@example.com')
        self.lms_user_id = self.user.id
        self.msg_kwargs = {
            'app_label': 'test_app_label',
            'name': 'test_message',
            'expiration_time': get_current_time(),
            'context': {
                'key1': 'value1',
                'key2': 'value2',
            },
            'recipient': Recipient(
                lms_user_id=self.lms_user_id,
            )
        }

    @override_settings(PUSH_NOTIFICATIONS_SETTINGS={'CONFIG': 'push_notifications.conf.AppConfig'})
    def test_enabled(self):
        """
        Test that the channel is enabled when the settings are configured.
        """
        assert PushNotificationChannel.enabled()

    @override_settings(PUSH_NOTIFICATIONS_SETTINGS=None)
    def test_disabled(self):
        """
        Test that the channel is disabled when the settings are not configured.
        """
        assert not PushNotificationChannel.enabled()

    @patch('edx_ace.channel.push_notification.LOG')
    @patch('edx_ace.channel.push_notification.PushNotificationChannel.send_message')
    def test_deliver_no_device_tokens(self, mock_send_message, mock_log):
        """
        Test that the deliver method logs a message when the recipient has no push tokens.
        """
        with patch.object(PushNotificationChannel, 'get_user_device_tokens', return_value=[]):
            message = Message(options={}, **self.msg_kwargs)
            rendered_message = RenderedPushNotification(title='Test', body='This is a test.')

            channel = PushNotificationChannel()
            channel.deliver(message, rendered_message)

            mock_log.info.assert_called_with(
                'Recipient with ID %s has no push token. Skipping push notification.',
                self.lms_user_id
            )
            mock_send_message.assert_not_called()

    @patch('edx_ace.channel.push_notification.PushNotificationChannel.send_message')
    def test_deliver_with_device_tokens(self, mock_send_message):
        """
        Test that the deliver method sends a push notification for each device token.
        """
        with patch.object(PushNotificationChannel, 'get_user_device_tokens', return_value=['token1', 'token2']):
            message = Message(options={}, **self.msg_kwargs)
            rendered_message = RenderedPushNotification(title='Test', body='This is a test.')

            channel = PushNotificationChannel()
            channel.deliver(message, rendered_message)

            assert mock_send_message.call_count == 2

    @override_settings(FCM_APP_NAME='test_app')
    @patch('edx_ace.channel.push_notification.send_message')
    @patch('edx_ace.channel.push_notification.dict_to_fcm_message')
    @patch('edx_ace.channel.push_notification.PushNotificationChannel.collect_apns_config')
    def test_send_message_success(self, mock_collect_apns_config, mock_dict_to_fcm_message, mock_send_message):
        """
        Test that the send_message method sends a push notification successfully.
        """
        mock_dict_to_fcm_message.return_value = MagicMock()
        mock_collect_apns_config.return_value = MagicMock()

        message = Message(options={}, **self.msg_kwargs)
        rendered_message = RenderedPushNotification(title='Test', body='This is a test.')

        channel = PushNotificationChannel()
        channel.send_message(message, 'token', rendered_message)

        mock_send_message.assert_called_once()

    @override_settings(FCM_APP_NAME='test_app')
    @patch('edx_ace.channel.push_notification.send_message', side_effect=FatalChannelDeliveryError('Error'))
    @patch('edx_ace.channel.push_notification.dict_to_fcm_message')
    @patch('edx_ace.channel.push_notification.PushNotificationChannel.collect_apns_config')
    @patch('edx_ace.channel.push_notification.LOG')
    def test_send_message_failure(
        self, mock_log, mock_collect_apns_config, mock_dict_to_fcm_message, mock_send_message
    ):
        """
        Test that the send_message method logs an exception when an error occurs while sending the message.
        """
        mock_dict_to_fcm_message.return_value = MagicMock()
        mock_collect_apns_config.return_value = MagicMock()

        message = Message(options={}, **self.msg_kwargs)
        rendered_message = RenderedPushNotification(title='Test', body='This is a test.')

        channel = PushNotificationChannel()

        with pytest.raises(FatalChannelDeliveryError):
            channel.send_message(message, 'token', rendered_message)

        mock_send_message.assert_called_with('token', mock_dict_to_fcm_message.return_value, 'test_app')
        mock_log.exception.assert_called_with('Failed to send push notification to %s', 'token')

    def test_collect_apns_config(self):
        """
        Test that the collect_apns_config method returns an APNSConfig object with the correct headers.
        """
        notification_data = {'title': 'Test Title', 'body': 'Test Body'}

        apns_config = PushNotificationChannel.collect_apns_config(notification_data)

        assert isinstance(apns_config, APNSConfig)
        assert apns_config.headers['apns-priority'] == '5'
        assert apns_config.headers['apns-push-type'] == 'alert'

    def test_compress_spaces(self):
        """
        Test that the compress_spaces method removes extra spaces and newlines from a string.
        """
        compressed = PushNotificationChannel.compress_spaces('This   is a \n\n test.')
        assert compressed == 'This is a test.'

    def test_get_user_device_tokens(self):
        """
        Test that the get_user_device_tokens method returns the device tokens for a user.
        """
        gcm_device = GCMDevice.objects.create(user=self.user, registration_id='token1')

        channel = PushNotificationChannel()
        tokens = channel.get_user_device_tokens(self.lms_user_id)
        assert tokens == [gcm_device.registration_id]

    def test_get_user_device_tokens_no_tokens(self):
        """
        Test that the get_user_device_tokens method returns an empty list when the user has no device tokens.
        """
        channel = PushNotificationChannel()
        tokens = channel.get_user_device_tokens(self.lms_user_id)
        assert tokens == []
