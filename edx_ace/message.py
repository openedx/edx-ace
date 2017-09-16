# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
from abc import ABCMeta
from uuid import UUID, uuid4

import attr
import six

from django.apps import apps

import edx_ace.utils.date as date
from edx_ace.monitoring import report as monitoring_report
from edx_ace.recipient import Recipient
from edx_ace.serialization import MessageAttributeSerializationMixin


@attr.s
@six.add_metaclass(ABCMeta)
class Message(MessageAttributeSerializationMixin):

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

    # TODO(later): better naming to distinguish between these 2 UUIDs
    uuid = attr.ib(
        init=False,
        validator=attr.validators.instance_of(UUID),
    )
    send_uuid = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(UUID)),
        default=None
    )
    language = attr.ib(default=None)
    log_level = attr.ib(default=None)

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()

    @property
    def unique_name(self):
        return u'.'.join([self.app_label, self.name])

    @property
    def log_id(self):
        return u'.'.join([
            self.unique_name,
            six.text_type(self.send_uuid) if self.send_uuid else u'no_send_uuid',
            six.text_type(self.uuid)
        ])

    def get_message_specific_logger(self, logger):
        return MessageLoggingAdapter(logger, {u'message': self})

    def report_basics(self):
        monitoring_report(u'message_name', self.unique_name)
        monitoring_report(u'language', self.language)

    def report(self, key, value):
        monitoring_report(key, value)


class MessageLoggingAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return u'[%s] %s' % (self.extra[u'message'].log_id, msg), kwargs

    def debug(self, msg, *args, **kwargs):
        log_level = self.extra[u'message'].log_level
        if log_level and log_level <= logging.DEBUG:
            return self.info(msg, *args, **kwargs)
        else:
            super(MessageLoggingAdapter, self).debug(msg, *args, **kwargs)


@attr.s(cmp=False)
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
    app_label = attr.ib()
    name = attr.ib()
    log_level = attr.ib(default=None)

    @context.default
    def default_context_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()

    @name.default
    def default_name(self):
        if self.NAME is None:
            return self.__class__.__name__.lower()
        else:
            return self.NAME

    @app_label.default
    def default_app_label(self):
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
            log_level=self.log_level,
        )

    # TODO(later): Why is it necessary to override attr's
    # implementation of these?
    def __eq__(self, other):
        if isinstance(other, MessageType):
            return attr.astuple(self) == attr.astuple(other)
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self == other
        if result == NotImplemented:
            return NotImplemented
        else:
            return not result
