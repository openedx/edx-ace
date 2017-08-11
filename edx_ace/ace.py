
from edx_ace.delivery import DeliveryStep
from edx_ace.policy import PolicyStep
from edx_ace.presentation import PresentationStep


def send(msg):
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
            cls.policy = PolicyStep()
        if cls.presentation is None:
            cls.presentation = PresentationStep()
        if cls.delivery is None:
            cls.delivery = DeliveryStep()


PipelineSteps.startup()
