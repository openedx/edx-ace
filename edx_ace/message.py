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

    # app_label = attr.ib()

    # mandatory attributes
    # Name is the unique identifier for the message type.
    # Used for:
    #   tracking
    #   discovering message presentation templates
    name = attr.ib()

    expiration_time = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(date.datetime)),
    )

    context = attr.ib()
    uuid = attr.ib(
        validator=attr.validators.instance_of(UUID),
    )

    # optional attributes
    recipient = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(Recipient)),
    )

    @name.default
    def default_name(self):
        return getattr(self.__class__, 'name', attr.NOTHING)

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()


@attr.s
class MessageType(object):
    NAME = None
    APP_LABEL = None

    context = attr.ib()
    uuid = attr.ib()
    expiration_time = attr.ib(default=None)

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()

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

    def personalize(self, user_context):
        context = dict(self.context)
        context.update(user_context)
        context['template_uuid'] = self.uuid
        return Message(
            app_label=self.app_label,
            name=self.name,
            expiration_time=self.expiration_time,
            context=context,
        )
