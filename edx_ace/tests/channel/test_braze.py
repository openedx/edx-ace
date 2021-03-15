"""Unit tests for braze.py"""
from unittest.mock import Mock, patch

import ddt
import requests

from django.test import TestCase, override_settings

from edx_ace.channel.braze import BrazeEmailChannel
from edx_ace.errors import FatalChannelDeliveryError, RecoverableChannelDeliveryError
from edx_ace.message import Message
from edx_ace.presentation import render
from edx_ace.recipient import Recipient


@ddt.ddt
@override_settings(
    ACE_CHANNEL_BRAZE_API_KEY='test-api-key',
    ACE_CHANNEL_BRAZE_APP_ID='test-app-id',
    ACE_CHANNEL_BRAZE_REST_ENDPOINT='rest.braze.com',
    ACE_DEFAULT_EXPIRATION_DELAY=0,
)
class TestBrazeChannel(TestCase):
    """Tests for the braze channel"""

    def setUp(self):
        self.channel = BrazeEmailChannel()

    def deliver_email(self, lms_user_id=123, options=None, response_code=200, response_message='Success!'):
        """Sets up all the mocks for a single email"""
        message = Message(
            app_label='testapp',
            name='testmessage',
            options=options or {},
            recipient=Recipient(lms_user_id=lms_user_id, email_address='mr@robot.io'),
        )
        rendered_message = render(self.channel, message)

        with patch('edx_ace.channel.braze.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = response_code
            mock_response.json.return_value = {'message': response_message, 'dispatch_id': 'test-dispatch-id'}
            if response_code >= 400:
                mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
            mock_post.return_value = mock_response
            self.channel.deliver(message, rendered_message)  # direct, so we can catch interesting exceptions ourselves

        return mock_post

    def test_happy_path(self):
        """Basic email send, no special settings"""
        mock_post = self.deliver_email()

        assert mock_post.call_count == 1
        assert mock_post.call_args[0] == ('https://rest.braze.com/messages/send',)
        assert mock_post.call_args[1] == {
            'headers': {'Authorization': 'Bearer test-api-key'},
            'json': {
                'external_user_ids': ['123'],
                'recipient_subscription_state': 'subscribed',
                'campaign_id': None,
                'messages': {
                    'email': {
                        'app_id': 'test-app-id',
                        'subject': 'template subject.txt',
                        'from': 'webmaster@localhost',
                        'reply_to': None,
                        'body': """<!DOCTYPE html>
<html>
  <head>
    template head.html\n
  </head>
  <body>
    template body.html\n\n\n\n
<tr>
    <!-- Actions -->
    <td style="padding-bottom: 20px;">
        
            <p>
                <a href="{{${set_user_to_unsubscribed_url}}}" style="color: #960909">
                    <font color="#960909"><b>Unsubscribe from this list</b></font>
                </a>
            </p>
        
    </td>
</tr>\n\n
  </body>
</html>""",  # noqa
                        'plaintext_body': 'template body.txt',
                        'message_variation_id': None,
                        'should_inline_css': False,
                    },
                },
            },
        }

    @ddt.data(
        (None, None, None),
        ('', None, None),
        ('campaign_id', 'campaign_id', None),
        ('campaign_id:variation_id', 'campaign_id', 'variation_id'),
    )
    @ddt.unpack
    def test_campaigns(self, campaign_setting, campaign_id, variation_id):
        """If set, we should pass on the campaign identifiers"""
        full_settings = {
            'testmessage': campaign_setting,
        }
        with override_settings(ACE_CHANNEL_BRAZE_CAMPAIGNS=full_settings):
            mock_post = self.deliver_email()
        assert mock_post.call_args[1]['json']['campaign_id'] == campaign_id
        assert mock_post.call_args[1]['json']['messages']['email']['message_variation_id'] == variation_id

    def test_transactional(self):
        """Transactional emails have different subscriber settings"""
        mock_post = self.deliver_email(options={'transactional': True})
        assert mock_post.call_args[1]['json']['recipient_subscription_state'] == 'all'

    def test_from_address(self):
        """Can set a from address in options"""
        mock_post = self.deliver_email(options={'from_address': 'testing@example.com'})
        assert mock_post.call_args[1]['json']['messages']['email']['from'] == 'testing@example.com'

    def test_reply_to(self):
        """Can set a reply-to address in options"""
        mock_post = self.deliver_email(options={'reply_to': 'reply@example.com'})
        assert mock_post.call_args[1]['json']['messages']['email']['reply_to'] == 'reply@example.com'

    @ddt.data(0, None)
    def test_lms_user_id_fallback(self, user_id):
        """Use django instead if we can't find user id"""
        with patch('edx_ace.channel.braze.DjangoEmailChannel') as mock_django:
            mock_post = self.deliver_email(lms_user_id=user_id)

        assert mock_post.call_count == 0
        assert mock_django.call_count == 1

    @ddt.data(
        (400, FatalChannelDeliveryError),
        (429, RecoverableChannelDeliveryError),
        (500, RecoverableChannelDeliveryError),
    )
    @ddt.unpack
    def test_status_raises(self, code, exception):
        with self.assertRaisesRegex(exception, 'error will robinson'):
            self.deliver_email(response_code=code, response_message='error will robinson')

    @override_settings(ACE_CHANNEL_BRAZE_API_KEY='')
    def test_disabled(self):
        assert not self.channel.enabled()
        with self.assertRaisesRegex(FatalChannelDeliveryError, 'disabled'):
            self.deliver_email()
