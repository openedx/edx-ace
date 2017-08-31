from edx_ace import delivery, policy, presentation
from edx_ace.errors import ChannelError


def send(msg):
    msg.report_basics()

    channels_for_message = policy.channels_for(msg)
    for channel in channels_for_message:
        try:
            rendered_message = presentation.render(channel, msg)
            delivery.deliver(channel, rendered_message, msg)
        except ChannelError as error:
            msg.report(
                u'channel_error',
                u'Unable to send over channel {}: {}'.format(channel, str(error))
            )
