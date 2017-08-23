# lint-amnesty, pylint: disable=missing-docstring
import attr
from edx_ace.serialization import MessageAttributeSerializationMixin


@attr.s
class Recipient(MessageAttributeSerializationMixin):
    username = attr.ib()
    email_address = attr.ib(default=None)
