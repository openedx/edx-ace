from abc import ABCMeta, abstractmethod
from edx_ace.ace_step import ACEStep


class RecipientResolver(ACEStep):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, msg_template, *args, **kwargs):
        pass
