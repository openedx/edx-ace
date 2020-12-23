"""
Tests of :mod:`edx_ace.policy`.
"""
from collections import namedtuple
from unittest import TestCase, mock

import ddt

from edx_ace import policy
from edx_ace.channel import ChannelType
from edx_ace.test_utils import StubPolicy


@ddt.ddt
class TestPolicy(TestCase):
    """ Test Policies. """
    PolicyCase = namedtuple('PolicyCase', 'deny_values, expected_channels')

    @ddt.data(
        # allow all
        PolicyCase(deny_values=[set()], expected_channels=set(ChannelType)),

        # deny all
        PolicyCase(deny_values=[set(ChannelType)], expected_channels=set()),

        # deny only email
        PolicyCase(deny_values=[{ChannelType.EMAIL}], expected_channels={ChannelType.PUSH}),  # single policy
        PolicyCase(deny_values=[{ChannelType.EMAIL}, set()], expected_channels={ChannelType.PUSH}),  # multiple policies

        # deny both email and push
        PolicyCase(deny_values=[{ChannelType.EMAIL, ChannelType.PUSH}], expected_channels=set()),  # single policy
        PolicyCase(deny_values=[{ChannelType.EMAIL}, {ChannelType.PUSH}], expected_channels=set()),  # multiple policies

        # deny all and email
        PolicyCase(deny_values=[{ChannelType.EMAIL}, set(ChannelType)], expected_channels=set()),
    )
    @ddt.unpack
    def test_policies(self, deny_values, expected_channels):
        policies = [StubPolicy(deny_value) for deny_value in deny_values]
        with mock.patch.object(policy, 'policies', return_value=policies):
            channels = policy.channels_for(message=mock.Mock())
            self.assertEqual(channels, expected_channels)
