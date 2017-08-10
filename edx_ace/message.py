from abc import ABCMeta
import attr
import json
from uuid import uuid4, UUID

import edx_ace.utils.date as date


@attr.s
class Message(object):
    __metaclass__ = ABCMeta

    name = attr.ib()
    expiration_time = attr.ib(default=attr.NOTHING)

    context = attr.ib()
    uuid = attr.ib()

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()

    def _serialize(self):
        json_value = {
            field.name: json.dumps(getattr(self, field.name), cls=MessageEncoder)
            for field in attr.fields(type(self))
        }
        return json_value

    @classmethod
    def _deserialize(cls, json_value):
        fields = json_value.copy()
        for field_name, field_value in fields.iteritems():
            fields[field_name] = cls._deserialize_field(field_name, field_value)
        return fields

    @classmethod
    def _deserialize_field(cls, field_name, field_value):
        value = json.loads(field_value)
        if field_name in ('name', 'context'):
            return value
        elif field_name == 'expiration_time':
            return date.deserialize(value)
        elif field_name == 'uuid':
            return UUID(value)
        else:
            raise ValueError()  # TODO raise better error here

    def __unicode__(self):
        return json.dumps(self, cls=MessageEncoder)

    @classmethod
    def from_string(cls, string_value):
        fields = json.loads(
            string_value,
            object_hook=cls._deserialize,
        )
        return Message(**fields)


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return unicode(obj)
        if isinstance(obj, date.datetime):
            return date.serialize(obj)
        if isinstance(obj, Message):
            return obj._serialize()
        else:
            return super(MessageEncoder, self).default(obj)
