from abc import ABCMeta, abstractmethod
from edx_ace.ace_step import ACEStep


class Presentation(ACEStep):
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self, channel, msg):
        pass
