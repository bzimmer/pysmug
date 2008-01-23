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

import os
import md5
import pprint
import pycurl
import urllib
import logging
import cStringIO
from itertools import islice

try:
  from cjson import decode as jsondecode
except ImportError:
  from simplejson import loads as jsondecode

from pysmug import __version__
from pysmug.methods import methods as _methods

_userAgent = "pysmug(%s)" % (__version__)

_curlinfo = (
  ("total-time", pycurl.TOTAL_TIME),
  ("upload-speed", pycurl.SPEED_UPLOAD),
  ("download-speed", pycurl.SPEED_DOWNLOAD)
)

class SmugMugException(Exception):
  """Representation of a SmugMug exception."""

  def __init__(self, message, code=0):
    super(SmugMugException, self).__init__(message)
    self.code = code

class SmugBase(object):
  """Abstract functionality for SmugMug API clients."""

  def __init__(self, sessionId=None, protocol="https"):
    self.protocol = protocol
    """Communication protocol -- either C{http} or C{https}"""
    self.sessionId = sessionId
    """Session id from smugmug."""

  def __getattr__(self, method):
    """Construct a dynamic handler for the SmugMug API."""
    # Refuse to act as a proxy for unimplemented special methods
    if method.startswith('__'):
      raise AttributeError("no such attribute '%s'" % (method))
    return self._make_handler(method)

  def _make_handler(self, method):
    method = "smugmug." + method.replace("_", ".")

    if method not in _methods:
      raise SmugMugException("no such smugmug method '%s'" % (method))

    def smugmug(*args, **kwargs):
      """Dynamically created SmugMug function call."""
      if args:
        raise SmugMugException("smugmug methods take no arguments, only named parameters")
      defaults = {"method": method, "SessionID":self.sessionId}
      for key, value in defaults.iteritems():
        if key not in kwargs:
          kwargs[key] = value
        # remove a default by assigning None
        if key in kwargs and kwargs[key] is None:
          del kwargs[key]
      if "SessionID" in kwargs and kwargs["SessionID"] is None:
        raise SmugMugException("not authenticated -- no valid session id")
      query = urllib.urlencode(kwargs)
      url = "%s://api.smugmug.com/services/api/json/1.2.1/?%s" % (self.protocol, query)
      c = self._new_connection(url, kwargs)
      return self._perform(c)
    
    return smugmug

  def _new_connection(self, url, args):
    """Prepare a new connection.

    Create a new connection setting up the query string,
    user agent header, response buffer and ssl parameters.

    @param url: complete query string with parameters already encoded
    @param args: arguments passed to method to be used for later callbacks
    """
    c = pycurl.Curl()
    c.args = args
    c.setopt(c.URL, url)
    logging.debug(url)
    c.setopt(c.USERAGENT, _userAgent)
    c.response = cStringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, c.response.write)
    # for SSL
    c.setopt(c.SSL_VERIFYPEER, False)
    return c

  def _handle_response(self, c):
    """Handle the response from SmugMug.

    This method decodes the JSON response and checks for any error
    condition.  It additionally adds a C{Statistics} item to the response
    which contains upload & download times.

    @param c: a completed connection
    @return: a dictionary of results corresponding to the SmugMug response
    @raise SmugMugException: if an error exists in the response
    """
    #### HACK ####
    # for some reason the response from smugmug
    #  is encoded incorrectly
    json = c.response.getvalue().replace("\/", "/")
    ##############
    logging.debug(json)
    resp = jsondecode(json)
    if not resp["stat"] == "ok":
      raise SmugMugException(resp["message"], resp["code"])
    resp["Statistics"] = dict(((key, c.getinfo(const)) for key, const in _curlinfo))
    return resp

  def _perform(self, c):
    pass
  
  def images_upload(self, AlbumID=None, ImageID=None, Data=None, FileName=None, **kwargs):
    """Upload the corresponding image.

    ** Note: one of ImageID or AlbumID must be present, but not both **

    @param Data: the binary data of the image
    @param ImageID: the id of the image to replace
    @param AlbumID: the name of the album in which to add the photo
    @param FileName: the name of the file *optional*
    """
    if (ImageID is not None) and (AlbumID is not None):
      raise SmugMugException("must set only one of AlbumID or ImageID")

    filename = os.path.split(FileName)[-1]
    fingerprint = md5.new(Data).hexdigest()
    image = cStringIO.StringIO(Data)
    url = "%s://upload.smugmug.com/%s" % (self.protocol, filename)

    headers = [
      "Host: upload.smugmug.com",
      "Content-MD5: " + fingerprint,
      "X-Smug-Version: 1.2.1",
      "X-Smug-ResponseType: JSON",
      "X-Smug-AlbumID: " + str(AlbumID) if AlbumID else "X-Smug-ImageID: " + str(ImageID),
      "X-Smug-FileName: " + filename,
      "X-Smug-SessionID: " + self.sessionId,
    ]
    for (k, v) in kwargs:
      # Caption, Keywords, Latitude, Longitude, Altitude
      headers.append("X-Smug-%s: %s" % (k, v))

    kwargs.update({"SessionID":self.sessionId,
      "FileName":FileName, "ImageID":ImageID, "AlbumID":AlbumID})
    c = self._new_connection(url, kwargs)
    c.setopt(c.UPLOAD, True)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.INFILESIZE, len(Data))
    c.setopt(c.READFUNCTION, image.read)
    
    return self._perform(c)

class SmugMug(SmugBase):
  """Serial version of a SmugMug client."""
  
  def _perform(self, c):
    """Perform the low-level communication with SmugMug."""
    try:
      c.perform()
      return self._handle_response(c)
    finally:
      c.close()

  def batch(self):
    """Return an instance of a batch-oriented SmugMug client."""
    return SmugBatch(self.sessionId, self.protocol)
  
  def login_anonymously(self, APIKey=None):
    """Login into SmugMug anonymously.
    
    @param APIKey: a SmugMug api key
    @return: the SmugMug instance with a session established
    """
    login = self._make_handler("login_anonymously")
    session = login(SessionID=None, APIKey=APIKey)
    self.sessionId = session['Login']['Session']['id']
    return self

  def login_withPassword(self, EmailAddress=None, Password=None, APIKey=None):
    """Login into SmugMug with username, password and API key.

    @param EmailAddress: the account holder's email address
    @param Password: the account holder's password
    @param APIKey: a SmugMug api key
    @return: the SmugMug instance with a session established
    """
    login = self._make_handler("login_withPassword")
    session = login(SessionID=None,
      EmailAddress=EmailAddress, Password=Password, APIKey=APIKey)
    self.sessionId = session['Login']['Session']['id']
    return self

class SmugBatch(SmugBase):
  """Batching version of a SmugMug client."""

  def __init__(self, *args, **kwargs):
    super(SmugBatch, self).__init__(*args, **kwargs)
    self._batch = list()
    """A list of requests pending executions."""
    self.concurrent = kwargs.get("concurrent", 10)
    """The number of concurrent requests to execute."""
  
  def _perform(self, c):
    """Store the request for later processing."""
    self._batch.append(c)
    return None

  def __len__(self):
    return len(self._batch)
  
  def __call__(self, n=None):
    """Execute all pending requests.

    @type n: int
    @param n: maximum number of simultaneous connections
    @return: a generator of results from the batch execution - order independent
    """
    if not self._batch:
      raise SmugMugException("no pending events")

    try:
      return self._multi(self._batch[:], self._handle_response, n=n)
    finally:
      self._batch = list()

  def _multi(self, batch, func, n=None):
    m = pycurl.CurlMulti()

    ibatch = iter(batch)
    total, working = len(batch), 0

    n = (n if n is not None else self.concurrent)
    if n <= 0:
      raise SmugMugException("concurrent requests must be greater than zero")

    while total > 0:
      for c in islice(ibatch, (n-working)):
        m.add_handle(c)
        working += 1
      while True:
        ret, nhandles = m.perform()
        if ret != pycurl.E_CALL_MULTI_PERFORM:
          break
      while True:
        q, ok, err = m.info_read()
        for c in ok:
          m.remove_handle(c)
          yield (c.args, func(c))
        for c, errno, errmsg in err:
          m.remove_handle(c)
          yield (c.args, func(c))
        read = len(ok) + len(err)
        total -= read
        working -= read
        if q == 0:
          break
      m.select(1.0)

    while batch:
      try:
        batch.pop().close()
      except: pass

  def images_download(self, AlbumID=None, Path=None, Format="Original"):
    """Download the entire contents of an album to the specified path.
    
    * This method is not a standard smugmug method. *

    @param AlbumID: the album to download
    @param Path: the path to store the images
    @param Format: the size of the image (check smugmug for possible sizes)
    @return: a generator of responses containing the filenames saved locally
    """
    path = os.path.abspath(os.getcwd() if not Path else Path)
    
    self.images_get(AlbumID=AlbumID, Heavy=1)
    album = list(self())[0][1]

    path = os.path.join(path, str(AlbumID))
    if not os.path.exists(path):
      os.mkdir(path)

    fp = open(os.path.join(path, "album.txt"), "w")
    pprint.pprint(album, fp)
    fp.close()

    connections = list()
    for image in album["Images"]:
      url = image.get(Format+"URL", None)
      if url is None:
        continue
      fn = image.get("FileName", None)
      if fn is None:
        fn = os.path.split(url)[-1]
      filename = os.path.join(path, fn)
      connections.append(self._new_connection(url, {"FileName":filename}))

    def f(c):
      fn = c.args["FileName"]
      fp = open(fn, "wb")
      fp.write(c.response.getvalue())
      fp.close()
      return fn

    # force concurrent downloads regardless of the smug instance
    args = {"AlbumID":AlbumID, "Path":Path, "Format":Format}
    for a in self._multi(connections, f):
      r = {"method":"pysmug.images.download", "stat":"ok", "Image":{"FileName":a[1]}}
      yield (args, r)

