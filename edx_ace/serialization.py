import json
from uuid import UUID

import attr
import six

from edx_ace.utils import date


@six.python_2_unicode_compatible
class MessageAttributeSerializationMixin(object):
    def __str__(self):
        return json.dumps(self, cls=MessageEncoder)

    @classmethod
    def from_string(cls, string_value):
        fields = json.loads(
            string_value,
            object_hook=cls._deserialize,
        )
        uuid = fields.pop('uuid')
        instance = cls(**fields)
        instance.uuid = uuid
        return instance

    def to_json(self):
        return attr.asdict(self)

    @classmethod
    def _deserialize(cls, json_value):
        fields = json_value.copy()
        for field_name, field_value in six.iteritems(fields):
            fields[field_name] = cls._deserialize_field(field_name, field_value)
        return fields

    @classmethod
    def _deserialize_field(cls, field_name, field_value):
        # We have to import these here to avoid a circular dependency since these classes use this mixin.
        from edx_ace.recipient import Recipient
        from edx_ace.message import Message

        if field_value is None:
            return None

        if field_name == 'expiration_time':
            return date.deserialize(field_value)
        elif field_name in ('uuid', 'send_uuid'):
            return UUID(field_value)
        # TODO(later): should this be more dynamic?
        elif field_name == 'message':
            return Message(**field_value)
        elif field_name == 'recipient':
            return Recipient(**field_value)
        else:
            return field_value


class MessageEncoder(json.JSONEncoder):
    # The Pylint error is disabled because of a bug in Pylint.
    # See https://github.com/PyCQA/pylint/issues/414
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, UUID):
            return six.text_type(o)
        elif isinstance(o, date.datetime):
            return date.serialize(o)
        elif hasattr(o, 'to_json'):
            return o.to_json()
        else:
            return super(MessageEncoder, self).default(o)
