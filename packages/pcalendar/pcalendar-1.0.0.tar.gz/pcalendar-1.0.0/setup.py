#!/usr/bin/env python3
"""
Setup script for Persian Calendar Library (PCalendar)
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from __init__.py
def get_version():
    version_file = os.path.join(this_directory, 'pcalendar', '__init__.py')
    with open(version_file, encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name='pcalendar',
    version=get_version(),
    author='Ali Miracle',
    author_email='alimiracle@riseup.net',
    description='Persian Calendar Library - Python Implementation for Solar Hijri Calendar',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://codeberg.org/alimiracle/pcalendar',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        'Topic :: Utilities',
    ],
    keywords='persian calendar solar hijri shamsi date time conversion',
    license='GPLv3',
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
        ],
    },
    project_urls={
        'Bug Reports': 'https://codeberg.org/alimiracle/pcalendar/issues',
        'Source': 'https://codeberg.org/alimiracle/pcalendar',
        'Documentation': 'https://codeberg.org/alimiracle/pcalendar#readme',
    },
    zip_safe=False,
    include_package_data=True,
)
