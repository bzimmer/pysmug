
"""SmugMug API

This module has been greatly influenced by the Flickr module.
"""

import os
import md5
import cjson
import types
import pycurl
import urllib
import logging
import cStringIO

__all__ = ('login', 'BatchSmugMug', 'SmugMug', 'SmugMugException', '__version__')

__version__ = '0.1'

userAgent = "pysmug(%s)" % (__version__)

def login(conf=None):
  if not conf:
    home = os.environ.get("HOME", None)
    if not home:
      raise ValueError("unknown home directory")
    conf = os.path.join(home, ".smuglibrc")
    if not os.path.exists(conf):
      raise ValueError("'%s' not found" % (conf))
  mod = types.ModuleType("smuglibrc")
  fp = open(conf)
  exec fp in mod.__dict__
  return SmugMug.login_withPassword(mod.username, mod.password, mod.apikey)

def _make_handler(instance, method, func):
  # Construct the method name and URL
  method = "smugmug." + method.replace("_", ".")
  url = "http://api.smugmug.com/services/api/json/1.2.1/?%s"
  
  def handler(**args):
    '''Dynamically created handler for a SmugMug API call'''
    # Set some defaults
    sessionId = getattr(instance, "_sessionId", None)
    defaults = {"method": method, "SessionID":sessionId}
    for key, value in defaults.iteritems():
      if key not in args:
        args[key] = value
      # Remove a default by assigning None
      if key in args and args[key] is None:
        del args[key]

    query = url % urllib.urlencode(args)
    logging.debug(query)

    c = pycurl.Curl()
    c.setopt(c.URL, query)
    c.response = cStringIO.StringIO()
    c.setopt(c.USERAGENT, userAgent)
    c.setopt(c.WRITEFUNCTION, c.response.write)

    return func(c)
  
  return handler

class SmugMugException(Exception):
  def __init__(self, code, message):
    super(Exception, self).__init__(message)
    self.code = code

class SmugMug(object):
  def __init__(self, sessionId):
    self._sessionId = sessionId

  @classmethod
  def login_withPassword(cls, username, password, apiKey):
    """Login into the smugmug service with username, password and API key."""
    login = _make_handler(cls, "login_withPassword", SmugMug.__perform)
    session = login(EmailAddress=username, Password=password, APIKey=apiKey)
    return SmugMug(session['Login']['Session']['id'])

  @classmethod
  def _handle_response(cls, c):
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
      raise SmugMugException(resp["code"], resp["message"])
    stats = dict([("total-time", c.getinfo(c.TOTAL_TIME)), ("upload-speed", c.getinfo(c.SPEED_UPLOAD))])
    resp["Statistics"] = stats
    return resp
  
  @classmethod
  def __perform(cls, c):
    """Perform the low-level communication with smugmug."""
    try:
      c.perform()
      return cls._handle_response(c)
    finally:
      c.close()

  def __getattr__(self, method):
    """Construct a dynamic handler for the smugmug api."""
    # Refuse to act as a proxy for unimplemented special methods
    if method.startswith('__'):
      raise AttributeError("No such attribute '%s'" % method)
    return _make_handler(self, method, self._perform)

  def batch(self):
    """Return an instance of a batch-oriented smugmug client."""
    return BatchSmugMug(self._sessionId)

  def _perform(self, c):
    """Execute the http request."""
    return SmugMug.__perform(c)

  def images_upload(self, **kwargs):
    """Upload the corresponding image.

    @keyword Data the binary data of the image
    @keyword FileName the name of the file (optional)
    @keyword ImageID the id of the image to replace
    @keyword AlbumID the name of the album in which to add the photo

    Note: one of ImageID or AlbumID must be present, but not both
    """
    def get(m, key, required=True):
      if required and key not in m:
        raise SmugMugException(0, "missing param '%s'" % (key))
      return m.pop(key, None)

    Data = get(kwargs, "Data")
    FileName = get(kwargs, "FileName")
    ImageID = get(kwargs, "ImageID", False)
    AlbumID = get(kwargs, "AlbumID", False)

    if (ImageID is not None) and (AlbumID is not None):
      raise SmugMugException(0, "must set only one of AlbumID or ImageID")

    filename = os.path.split(FileName)[-1]
    fingerprint = md5.new(Data).hexdigest()
    image = cStringIO.StringIO(Data)
    url = "http://upload.smugmug.com/" + filename

    headers = [
      "Host: upload.smugmug.com",
      "Content-MD5: " + fingerprint,
      "X-Smug-Version: 1.2.1",
      "X-Smug-ResponseType: JSON",
      "X-Smug-ImageID: " + str(ImageID) if ImageID else "X-Smug-AlbumID: " + str(AlbumID),
      "X-Smug-FileName: " + filename,
      "X-Smug-SessionID: " + self._sessionId,
    ]

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.UPLOAD, True)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.USERAGENT, userAgent)
    c.setopt(c.INFILESIZE, len(Data))
    c.setopt(c.READFUNCTION, image.read)
    c.response = cStringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, c.response.write)
    
    return self._perform(c)

class BatchSmugMug(SmugMug):
  """Batching interface to smugmug.  The standard smugmug client
  executes each request as they are executed.  The batching version
  postpones executing all the requests until all have been prepared.
  The requests are then performed in parallel which generally achieves
  far greater performance than serially executing the requests.
  """
  def __init__(self, sessionId):
    super(BatchSmugMug, self).__init__(sessionId)
    self._batch = list()
  
  def _perform(self, c):
    self._batch.append(c)
    return None
  
  def __call__(self):
    if not self._batch:
      raise SmugMugException(0, "no pending events")

    def f(_batch):
      m = pycurl.CurlMulti()
      #m.setopt(pycurl.M_PIPELINING, 1)

      for c in _batch:
        m.add_handle(c)
      
      processed = len(_batch)
      while processed > 0:
        while True:
          ret, nhandles = m.perform()
          if ret != pycurl.E_CALL_MULTI_PERFORM:
            break
        while True:
          q, ok, err = m.info_read()
          for c in ok:
            m.remove_handle(c)
            yield self._handle_response(c)
          for c, errno, errmsg in err:
            m.remove_handle(c)
            yield self._handle_response(c)
          processed -= len(ok) + len(err)
          if q == 0:
            break
        m.select(1.0)

      while _batch:
        try:
          _batch.pop().close()
        except: pass

    try:
      return f(self._batch[:])
    finally:
      self._batch = None

