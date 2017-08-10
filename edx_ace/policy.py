from abc import ABCMeta, abstractmethod
import attr
from edx_ace.ace_step import ACEStep
from edx_ace.channel import ChannelTypes


@attr.s
class PolicyResult(object):
    deny = attr.ib(attr.validators.in_(ChannelTypes))


class Policy(ACEStep):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, message):
        """
        Returns PolicyResult.
        """
        pass
