# Copyright (c) 2008 Brian Zimmer <bzimmer@ziclix.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A high-performance client to the SmugMug API.

 This client supports the entire set of methods available through smugmug
 both serially and in batch.

 References:
   - U{pysmug <http://code.google.com/p/pysmug>}
   - U{SmugMug API <http://www.smugmug.com>}
"""

__version__ = "0.6"

from pysmug.smugtool import SmugTool
from pysmug.smugmug import SmugMug, SmugBatch, SmugMugException

def login(conf=None, klass=None, proxy=None):
  """Login to smugmug using the contents of the configuration file.

  If no configuration file is specified then a file named C{.pysmugrc} in
  the user's home directory is used if it exists.
  
  The format is a standard configuration parseable by C{ConfigParser}.  The main
  section C{pysmug} is required.  The key C{login} references which section to use
  for authentication with SmugMug.  The key C{smugmug} is optional and can specify
  an alternate C{SmugMug} class to instantiate.  This is an example file::

    [pysmug]
    login=login_withHash
    smugmug=pysmug.SmugTool

    [login_withHash]
    APIKey = <my api key>
    userId = <my user id>
    passwordHash = <my password hash>

    [login_anonymously]
    APIKey = <my api key>

  @type conf: string
  @param conf: path to a configuration file
  @type klass: C{SmugMug} class
  @param klass: class to instantiate
  @param proxy: address of proxy server if one is required (http[s]://localhost[:8080])
  @raise ValueError: if no configuration file is found
  """
  import os
  from ConfigParser import ConfigParser

  if not conf:
    home = os.environ.get("HOME", None)
    if not home:
      raise ValueError("unknown home directory")
    conf = os.path.join(home, ".pysmugrc")
    if not os.path.exists(conf):
      raise ValueError("'%s' not found" % (conf))

  config = ConfigParser()
  config.optionxform = str
  config.read(conf)

  if not klass:
    klass = SmugMug
    if config.has_option("pysmug", "smugmug"):
      path = config.get("pysmug", "smugmug")
      i = path.rfind(".")
      module, attr = path[:i], path[i+1:]
      mod = __import__(module, globals(), locals(), [attr])
      klass = getattr(mod, attr)
  m = klass(proxy=proxy)

  auth = config.get("pysmug", "login")
  keys = dict(config.items(auth))
  return getattr(m, auth)(**keys)
