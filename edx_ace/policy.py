from abc import ABCMeta, abstractmethod
from edx_ace.ace_step import ACEStep


class Policy(ACEStep):
    __metaclass__ = ABCMeta

    @abstractmethod
    def channels_for(self, message):
        pass
