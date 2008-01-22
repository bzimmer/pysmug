
#import logging
#logging.basicConfig(level=logging.DEBUG)

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

  def test(self, albumId):
    m, b = self.m, self.m.batch()
    album = m.albums_getInfo(AlbumID=albumId)
    print
    print "Album:", album["Album"]["Title"],

    images = m.images_get(AlbumID=albumId)
    for image in images["Images"]:
      # add each image to the batch
      b.images_getInfo(ImageID=image["id"], Heavy=1)
    
    count = len(b)
    print "(%d photos)" % (len(b))

    max_time = 0.0
    total_time = 0.0

    # execute the batch request
    for (params, value) in b():
      stats = value["Statistics"]
      max_time = max(max_time, stats["total-time"])
      total_time += stats["total-time"]

    # print some stats
    def seconds(g, t):
      return "%s: %0.2f seconds" % (g, t)
    print seconds("Synchronously        ", total_time)
    print seconds("Asynchronously       ", max_time)
    print seconds("Average response time", total_time/count)

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

