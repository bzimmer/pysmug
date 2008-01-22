#!/usr/bin/env python

# Written by Brian Zimmer

import pysmug
from distutils.core import setup

setup(
  name = "pysmug",
  version = pysmug.__version__,
  description = "A high-performance python client for the SmugMug API.",
  author = "Brian Zimmer",
  author_email = "bzimmer@ziclix.com",
  url = "http://code.google.com/p/pysmug",
  packages = ['pysmug'],
  platforms = ['any'],
  license = "MIT License",
  classifiers = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
)

