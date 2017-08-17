from collections import namedtuple
import ddt
from unittest import TestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


from edx_ace.channel import ChannelType
from edx_ace import policy


class StubPolicy(policy.Policy):
    def __init__(self, deny_value):
        self.deny_value = deny_value

    def check(self, message):
        return policy.PolicyResult(deny=self.deny_value)


ALL_ALLOWED_CHANNELS = {ChannelType.EMAIL, ChannelType.PUSH}


@ddt.ddt
class TestPolicy(TestCase):

    PolicyCase = namedtuple('PolicyCase', 'deny_values, expected_channels')

    @ddt.data(
        # allow all
        PolicyCase(deny_values=[set()], expected_channels=ALL_ALLOWED_CHANNELS),

        # deny all
        PolicyCase(deny_values=[set(ChannelType)], expected_channels=set()),

        # deny only email
        PolicyCase(deny_values=[{ChannelType.EMAIL}], expected_channels={ChannelType.PUSH}),         # single policy
        PolicyCase(deny_values=[{ChannelType.EMAIL}, set()], expected_channels={ChannelType.PUSH}),  # multiple policies

        # deny both email and push
        PolicyCase(deny_values=[{ChannelType.EMAIL, ChannelType.PUSH}], expected_channels=set()),    # single policy
        PolicyCase(deny_values=[{ChannelType.EMAIL}, {ChannelType.PUSH}], expected_channels=set()),  # multiple policies

        # deny all and email
        PolicyCase(deny_values=[{ChannelType.EMAIL}, set(ChannelType)], expected_channels=set()),
    )
    @ddt.unpack
    def test_policies(self, deny_values, expected_channels):
        policies = [StubPolicy(deny_value) for deny_value in deny_values]
        with patch.object(policy, 'policies', return_value=policies):
            channels = policy.channels_for(message=None)
            self.assertEquals(channels, expected_channels)
