from edx_ace.message import Message
from edx.ace.policy import Policy
from edx.ace.presentation import Presentation
from edx.ace.delivery import Delivery


def send(msg):
    assert isinstance(msg, Message)

    channels_for_message = PipelineSteps.policy.channels_for(msg)
    for channel in channels_for_message:
        rendered_message = PipelineSteps.presentation.render(channel, msg)
        PipelineSteps.delivery.deliver(channel, rendered_message, msg)


class PipelineSteps(object):
    policy = None
    presentation = None
    delivery = None

    @classmethod
    def startup(cls):
        if cls.policy is None:
            cls.policy = Policy()
        if cls.presentation is None:
            cls.presentation = Presentation()
        if cls.delivery is None:
            cls.delivery = Delivery()


PipelineSteps.startup()
