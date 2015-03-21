#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


requirements = [
    'docopt'
]

test_requirements = [
    'pytest',
    'selenium',
    'freezegun',
]

setup(
    name='httpserver',
    version='1.0.1',
    description="Asyncio implementation of an HTTP server",
    long_description=readme + '\n\n' + history,
    author="Thom Wiggers and Luuk Scholten",
    author_email='thom@thomwiggers.nl, info@luukscholten.com',
    maintainer="Thom Wiggers",
    maintainer_email='thom@thomwiggers.nl',
    url='https://github.com/thomwiggers/httpserver',
    packages=[
        'httpserver',
    ],
    package_dir={'httpserver':
                 'httpserver'},
    entry_points={
        'console_scripts': [
            'httpserver = httpserver:run'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='httpserver',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': PyTest}
)
