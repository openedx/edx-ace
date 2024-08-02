"""
The main entry point for sending messages with ACE.

Usage:

.. code-block:: python

    from edx_ace import ace
    from edx_ace.messages import Message

    msg = Message(
        name="test_message",
        app_label="my_app",
        recipient=Recipient(lms_user_id='123456', email='a_user@example.com'),
        language='en',
        context={
            'stuff': 'to personalize the message',
        }
    )
    ace.send(msg)
"""
import logging

from django.template import TemplateDoesNotExist

from edx_ace import delivery, policy, presentation
from edx_ace.channel import get_channel_for_message
from edx_ace.errors import ChannelError, UnsupportedChannelError

log = logging.getLogger(__name__)


def send(msg, limit_to_channels=None):
    """
    Send a message to a recipient.

    Calling this method will result in an attempt being made to deliver the provided message to the recipient. Depending
    on the configured policies, it may be transmitted to them over one or more channels (email, sms, push etc).

    The message must have valid values for all required fields in order for it to be sent. Different channels have
    different requirements, so care must be taken to ensure that all of the needed information is present in the message
    before calling ``ace.send()``.

    Args:
        msg (Message): The message to send.
        limit_to_channels (list of ChannelType, optional): If provided, only send the message over the specified
            channels. If not provided, the message will be sent over all channels that the policies allow.
    """
    msg.report_basics()

    channels_for_message = policy.channels_for(msg)

    for channel_type in channels_for_message:
        if limit_to_channels and channel_type not in limit_to_channels:
            log.debug('Skipping channel %s', channel_type)

        try:
            channel = get_channel_for_message(channel_type, msg)
        except UnsupportedChannelError:
            continue

        try:
            rendered_message = presentation.render(channel, msg)
        except TemplateDoesNotExist as error:
            msg.report(
                'template_error',
                'Unable to send message because template not found\n' + str(error)
            )
            continue

        try:
            delivery.deliver(channel, rendered_message, msg)
        except ChannelError as error:
            msg.report(
                f'{channel_type}_error',
                str(error)
            )
