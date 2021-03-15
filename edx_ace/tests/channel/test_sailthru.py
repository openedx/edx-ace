# pylint: disable=missing-docstring
from unittest.mock import patch

import ddt
from edx_toggles.toggles.testutils import override_waffle_flag

from django.test import TestCase, override_settings

from edx_ace.channel.sailthru import BRAZE_ROLLOUT_FLAG, SailthruEmailChannel
from edx_ace.delivery import deliver
from edx_ace.message import Message
from edx_ace.presentation import render
from edx_ace.recipient import Recipient


@ddt.ddt
class TestSailthruChannel(TestCase):

    def setUp(self):
        self.channel = SailthruEmailChannel()

    def test_render_email_with_sailthru(self):
        message = Message(
            app_label='testapp',
            name='testmessage',
            options={},
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )

        rendered_email = render(self.channel, message)

        assert '{beacon_src}' in rendered_email.body_html
        assert '{view_url}' in rendered_email.body_html
        assert '{optout_confirm_url}' in rendered_email.body_html

    @override_settings(
        ACE_CHANNEL_SAILTHRU_DEBUG=False,
    )
    @ddt.data(
        ({'from_address': 'custom@example.com'}, {'behalf_email': 'custom@example.com'}),
        ({'reply_to': 'student@example.com'}, {'behalf_email': 'student@example.com'}),
        ({'irrelevant': 'test'}, {}),
        ({}, {}),
    )
    @ddt.unpack
    def test_on_behalf_option_with_sailthru(self, message_options, expected_options):
        """
        Tests sailthru send API is called with on_behalf option
        """
        message = Message(
            app_label='testapp',
            name='testmessage',
            options=message_options,
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )
        rendered_email = render(self.channel, message)

        with patch('edx_ace.channel.sailthru.SailthruClient.send') as mock_send:
            deliver(self.channel, rendered_email, message)
            self.assertEqual(mock_send.call_args_list[0][1]['options'], expected_options)

    @override_settings(
        ACE_CHANNEL_BRAZE_API_KEY='test-api-key',
        ACE_CHANNEL_BRAZE_APP_ID='test-app-id',
        ACE_CHANNEL_BRAZE_REST_ENDPOINT='rest.braze.com',
        ACE_CHANNEL_SAILTHRU_DEBUG=False,
    )
    @ddt.data(True, False)
    def test_braze_rollout_flag(self, enabled):
        message = Message(
            app_label='testapp',
            name='testmessage',
            recipient=Recipient(lms_user_id=123, email_address='mr@robot.io'),
        )
        rendered_email = render(self.channel, message)

        with patch('edx_ace.channel.sailthru.SailthruClient.send') as mock_send:
            with patch('edx_ace.channel.sailthru.BrazeEmailChannel') as mock_braze:
                with override_waffle_flag(BRAZE_ROLLOUT_FLAG, active=enabled):
                    deliver(self.channel, rendered_email, message)
                    assert mock_braze.call_count == (1 if enabled else 0)
                    assert mock_send.call_count == (0 if enabled else 1)

    @override_settings(
        ACE_CHANNEL_BRAZE_API_KEY='test-api-key',
        ACE_CHANNEL_BRAZE_APP_ID='test-app-id',
        ACE_CHANNEL_BRAZE_REST_ENDPOINT='rest.braze.com',
        ACE_CHANNEL_SAILTHRU_DEBUG=False,
    )
    @override_waffle_flag(BRAZE_ROLLOUT_FLAG, active=True)
    def test_braze_rollout_properties(self):
        assert self.channel.action_links == [('{{${set_user_to_unsubscribed_url}}}', 'Unsubscribe from this list')]
        assert self.channel.tracker_image_sources == []
