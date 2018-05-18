#!/usr/bin/env python

__author__ = 'John Richardson'
__email__ = 'john@nlp.ist.i.kyoto-u.ac.jp'
__copyright__ = ''
__license__ = 'See COPYING'

import os
from setuptools import setup, find_packages, Extension

version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_file) as fh:
    pyknp_version = fh.read().strip()
__version__ = pyknp_version

setup(
    name='pyknp',
    version=pyknp_version,
    maintainer=__author__,
    maintainer_email=__email__,
    author=__author__,
    author_email=__email__,
    description='Python module for JUMAN/KNP.',
    license=__license__,
    url='https://bitbucket.org/ku_nlp/pyknp',
    scripts=['pyknp/scripts/knp-drawtree', ],
    packages=find_packages(),
)
