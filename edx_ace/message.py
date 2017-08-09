from abc import ABCMeta
import json
from uuid import uuid4

import edx_ace.utils.date as date


class MessageBase(object):
    __metaclass__ = ABCMeta

    SERIALIZED_KEYS = ('name', 'expiration_time', 'uuid', 'fields')
    CLASS_KEY = 'class'

    def __init__(self, name, expiration_time, uuid, fields=None):
        self.name = name
        self.expiration_time = expiration_time
        self.uuid = uuid
        self.fields = {} if fields is None else fields

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(repr(getattr(self, key)) for key in self.SERIALIZED_KEYS)
        )

    def _serialize(self):
        json_value = {
            key: json.dumps(getattr(self, key))
            for key in self.SERIALIZED_KEYS
        }
        json_value.update({self.CLASS_KEY: self.__class__})
        return json_value

    # TODO Get serialization/deserialization working
    @classmethod
    def _deserialize(cls, json_value):
        json_value = json_value.copy()
        class_value = json_value.pop(cls.CLASS_KEY)
        return class_value(**json_value)

    def __unicode__(self):
        return json.dumps(self, cls=MessageEncoder)

    @classmethod
    def from_string(cls, string_value):
        return json.loads(
            string_value,
            # object_hook=message_decoder,
        )


class MessageTemplate(MessageBase):
    @classmethod
    def create(cls, name, expiration_time=None, fields=None):
        return MessageTemplate(name, expiration_time, uuid4(), fields)


class Message(MessageBase):
    SERIALIZED_KEYS = MessageBase.SERIALIZED_KEYS + ('recipient',)

    def __init__(self, recipient, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.recipient = recipient

    @classmethod
    def create(cls, recipient, name, expiration_time=None):
        return Message(recipient, name, expiration_time, uuid4())


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date.datetime):
            return date.serialize(obj)
        if isinstance(obj, MessageBase):
            return obj._serialize()
        else:
            return super(MessageEncoder, self).default(obj)
