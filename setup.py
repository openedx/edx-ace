#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0111,W6005,W6100
from __future__ import absolute_import, print_function

import os
import re
import sys

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = [ub]?['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


VERSION = get_version('edx_ace', '__init__.py')

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
CHANGELOG = open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst')).read()

setup(
    name='edx-ace',
    version=VERSION,
    description='Framework for Messaging',
    long_description=README + '\n\n' + CHANGELOG,
    author='edX',
    author_email='oscm@edx.org',
    url='https://github.com/edx/edx-ace',
    packages=[
        'edx_ace',
    ],
    include_package_data=True,
    install_requires=[
        "Django>=1.8,<2.0",
        "six",
        "stevedore",
        "attrs>=17.2.0,<18.0.0",
        "python-dateutil",
        'enum34;python_version<"3.4"',
        'mock;python_version<"3.3"',
    ],
    extras_require={
        'sailthru':  ["sailthru-client>2.2,<2.3"]
    },
    license="AGPL 3.0",
    zip_safe=False,
    keywords='Django edx',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'openedx.ace.channel': [
            'sailthru_email = edx_ace.channel.sailthru:SailthruEmailChannel',
            'file_email = edx_ace.channel.file:FileEmailChannel',
            'django_email = edx_ace.channel.django_email:DjangoEmailChannel',
        ]
    }
)
