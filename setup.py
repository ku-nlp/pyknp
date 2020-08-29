#!/usr/bin/env python

__author__ = 'Kurohashi-Kawahara Lab, Kyoto Univ.'
__email__ = 'contact@nlp.ist.i.kyoto-u.ac.jp'
__copyright__ = ''
__license__ = 'See COPYING'

import os
from setuptools import setup, find_packages

about = {}
here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'pyknp', '__version__.py')).read(), about)

with open('README.md', encoding='utf8') as f:
    long_description = f.read()

setup(
    name='pyknp',
    version=about['__version__'],
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
