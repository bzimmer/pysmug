#!/usr/bin/env python

# Written by Brian Zimmer

import os
import glob
import pysmug
from distutils.core import setup
from distutils.cmd import Command
from distutils.errors import DistutilsExecError
from distutils.command.sdist import sdist as _sdist

class epydoc(Command):
  description = "Builds the documentation."
  user_options = []

  def initialize_options(self):
    pass
  
  def finalize_options(self):
    pass
  
  def run(self):
    self.mkpath("doc/html")
    stat = os.system("epydoc --config epydoc.cfg pysmug/*.py")
    if not stat == 0:
      raise DistutilsExecError("failed to run epydoc")

class sdist(_sdist):
  def run(self):
    self.run_command("epydoc")
    _sdist.run(self)

def datafiles():
  """Returns a generator of (path, [files]) to install.
  """
  root = os.path.join("share", "doc", "pysmug-" + pysmug.__version__)
  yield (root, ("ChangeLog", "LICENSE.txt", "README"))
  for dn, pattern in (("doc/html", "*"), ("examples", "*.py"), ("tests", "*.py")):
    files = glob.glob(os.path.join(dn, pattern))
    if files:
      yield (os.path.join(root, dn), files)
data_files = list(datafiles())

setup(
  name = "pysmug",
  version = pysmug.__version__,
  description = "A high-performance python client for the SmugMug API.",
  author = "Brian Zimmer",
  author_email = "bzimmer@ziclix.com",
  url = "http://code.google.com/p/pysmug",
  download_url = "http://pypi.python.org/pypi/pysmug/%s" % (pysmug.__version__),
  packages = ['pysmug'],
  data_files = data_files,
  platforms = ['any'],
  license = "MIT License",
  classifiers = [
    'Intended Audience :: Developers',
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
  cmdclass = {"epydoc":epydoc, "sdist":sdist},
)

