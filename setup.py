#!/usr/bin/env python

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (2,5):
    raise NotImplementedError("Sorry, you need at least Python 2.5 or Python 3.x")

import contexter

with contexter.Contexter() as ctx:
    long_description = '  '.join(ctx << open('README.rst')).rstrip()

setup(name='contexter',
      version=contexter.__version__,
      description=contexter.__doc__.replace('\n', '\n  ').rstrip(),
      long_description=long_description,
      author=contexter.__author__,
      author_email='marc@gsites.de',
      url='https://bitbucket.org/defnull/contexter',
      py_modules=['contexter'],
      license='MIT',
      platforms = 'any',
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ],
     )



