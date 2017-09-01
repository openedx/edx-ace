# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from django.apps import AppConfig


class EdxAceConfig(AppConfig):
    u"""
    Configuration for the edx_ace Django application.
    """

    name = u'edx_ace'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import edx_ace.signals  # pylint: disable=unused-variable
