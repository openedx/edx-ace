from abc import ABCMeta
import attr
from uuid import uuid4, UUID
from django.apps import apps
from lazy import lazy

import edx_ace.utils.date as date
from edx_ace.serialization import MessageAttributeSerializationMixin
from edx_ace.recipient import Recipient


@attr.s
class Message(MessageAttributeSerializationMixin):
    __metaclass__ = ABCMeta

    # mandatory attributes
    # Name is the unique identifier for the message type.
    # Used for:
    #   tracking
    #   discovering message presentation templates
    app_label = attr.ib()
    name = attr.ib()

    # optional attributes
    recipient = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Recipient)),
    )

    expiration_time = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(date.datetime)),
    )

    context = attr.ib()
    uuid = attr.ib(
        init=False,
        validator=attr.validators.instance_of(UUID),
    )
    send_uuid = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(UUID)),
        default=None
    )
    language = attr.ib(default=None)

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()


@attr.s
class MessageType(MessageAttributeSerializationMixin):
    NAME = None
    APP_LABEL = None

    context = attr.ib()
    uuid = attr.ib(
        init=False,
        validator=attr.validators.instance_of(UUID),
    )
    expiration_time = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(date.datetime)),
    )

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()

    # TODO(now): It seems like these values won't traverse a wire boundary well, maybe move to a default value for attr.ib()?
    @lazy
    def name(self):
        if self.NAME is None:
            return self.__class__.__name__.lower()
        else:
            return self.NAME

    @lazy
    def app_label(self):
        if self.APP_LABEL is None:
            return apps.get_containing_app_config(self.__class__.__module__).label
        else:
            return self.APP_LABEL

    def personalize(self, recipient, language, user_context):
        context = dict(self.context)
        context.update(user_context)
        return Message(
            app_label=self.app_label,
            name=self.name,
            expiration_time=self.expiration_time,
            context=context,
            send_uuid=self.uuid,
            recipient=recipient,
            language=language,
        )
