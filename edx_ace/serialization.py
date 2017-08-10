import attr
import json
from uuid import UUID

from edx_ace.utils import date


class MessageAttributeSerializationMixin(object):

    def __unicode__(self):
        return json.dumps(self, cls=MessageEncoder)

    @classmethod
    def from_string(cls, string_value):
        fields = json.loads(
            string_value,
            object_hook=cls._deserialize,
        )
        return cls(**fields)

    def to_json(self):
        return attr.asdict(self)

    @classmethod
    def _deserialize(cls, json_value):
        fields = json_value.copy()
        for field_name, field_value in fields.iteritems():
            fields[field_name] = cls._deserialize_field(field_name, field_value)
        return fields

    @classmethod
    def _deserialize_field(cls, field_name, field_value):
        from edx_ace.recipient import Recipient
        from edx_ace.message import Message

        if field_name == 'expiration_time':
            return date.deserialize(field_value)
        elif field_name == 'uuid':
            return UUID(field_value)
        elif field_name == 'message':
            return Message(**field_value)
        elif field_name == 'recipient':
            return Recipient(**field_value)
        else:
            return field_value


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return unicode(obj)
        elif isinstance(obj, date.datetime):
            return date.serialize(obj)
        elif hasattr(obj, 'to_json'):
            return obj.to_json()
        else:
            return super(MessageEncoder, self).default(obj)
