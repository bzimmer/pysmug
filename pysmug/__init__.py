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

r"""A high-performance client to the SmugMug API.

 This client supports the entire set of methods available through smugmug
 both serially and in batch.

 References:
   - U{pysmug <http://code.google.com/p/pysmug>}
   - U{SmugMug API <http://smugmug.jot.com/WikiHome/API/Versions/1.2.1>}
"""

__version__ = "0.3"

from pysmug.smugmug import SmugMug, SmugBatch, SmugMugException, HTTPException

def login(conf=None, klass=SmugMug, proxy=None):
  """Login to smugmug using the contents of the configuration file.

  If no configuration file specified then a file named C{.pysmugrc} in
  the user's home directory is used if it exists.

  The following order determines the C{login} method used:

    - B{In all cases C{APIKey} is required.}

    1. If C{PasswordHash} is in configuration, then C{login_withHash} is used.
      - C{UserID} is additionally required.
    2. If C{Password} is in configuration, then C{login_withPassword} is used.
      - C{EmailAddress} is additionally required.
    3. Else C{login_anonymously} is used.
  
  @param conf: path to a configuration file
  @type klass: C{SmugMug} class
  @param klass: class to instantiate
  @param proxy: address of proxy server if one is required (http[s]://localhost[:8080])
  @raise ValueError: if no configuration file is found
  """
  
  import os
  if not conf:
    home = os.environ.get("HOME", None)
    if not home:
      raise ValueError("unknown home directory")
    conf = os.path.join(home, ".pysmugrc")
    if not os.path.exists(conf):
      raise ValueError("'%s' not found" % (conf))
  config = eval(open(conf).read())
  m = klass(proxy=proxy)
  keys = set(x.lower() for x in config.keys())
  if "passwordhash" in keys:
    return m.login_withHash(**config)
  elif "password" in keys:
    return m.login_withPassword(**config)
  return m.login_anonymously(**config)
