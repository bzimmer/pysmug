
import os
import md5
import cjson
import pycurl
import urllib
import logging
import cStringIO
from itertools import islice

from pysmug import __version__
from pysmug.methods import methods as _methods

_userAgent = "pysmug(%s)" % (__version__)

_curlinfo = (
  ("total-time", pycurl.TOTAL_TIME),
  ("upload-speed", pycurl.SPEED_UPLOAD),
  ("download-speed", pycurl.SPEED_DOWNLOAD)
)

class SmugMugException(Exception):
  def __init__(self, message, code=0):
    super(SmugMugException, self).__init__(message)
    self.code = code

class SmugBase(object):
  def __init__(self, sessionId=None):
    self.sessionId = sessionId

  def __getattr__(self, method):
    """Construct a dynamic handler for the smugmug api."""
    # Refuse to act as a proxy for unimplemented special methods
    if method.startswith('__'):
      raise AttributeError("no such attribute '%s'" % (method))
    return self._make_handler(method)

  def _make_handler(self, method):
    method = "smugmug." + method.replace("_", ".")

    if method not in _methods:
      raise SmugMugException("no such smugmug method '%s'" % (method))

    url = "http://api.smugmug.com/services/api/json/1.2.1/?%s"
    
    def smugmug(*args, **kwargs):
      """Dynamically created handler for a SmugMug API call."""
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
      query = url % urllib.urlencode(kwargs)
      c = self._new_connection(query, kwargs)
      return self._perform(c)
    
    return smugmug

  def _new_connection(self, url, args):
    c = pycurl.Curl()
    c.args = args
    c.setopt(c.URL, url)
    logging.debug(url)
    c.setopt(c.USERAGENT, _userAgent)
    c.response = cStringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, c.response.write)
    return c

  def _handle_response(self, c):
    """Read the response, convert it to a pythonic instance and check
    the error code to ensure the operation was successful.
    """
    #### HACK ####
    # for some reason the response from smugmug
    #  is encoded incorrectly
    json = c.response.getvalue().replace("\/", "/")
    ##############
    logging.debug(json)
    resp = cjson.decode(json)
    if not resp["stat"] == "ok":
      raise SmugMugException(resp["message"], resp["code"])
    resp["Statistics"] = dict(((key, c.getinfo(const)) for key, const in _curlinfo))
    return resp

  def _perform(self, c):
    """Perform the low-level communication with smugmug."""
    try:
      c.perform()
      return self._handle_response(c)
    finally:
      c.close()

  def images_upload(self, AlbumID=None, ImageID=None, Data=None, FileName=None, **kwargs):
    """Upload the corresponding image.

    @keyword Data the binary data of the image
    @keyword FileName the name of the file (optional)
    @keyword ImageID the id of the image to replace
    @keyword AlbumID the name of the album in which to add the photo

    Note: one of ImageID or AlbumID must be present, but not both
    """
    if (ImageID is not None) and (AlbumID is not None):
      raise SmugMugException("must set only one of AlbumID or ImageID")

    filename = os.path.split(FileName)[-1]
    fingerprint = md5.new(Data).hexdigest()
    image = cStringIO.StringIO(Data)
    url = "http://upload.smugmug.com/" + filename

    headers = [
      "Host: upload.smugmug.com",
      "Content-MD5: " + fingerprint,
      "X-Smug-Version: 1.2.1",
      "X-Smug-ResponseType: JSON",
      "X-Smug-AlbumID: " + str(AlbumID) if AlbumID else "X-Smug-ImageID: " + str(ImageID),
      "X-Smug-FileName: " + filename,
      "X-Smug-SessionID: " + self.sessionId,
    ]

    c = self._new_connection(url, {"SessionID":self.sessionId,
      "FileName":FileName, "ImageID":ImageID, "AlbumID":AlbumID})
    c.setopt(c.UPLOAD, True)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.INFILESIZE, len(Data))
    c.setopt(c.READFUNCTION, image.read)
    
    return self._perform(c)

class SmugMug(SmugBase):

  def batch(self):
    """Return an instance of a batch-oriented smugmug client."""
    return SmugBatch(self.sessionId)
  
  def login_anonymously(self, APIKey=None):
    login = self._make_handler("login_anonymously")
    session = login(SessionID=None, APIKey=APIKey)
    self.sessionId = session['Login']['Session']['id']
    return self

  def login_withPassword(self, EmailAddress=None, Password=None, APIKey=None):
    """Login into the smugmug service with username, password and API key."""
    login = self._make_handler("login_withPassword")
    session = login(SessionID=None,
      EmailAddress=EmailAddress, Password=Password, APIKey=APIKey)
    self.sessionId = session['Login']['Session']['id']
    return self

class SmugBatch(SmugBase):
  """Batching interface to smugmug.  The standard smugmug client
  executes each request as they are executed.  The batching version
  postpones executing all the requests until all have been prepared.
  The requests are then performed in parallel which generally achieves
  far greater performance than serially executing the requests.
  """
  def __init__(self, sessionId=None):
    super(SmugBatch, self).__init__(sessionId)
    self._batch = list()
  
  def _perform(self, c):
    self._batch.append(c)
    return None

  def __len__(self):
    return len(self._batch)
  
  def __call__(self, n=35):
    """Execute all events in batch using at most n simulatenous connections."""
    if not self._batch:
      raise SmugMugException("no pending events")

    def f(batch):
      m = pycurl.CurlMulti()

      ibatch = iter(batch)
      total, working = len(batch), 0

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
            yield (c.args, self._handle_response(c))
          for c, errno, errmsg in err:
            m.remove_handle(c)
            yield (c.args, self._handle_response(c))
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

    try:
      return f(self._batch[:])
    finally:
      self._batch = list()


