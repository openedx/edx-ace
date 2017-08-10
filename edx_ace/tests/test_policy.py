from collections import namedtuple
import ddt
from unittest import TestCase

from edx_ace.channel import ChannelType
import edx_ace.policy as policy


class StubPolicy(policy.Policy):
    def __init__(self, deny_value):
        self.deny_value = deny_value

    def check(self, message):
        return policy.PolicyResult(deny=self.deny_value)


ALL_ALLOWED_CHANNELS = {ChannelType.EMAIL, ChannelType.PUSH}


@ddt.ddt
class TestPolicy(TestCase):

    def setUp(self):
        self.policy_step = policy.PolicyStep()

    PolicyCase = namedtuple('PolicyCase', 'deny_values, expected_channels')

    @ddt.data(
        # allow all
        PolicyCase(deny_values=[set()], expected_channels=ALL_ALLOWED_CHANNELS),
        PolicyCase(deny_values=[{ChannelType.UNSPECIFIED}], expected_channels=ALL_ALLOWED_CHANNELS),

        # deny all
        PolicyCase(deny_values=[{ChannelType.ALL}], expected_channels=set()),

        # deny only email
        PolicyCase(deny_values=[{ChannelType.EMAIL}], expected_channels={ChannelType.PUSH}),         # single policy
        PolicyCase(deny_values=[{ChannelType.EMAIL}, set()], expected_channels={ChannelType.PUSH}),  # multiple policies

        # deny both email and push
        PolicyCase(deny_values=[{ChannelType.EMAIL, ChannelType.PUSH}], expected_channels=set()),    # single policy
        PolicyCase(deny_values=[{ChannelType.EMAIL}, {ChannelType.PUSH}], expected_channels=set()),  # multiple policies

        # deny all and email
        PolicyCase(deny_values=[{ChannelType.EMAIL}, {ChannelType.ALL}], expected_channels=set()),
    )
    @ddt.unpack
    def test_policies(self, deny_values, expected_channels):
        policies = [StubPolicy(deny_value) for deny_value in deny_values]
        self.policy_step.policies = policies
        channels = self.policy_step.channels_for(message=None)
        self.assertEquals(channels, expected_channels)
