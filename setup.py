#!/usr/bin/env python

# Written by Brian Zimmer

import os
import pysmug
from distutils.core import setup
from distutils.cmd import Command

class epydoc(Command):
  description = "Builds the documentation."
  user_options = []

  def initialize_options(self):
    pass
  
  def finalize_options(self):
    pass
  
  def run(self):
    os.system("epydoc -v -o doc pysmug/*.py")

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
  cmdclass = {"epydoc":epydoc},
)

