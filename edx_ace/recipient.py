import attr
from edx_ace.serialization import MessageAttributeSerializationMixin


@attr.s
class Recipient(MessageAttributeSerializationMixin):
    username = attr.ib()
    fields = attr.ib(attr.Factory(dict))
