u"""
Test utilities.

Since py.test discourages putting __init__.py into test directory (i.e. making tests a package)
one cannot import from anywhere under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes). So this package is the place to put them.
"""
from __future__ import absolute_import

from mock import patch

from edx_ace import policy


class StubPolicy(policy.Policy):
    def __init__(self, deny_value):
        self.deny_value = frozenset(deny_value)

    def check(self, message):
        return policy.PolicyResult(deny=self.deny_value)


def patch_policies(test_case, policies):
    u"""
    Set active policies for the duration of a test.

    Arguments:
        test_case (:class:`unittest.TestCase`): The test case that is running
        policies: The set of active policies to return from :func:`edx_ace.policy.policies`
    """
    patcher = patch(
        u'edx_ace.policy.policies',
        return_value=policies
    )
    patcher.start()
    test_case.addCleanup(patcher.stop)
