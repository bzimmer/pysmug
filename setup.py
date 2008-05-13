
import os
import glob
from ConfigParser import ConfigParser

from distutils.core import setup
from distutils.cmd import Command
from distutils.errors import DistutilsExecError
from distutils.command.sdist import sdist as _sdist

p = ConfigParser()
p.read("metainf.cfg")
PACKAGE = p.get("main", "package")
DESCRIPTION = p.get("main", "description")
VERSION = __import__(PACKAGE).__version__

class epydoc(Command):
  description = "Builds the documentation."
  user_options = []

  def initialize_options(self):
    pass
  
  def finalize_options(self):
    pass
  
  def run(self):
    if not os.path.exists("epydoc.cfg"):
      return
    self.mkpath("doc/html")
    stat = os.system("epydoc --config epydoc.cfg %s/*.py" % (PACKAGE))
    if not stat == 0:
      raise DistutilsExecError("failed to run epydoc")

class nosetests(Command):
  description = "Runs the tests."
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    from nose.core import TestProgram
    TestProgram(argv=[PACKAGE]).runTests()

class sdist(_sdist):
  def run(self):
    self.run_command("epydoc")
    _sdist.run(self)

def datafiles():
  """Returns a list of (path, [files]) to install.
  """
  def _datafiles():
    root = os.path.join("share", "doc", PACKAGE + "-" + VERSION)
    yield (root, [x for x in ("ChangeLog", "LICENSE", "README") if os.path.exists(x)])
    for dn, pattern in (("doc/html", "*"), ("examples", "*.py")):
      files = glob.glob(os.path.join(dn, pattern))
      if files:
        yield (os.path.join(root, dn), files)
  return list(_datafiles())

def scripts():
  """Returns a list of script files to install.
  """
  return glob.glob(os.path.join("scripts", "*.py"))

setup(
  name = PACKAGE,
  version = VERSION,
  description = DESCRIPTION,
  author = "Brian Zimmer",
  author_email = "bzimmer@ziclix.com",
  url = "http://code.google.com/p/%s" % (PACKAGE),
  download_url = "http://pypi.python.org/pypi/%s/%s" % (PACKAGE, VERSION),
  packages = [PACKAGE, PACKAGE + ".tests"],
  scripts = scripts(),
  data_files = datafiles(),
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
  cmdclass = {"epydoc":epydoc, "sdist":sdist, "nosetests":nosetests},
)

