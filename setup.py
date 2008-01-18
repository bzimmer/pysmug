#!/usr/bin/env python

# Written by Brian Zimmer

import pysmug
from distutils.core import setup, Extension

setup(
  name = "pysmug",
  version = pysmug.__version__,
  author = "Brian Zimmer",
  author_email = "<bzimmer@ziclix.com>",
  url = "http://code.google.com/pysmug",
  packages = ['pysmug'],
  license = "Python",
)

