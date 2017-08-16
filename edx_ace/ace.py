import logging

from edx_ace.delivery import DeliveryStep
from edx_ace.errors import UnsupportedChannelError
from edx_ace.policy import PolicyStep
from edx_ace.presentation import PresentationStep


LOG = logging.getLogger(__name__)


def send(msg):
    channels_for_message = PipelineSteps.policy.channels_for(msg)
    for channel in channels_for_message:
        try:
            rendered_message = PipelineSteps.presentation.render(channel, msg)
        except UnsupportedChannelError:
            LOG.exception("Unable to render message %s for channel %s", msg, channel)
        else:
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
