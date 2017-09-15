# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import six

from edx_ace import delivery, policy, presentation
from edx_ace.errors import ChannelError


def send(msg):
    u"""
    Send a message to a recipient.

    Calling this method will result in an attempt being made to deliver the provided message to the recipient. Depending
    on the configured policies, it may be transmitted to them over one or more channels (email, sms, push etc).

    The message must have valid values for all required fields in order for it to be sent. Different channels have
    different requirements, so care must be taken to ensure that all of the needed information is present in the message
    before calling ``ace.send()``.

    Args:
        msg (Message): The message to send.
    """
    msg.report_basics()

    channels_for_message = policy.channels_for(msg)
    for channel_type in channels_for_message:
        try:
            rendered_message = presentation.render(channel_type, msg)
            delivery.deliver(channel_type, rendered_message, msg)
        except ChannelError as error:
            msg.report(
                u'{channel_type}_error'.format(channel_type=channel_type),
                six.text_type(error)
            )
