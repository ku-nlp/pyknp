#!/usr/bin/env python

__author__ = 'Kurohashi-Kawahara Lab, Kyoto Univ.'
__email__ = 'contact@nlp.ist.i.kyoto-u.ac.jp'
__copyright__ = ''
__license__ = 'See COPYING'

import os
from setuptools import setup, find_packages, Extension

version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_file) as fh:
    pyknp_version = fh.read().strip()
__version__ = pyknp_version

with open("README.md") as f:
    long_description = f.read()

setup(
    name='pyknp',
    version=pyknp_version,
    maintainer=__author__,
    maintainer_email=__email__,
    author=__author__,
    author_email=__email__,
    description='Python module for JUMAN/KNP.',
    license=__license__,
    url='https://github.com/ku-nlp/pyknp',
    long_description=long_description,
    long_description_content_type='text/markdown',
    scripts=['pyknp/scripts/knp-drawtree', ],
    packages=find_packages(),
    install_requires=['six'],
)
