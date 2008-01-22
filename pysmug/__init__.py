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

__all__ = ("__version__", "SmugMug", "SmugBatch", "SmugMugException", "login")

__version__ = "0.1"

from pysmug.smugmug import SmugMug, SmugBatch, SmugMugException

def login(conf=None):
  """Login to smugmug using the contents of the configuration file.

  If no configuration file specified then a file named C{.pysmugrc} in
  the user's home directory is used if it exists.
  
  @param conf: path to a configuration file
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
  return SmugMug().login_withPassword(**config)

