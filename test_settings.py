"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'edx_ace',
)

LOCALE_PATHS = [
    root('edx_ace', 'conf', 'locale'),
]

ROOT_URLCONF = 'edx_ace.urls'

SECRET_KEY = 'insecure-secret-key'

ACE_ENABLED_POLICIES = []
ACE_CHANNEL_DEFAULT_EMAIL = 'sailthru_email'
ACE_CHANNEL_TRANSACTIONAL_EMAIL = 'file_email'

ACE_ENABLED_CHANNELS = [
    'sailthru_email',
    'file_email',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            root('edx_ace', 'tests', 'test_templates'),
        ],
    },
]

ACE_CHANNEL_SAILTHRU_DEBUG = True
ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME = 'Automated Communication Engine Email'
ACE_CHANNEL_SAILTHRU_API_KEY = None
ACE_CHANNEL_SAILTHRU_API_SECRET = None
