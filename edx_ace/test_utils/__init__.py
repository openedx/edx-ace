"""
Test utilities.

Since py.test discourages putting __init__.py into test directory (i.e. making tests a package)
one cannot import from anywhere under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes). So this package is the place to put them.
"""
from edx_ace.channel import ChannelType

try:
    from unittest.mock import patch, Mock, sentinel, call
except ImportError:
    from mock import patch, Mock, sentinel, call

from edx_ace import policy  # lint-amnesty, pylint: disable=ungrouped-imports


class StubPolicy(policy.Policy):
    def __init__(self, deny_value):
        self.deny_value = frozenset(deny_value)

    def check(self, message):
        return policy.PolicyResult(deny=self.deny_value)


def patch_policies(test_case, policies):  # lint-amnesty, pylint: disable=missing-docstring
    patcher = patch(
        'edx_ace.policy.policies',
        return_value=policies
    )
    patcher.start()
    test_case.addCleanup(patcher.stop)


def patch_channels(test_case, channels):  # lint-amnesty, pylint: disable=missing-docstring
    patcher = patch(
        'edx_ace.delivery.channels',
        return_value={
            c.channel_type: c for c in channels
        }
    )
    patcher.start()
    test_case.addCleanup(patcher.stop)
