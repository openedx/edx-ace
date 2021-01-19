"""
:mod:`edx_ace.serialization` contains :class:`MessageAttributeSerializationMixin`,
which allows messages to be round-tripped through JSON, and
:class:`MessageEncoder`, which actually performs the JSON encoding.
"""
import json
from uuid import UUID

import attr

from django.utils.functional import Promise

from edx_ace.utils import date


class MessageAttributeSerializationMixin:
    """
    This mixin allows an object to be serialized to (and deserialized from)
    a JSON string.

    :meth:`__str__` and :meth:`from_string` function as inverses,
    and are the primary point of interaction with this mixin by
    outside clients.

    :meth:`to_json` is used to recursively convert the object to a
    python dictionary that can then be encoded to a JSON string.
    """
    def __str__(self):
        return json.dumps(self, cls=MessageEncoder)

    @classmethod
    def from_string(cls, string_value):
        """
        Decode a JSON-encoded string representation of this type.

        Arguments:
            string_value (str): The JSON string to decode.

        Returns:
            An instance of this class.
        """
        fields = json.loads(
            string_value,
            object_hook=cls._deserialize,
        )
        uuid = fields.pop('uuid')
        instance = cls(**fields)
        instance.uuid = uuid
        return instance

    def to_json(self):
        """
        Returns: dict
            a python dictionary containing all serializable fields
            of this object, suitable for JSON-encoding.
        """
        return attr.asdict(self)

    @classmethod
    def _deserialize(cls, json_value):
        """
        Deserialize a JSON value (a python dictionary) into an
        instance of the current class.

        Arguments:
            json_value (dict): The json object to decode.

        Returns:
            An instance of the current class.
        """
        fields = json_value.copy()
        for field_name, field_value in fields.items():
            fields[field_name] = cls._deserialize_field(field_name, field_value)
        return fields

    @classmethod
    def _deserialize_field(cls, field_name, field_value):
        """
        Deserialize a single encoded field value for this message.

        Arguments:
            field_name (str): The name of the field being decoded.
            field_value: The value of field being deserialized.
        """
        # We have to import these here to avoid a circular dependency since these classes use this mixin.
        from edx_ace.message import Message  # pylint: disable=import-outside-toplevel
        from edx_ace.recipient import Recipient  # pylint: disable=import-outside-toplevel

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
    """ Custom Message Encoder. """
    # The Pylint error is disabled because of a bug in Pylint.
    # See https://github.com/PyCQA/pylint/issues/414
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        elif isinstance(o, date.datetime):
            return date.serialize(o)
        elif hasattr(o, 'to_json'):
            return o.to_json()
        elif isinstance(o, Promise):
            return str(o)
        else:
            return super().default(o)   # pragma: no cover
