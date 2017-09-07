edX Automated Communication Engine (A.C.E.)
===========================================

|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge| |license-badge|

The automated communication engine, A.C.E. for short, is a Django app for messaging learners on the edX platform. This
app can be installed in any edX project, but has only been tested with ``edx-platform``. Email delivery (via Sailthru)
is the only current delivery channel. In the future we may add support for other delivery channels such as push
notifications.


Documentation
-------------

The full documentation is at https://edx-ace.readthedocs.org.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

PR description template should be automatically applied if you are sending PR from github interface; otherwise you
can find it it at `PULL_REQUEST_TEMPLATE.md <https://github.com/edx/edx-ace/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_

Issue report template should be automatically applied if you are sending it from github UI as well; otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/edx/edx-ace/blob/master/.github/ISSUE_TEMPLATE.md>`_

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources <https://open.edx.org/getting-help>`_ if you need any assistance.



.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-ace.svg
    :target: https://pypi.python.org/pypi/edx-ace/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.org/edx/edx-ace.svg?branch=master
    :target: https://travis-ci.org/edx/edx-ace
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/edx/edx-ace/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/edx-ace?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/edx-ace/badge/?version=latest
    :target: http://edx-ace.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-ace.svg
    :target: https://pypi.python.org/pypi/edx-ace/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/edx-ace.svg
    :target: https://github.com/edx/edx-ace/blob/master/LICENSE.txt
    :alt: License
