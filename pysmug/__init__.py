
"""SmugMug API

This module has been greatly influenced by the Flickr module.

>>> import logging, urllib
>>> logging.basicConfig(level=logging.DEBUG)
>>> import pysmug
>>> m = pysmug.login()
>>> tree = m.users_getTree()
>>> category = m.categories_create(Name="Testing")
>>> categoryId = category["Category"]["id"]
>>> m.categories_rename(CategoryID=categoryId, Name="ReTesting")
>>> album = m.albums_create(Title="NewAlbum", CategoryID=categoryId)
>>> albumId = album["Album"]["id"]
>>> try: images = m.images_get(AlbumID=albumId)
... except pysmug.SmugMugException, e: print e.message
>>> assert m.albums_getInfo(AlbumID=albumId)["Album"]["Category"]["id"] == categoryId
>>> google = urllib.urlopen("http://www.google.com/intl/en_ALL/images/logo.gif").read()
>>> image = m.images_upload(Data=google, FileName="google.gif", AlbumID=albumId)
>>> images = m.images_get(AlbumID=albumId, Heavy=1)
>>> for a in images["Images"]:
...   print a
>>> x = raw_input("check the album...")
>>> m.albums_delete(AlbumID=albumId)
>>> m.categories_delete(CategoryID=categoryId)
"""

import os
import md5
import cjson
import types
import pycurl
import urllib
import logging
import cStringIO

__all__ = ('login', 'SmugMug', 'SmugMugException', '__version__')

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
  return SmugMug(mod.username, mod.password, mod.apikey)

class SmugMugException(Exception):
  def __init__(self, code, message):
    super(Exception, self).__init__(message)
    self.code = code

class SmugMug(object):
  def __init__(self, username, password, apiKey):
    self.__handlerCache = {}
    session = self.login_withPassword(SessionID=None,
      EmailAddress=username, Password=password, APIKey=apiKey)
    self.sessionId = session['Login']['Session']['id']

  def __handleResponse(self, json):
    #### HACK ####
    # for some reason the response from smugmug
    #  is encoded incorrectly
    json = json.replace("\/", "/")
    ##############
    logging.debug(json)
    resp = cjson.decode(json)
    if not resp["stat"] == "ok":
      raise SmugMugException(resp["code"], resp["message"])
    return resp

  def __getattr__(self, method):
    # Refuse to act as a proxy for unimplemented special methods
    if method.startswith('__'):
      raise AttributeError("No such attribute '%s'" % method)
    if self.__handlerCache.has_key(method):
      # If we already have the handler, return it
      return self.__handlerCache.has_key(method)

    # Construct the method name and URL
    method = "smugmug." + method.replace("_", ".")
    url = "http://api.smugmug.com/services/api/json/1.2.1/?%s"
    
    def handler(**args):
      '''Dynamically created handler for a SmugMug API call'''
      # Set some defaults
      defaults = {"method": method, "SessionID":self.sessionId}
      for key, value in defaults.iteritems():
        if key not in args:
          args[key] = value
        # Remove a default by assigning None
        if key in args and args[key] is None:
          del args[key]

      query = url % urllib.urlencode(args)
      logging.debug(query)

      c = pycurl.Curl()
      t = cStringIO.StringIO()
      try:
        c.setopt(c.URL, query)
        c.setopt(c.USERAGENT, userAgent)
        c.setopt(c.WRITEFUNCTION, t.write)
        c.perform()
      finally:
        c.close()
      return self.__handleResponse(t.getvalue())

    self.__handlerCache[method] = handler
    return self.__handlerCache[method]

  def images_upload(self, **kwargs):
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
    response = cStringIO.StringIO()
    url = "http://upload.smugmug.com/" + filename

    headers = [
      "Host: upload.smugmug.com",
      "Content-MD5: " + fingerprint,
      "X-Smug-Version: 1.2.1",
      "X-Smug-ResponseType: JSON",
      "X-Smug-ImageID: " + str(ImageID) if ImageID else "X-Smug-AlbumID: " + str(AlbumID),
      "X-Smug-FileName: " + filename,
      "X-Smug-SessionID: " + self.sessionId,
    ]

    c = pycurl.Curl()
    try:
      c.setopt(c.URL, url)
      c.setopt(c.UPLOAD, True)
      c.setopt(c.HTTPHEADER, headers)
      c.setopt(c.NOPROGRESS, True)
      c.setopt(c.USERAGENT, userAgent)
      c.setopt(c.INFILESIZE, len(Data))
      c.setopt(c.READFUNCTION, image.read)
      c.setopt(c.WRITEFUNCTION, response.write)
      c.perform()
      stats = dict([("total-time", c.getinfo(c.TOTAL_TIME)), ("upload-speed", c.getinfo(c.SPEED_UPLOAD))])
    finally:
      c.close()

    r = self.__handleResponse(response.getvalue())
    r["Statistics"] = stats
    return r
    
