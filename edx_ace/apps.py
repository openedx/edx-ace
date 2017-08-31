# -*- coding: utf-8 -*-
"""
edx_ace Django application initialization.
"""

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class EdxAceConfig(AppConfig):
    """
    Configuration for the edx_ace Django application.
    """

    name = 'edx_ace'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import edx_ace.signals  # pylint: disable=unused-variable
