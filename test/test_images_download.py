import logging
logging.basicConfig(level=logging.DEBUG)

import pysmug
import datetime

import optparse
from pysmug import SmugMug
from getpass import getpass

_APIKey = "1XhqbbxNfSygsmVReGQ8nek8D2Dz8F61"

class Test:
  def __init__(self, APIKey, EmailAddress=None, Password=None):
    self.m = SmugMug()
    if EmailAddress and Password:
      self.m.login_withPassword(APIKey=APIKey,
        EmailAddress=EmailAddress, Password=Password)
    else:
      self.m.login_anonymously(APIKey=APIKey)
    self.m.protocol = "http"

  def test(self, albumId):
    b = self.m.batch()
    t = datetime.datetime.now()
    for a in b.images_download(AlbumID=albumId, Format="Tiny", Path="/tmp"):
      print a
    print datetime.datetime.now() - t

if __name__ == "__main__":
  p = optparse.OptionParser()
  p.add_option("-a", "--apikey", default=_APIKey, action="store")
  p.add_option("-e", "--email", action="store")
  opts, args = p.parse_args()

  if not args:
    args = [630992] # Street Photos from Moon River Photography

  password = getpass() if opts.email else None
  test = Test(opts.apikey, opts.email, password)
  for arg in args:
    test.test(arg)
  raise SystemExit()

