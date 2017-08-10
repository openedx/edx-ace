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

    def _serialize(self):
        return json.dumps({
            field_name: json.dumps(field_value, cls=MessageEncoder)
            for field_name, field_value in attr.asdict(self).iteritems()
            if field_value is not None
        })

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

        try:
            value = json.loads(field_value)
        except ValueError:
            # TODO figure out why we're doubly-JSONifying some strings but not others
            value = field_value
        if field_name == 'expiration_time':
            return date.deserialize(value)
        elif field_name == 'uuid':
            return UUID(value)
        elif field_name == 'message':
            return Message.from_string(unicode(field_value))
        elif field_name == 'recipient':
            return Recipient.from_string(unicode(field_value))
        else:
            return value


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        from edx_ace.recipient import Recipient
        from edx_ace.message import Message

        if isinstance(obj, UUID):
            return unicode(obj)
        elif isinstance(obj, date.datetime):
            return date.serialize(obj)
        elif isinstance(obj, Message):
            return obj._serialize()
        elif isinstance(obj, Recipient):
            return obj._serialize()
        else:
            return super(MessageEncoder, self).default(obj)
