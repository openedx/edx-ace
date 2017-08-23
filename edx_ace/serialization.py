# lint-amnesty, pylint: disable=missing-docstring
import attr
import json  # lint-amnesty, pylint: disable=wrong-import-order
from uuid import UUID  # lint-amnesty, pylint: disable=wrong-import-order
import six

from edx_ace.utils import date


@six.python_2_unicode_compatible  # lint-amnesty, pylint: disable=missing-docstring
class MessageAttributeSerializationMixin(object):

    def __str__(self):
        return json.dumps(self, cls=MessageEncoder)

    @classmethod
    def from_string(cls, string_value):  # lint-amnesty, pylint: disable=missing-docstring
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
    def _deserialize_field(cls, field_name, field_value):  # pylint: disable=cyclic-import
        # We have to import these here to avoid a circular dependency since these classes use this mixin.
        from edx_ace.recipient import Recipient
        from edx_ace.message import Message

        if field_name == 'expiration_time':
            return date.deserialize(field_value)
        elif field_name == 'uuid':
            return UUID(field_value)
        # TODO(later): should this be more dynamic?
        elif field_name == 'message':
            return Message(**field_value)
        elif field_name == 'recipient':
            return Recipient(**field_value)
        else:
            return field_value


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):  # lint-amnesty, pylint: disable=arguments-differ, method-hidden
        if isinstance(obj, UUID):
            return six.text_type(obj)
        elif isinstance(obj, date.datetime):
            return date.serialize(obj)
        elif hasattr(obj, 'to_json'):
            return obj.to_json()
        else:
            return super(MessageEncoder, self).default(obj)
