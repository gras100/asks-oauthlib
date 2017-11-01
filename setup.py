#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

from setuptools import setup

if sys.version_info < (3, 5, 2):
    # 3.5.2 is when __aiter__ became a synchronous function
    raise SystemExit('Sorry! asks-oauthlib requires python 3.5.2 or later.')

# Get the version
version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('requests_oauthlib/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")


APP_NAME = 'requests-oauthlib'

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def readall(path):
    with open(path) as fp:
        return fp.read()


setup(
    name=APP_NAME,
    version=VERSION,
    description='OAuthlib authentication support for Asks.',
    long_description=readall('README.rst') + '\n\n' +
                     readall('HISTORY.rst'),
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    url='https://github.com/requests/requests-oauthlib',
    packages=['requests_oauthlib', 'requests_oauthlib.compliance_fixes'],
    install_requires=['oauthlib>=0.6.2', 'asks>=1.3.6'],
    extras_require={'rsa': ['oauthlib[rsa]>=0.6.2', 'asks>=1.3.6']},
    license='ISC',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5.2',
        'Programming Language :: Python :: 3.6',
    ),
    zip_safe=False,
    tests_require=[
        'mock',
        'requests-mock',
    ],
    test_suite='tests'
)
