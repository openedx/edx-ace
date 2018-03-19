# pylint: disable=missing-docstring
from __future__ import absolute_import

import datetime

from dateutil.tz import tzutc
from mock import Mock, call, patch, sentinel

from django.test import TestCase

from edx_ace.channel import ChannelType
from edx_ace.delivery import deliver
from edx_ace.errors import FatalChannelDeliveryError, RecoverableChannelDeliveryError
from edx_ace.message import Message
from edx_ace.recipient import Recipient


class TestDelivery(TestCase):
    def setUp(self):
        super(TestDelivery, self).setUp()

        self.mock_channel = Mock(
            name=u'test_channel',
            channel_type=ChannelType.EMAIL
        )
        self.recipient = Recipient(
            username=str(sentinel.username)
        )
        self.message = Message(
            app_label=str(sentinel.app_label),
            name=str(sentinel.name),
            options={
                u'from_address': u'bulk@example.com',
            },
            recipient=self.recipient,
        )
        self.current_time = datetime.datetime.utcnow().replace(tzinfo=tzutc())

    def test_happy_path(self):
        deliver(self.mock_channel, sentinel.rendered_email, self.message)
        self.mock_channel.deliver.assert_called_once_with(self.message, sentinel.rendered_email)

    def test_fatal_error(self):
        self.mock_channel.deliver.side_effect = FatalChannelDeliveryError(u'testing')
        with self.assertRaises(FatalChannelDeliveryError):
            deliver(self.mock_channel, sentinel.rendered_email, self.message)

    @patch(u'edx_ace.delivery.get_current_time')
    def test_custom_message_expiration(self, mock_get_current_time):
        self.message.expiration_time = self.current_time - datetime.timedelta(seconds=10)
        mock_get_current_time.return_value = self.current_time
        deliver(self.mock_channel, sentinel.rendered_email, self.message)
        assert not self.mock_channel.deliver.called

    @patch(u'edx_ace.delivery.time')
    @patch(u'edx_ace.delivery.get_current_time')
    def test_single_retry(self, mock_get_current_time, mock_time):
        mock_get_current_time.side_effect = [
            self.current_time,  # First call to figure out the expiration time
            self.current_time,  # Check to see if the message has expired
            self.current_time,  # Time after attempting the send
            self.current_time + datetime.timedelta(seconds=1.1),
        ]
        self.mock_channel.deliver.side_effect = [
            RecoverableChannelDeliveryError(u'Try again later', self.current_time + datetime.timedelta(seconds=1)),
            True
        ]
        deliver(self.mock_channel, sentinel.rendered_email, self.message)
        assert self.mock_channel.deliver.call_count == 2
        mock_time.sleep.assert_called_once_with(1)

    @patch(u'edx_ace.delivery.time')
    @patch(u'edx_ace.delivery.get_current_time')
    def test_next_attempt_time_after_expiration(self, mock_get_current_time, mock_time):
        self.message.expiration_time = self.current_time + datetime.timedelta(seconds=10)
        mock_get_current_time.return_value = self.current_time
        self.mock_channel.deliver.side_effect = [
            RecoverableChannelDeliveryError(u'Try again later', self.current_time + datetime.timedelta(seconds=11)),
        ]
        deliver(self.mock_channel, sentinel.rendered_email, self.message)
        assert not mock_time.sleep.called
        assert self.mock_channel.deliver.call_count == 1

    @patch(u'edx_ace.delivery.time')
    @patch(u'edx_ace.delivery.get_current_time')
    def test_multiple_retries(self, mock_get_current_time, mock_time):
        mock_get_current_time.side_effect = [
            self.current_time,  # First call to figure out the expiration time
            self.current_time,  # Check to see if the message has expired
            self.current_time,  # Time after attempting the send
            # This attempt fails and the app is instructed to wait for a second
            self.current_time + datetime.timedelta(seconds=1),  # Check again to see if it's expired
            self.current_time + datetime.timedelta(seconds=1),  # Time after second send attempt
            # This attempt fails and the app is instructed to wait for another second
            self.current_time + datetime.timedelta(seconds=2),  # Final expiration check
        ]
        self.mock_channel.deliver.side_effect = [
            RecoverableChannelDeliveryError(u'Try again later', self.current_time + datetime.timedelta(seconds=1)),
            RecoverableChannelDeliveryError(u'Try again later', self.current_time + datetime.timedelta(seconds=2)),
            True
        ]
        deliver(self.mock_channel, sentinel.rendered_email, self.message)
        assert mock_time.sleep.call_args_list == [call(1), call(1)]
        assert self.mock_channel.deliver.call_count == 3
