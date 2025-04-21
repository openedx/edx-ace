"""
Tests for TestBrazePushNotificationChannel.
"""
from unittest.mock import MagicMock, patch

import pytest

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from edx_ace.channel.braze_push_notification import BrazePushNotificationChannel
from edx_ace.message import Message
from edx_ace.recipient import Recipient
from edx_ace.renderers import RenderedBrazePushNotification

BRAZE_URL = "https://example.braze.com"
API_KEY = "test-api-key"
User = get_user_model()


@pytest.mark.django_db
@override_settings(
    EDX_BRAZE_API_KEY=API_KEY,
    EDX_BRAZE_API_SERVER=BRAZE_URL,
)
class TestBrazePushNotificationChannel(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='username', email='email@example.com')
        self.lms_user_id = self.user.id
        self.mocked_post_data = {
                'notification_type': 'new_response',
                'course_id': 'course-v1:edX+DemoX+Demo_Course',
                'content_url': 'http://localhost',
                'replier_name': 'verified',
                'post_title': 'New test response',
                'course_name': 'Demonstration Course',
                'thread_id': '67bedeb9ceb0b101343294c5',
                'topic_id': 'i4x-edx-eiorguegnru-course-foobarbaz',
                'response_id': '67ffa1f1ceb0b10134db3d8e',
                'comment_id': None,
                'strong': 'strong', 'p': 'p'
        }

        self.mocked_payload = {
            'campaign_id': '1234test',
            'trigger_properties': self.mocked_post_data,
            'emails': ['edx@example.com']
        }

    @patch('edx_ace.channel.braze_push_notification.get_braze_client', return_value=True)
    def test_enabled(self, mock_braze_client):
        """
        Test that the channel is enabled when the settings are configured.
        """
        assert BrazePushNotificationChannel.enabled()

    @patch('edx_ace.channel.braze_push_notification.get_braze_client', return_value=False)
    def test_disabled(self, mock_braze_client):
        """
        Test that the channel is disabled when the settings are not configured.
        """
        assert not BrazePushNotificationChannel.enabled()

    @override_settings(ACE_CHANNEL_BRAZE_PUSH_CAMPAIGNS={'new_response': "1234test"})
    @patch('edx_ace.channel.braze_push_notification.get_braze_client')
    def test_deliver_success(self, mock_braze_function):
        mock_braze_client = MagicMock()
        mock_braze_function.return_value = mock_braze_client
        mock_braze_client.send_campaign_message = MagicMock(return_value=True)

        rendered_message = RenderedBrazePushNotification()
        message = Message(
            app_label='testapp',
            name="test_braze",
            recipient=Recipient(lms_user_id="1", email_address="user@example.com"),
            context={'post_data': self.mocked_post_data},
            options={'emails': ['edx@example.com'], 'braze_campaign': 'new_response'}
        )
        channel = BrazePushNotificationChannel()
        channel.deliver(message, rendered_message)
        mock_braze_client.send_campaign_message.assert_called_once()
        args, kwargs = mock_braze_client.send_campaign_message.call_args

        # Verify the payload
        self.assertEqual(kwargs, self.mocked_payload)

    @patch('edx_ace.channel.braze_push_notification.get_braze_client')
    def test_campaign_not_configured(self, mock_braze_function):
        mock_braze_client = MagicMock()
        mock_braze_function.return_value = mock_braze_client
        mock_braze_client.send_campaign_message = MagicMock(return_value=True)

        rendered_message = RenderedBrazePushNotification()
        message = Message(
            app_label='testapp',
            name="test_braze",
            recipient=Recipient(lms_user_id="1", email_address="user@example.com"),
            context={'post_data': self.mocked_post_data},
            options={'emails': ['edx@example.com'], 'braze_campaign': 'new_response'}
        )
        channel = BrazePushNotificationChannel()
        channel.deliver(message, rendered_message)
        mock_braze_client.send_campaign_message.assert_not_called()
