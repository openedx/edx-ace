"""
:mod:`edx_ace.recipient` contains :class:`Recipient`, which captures all targeting
information needed to deliver a message to some user.
"""
import attr

from edx_ace.serialization import MessageAttributeSerializationMixin


@attr.s
class Recipient(MessageAttributeSerializationMixin):
    """
    The target for a message.

    Arguments:
        lms_user_id (int): The LMS user ID of the intended recipient.
        email_address (str): The email address of the intended recipient. Optional.
    """
    lms_user_id = attr.ib()
    email_address = attr.ib(default=None)
