
import time
import urllib
import datetime
import unittest
from pysmug import SmugMug, SmugMugException

class PySmugTestCase(unittest.TestCase):
  
  def __init__(self, m, testCase):
    super(PySmugTestCase, self).__init__(testCase)
    self.m = m

  def test_album_create(self):
    self.m.secure = False
    category = self.m.categories_create(Name="NewCategory-%s" % (datetime.datetime.now()))
    categoryId = category["Category"]["id"]
    title = "NewAlbum-%s" % (datetime.datetime.now())
    album = self.m.albums_create(Title=title, categoryId=categoryId)
    albumId = album["Album"]["id"]
    assert albumId > 0

    _categoryId = 0
    for i in range(0, 3):
      _categoryId = self.m.albums_getInfo(AlbumID=albumId)["Album"]["Category"]["id"]
      if _categoryId == 0:
        # some kind of race condition with the applying of categories to a gallery?
        time.sleep(2)
        continue
      break
    self.assertEqual(categoryId, _categoryId)

    try:
      images = self.m.images_get(AlbumID=albumId)
    except SmugMugException, e:
      assert e.code == 15 # empty set
    self.m.albums_delete(albumId=albumId)
    self.m.categories_delete(categoryId=categoryId)
  
  def test_images_upload(self):
    title = "NewAlbum-%s" % (datetime.datetime.now())
    album = self.m.albums_create(Title=title)
    albumId = album["Album"]["id"]
    try:
      images = self.m.images_get(AlbumID=albumId)
    except SmugMugException, e:
      assert e.code == 15 # empty set

    google = urllib.urlopen("http://www.google.com/intl/en_ALL/images/logo.gif").read()
    image = self.m.images_upload(Data=google, FileName="google.gif", AlbumID=albumId)

    images = self.m.images_get(AlbumID=albumId, Heavy=1)
    self.assertEqual(1, len(images["Images"]))
    self.assertEqual("google.gif", images["Images"][0]["FileName"])
    self.m.albums_delete(AlbumID=albumId)

def login(APIKey, EmailAddress=None, Password=None, PasswordHash=None):
  m = SmugMug()
  if EmailAddress and Password:
    m.login_withPassword(APIKey=APIKey, EmailAddress=EmailAddress, Password=Password)
  else:
    m.login_anonymously(APIKey=APIKey)
  return m

def suite(m):
  suite = unittest.TestSuite()
  suite.addTest(PySmugTestCase(m, "test_album_create"))
  suite.addTest(PySmugTestCase(m, "test_images_upload"))
  return suite

def main():
  import optparse, logging
  from getpass import getpass
  
  apiKey = "1XhqbbxNfSygsmVReGQ8nek8D2Dz8F61"
  
  p = optparse.OptionParser()
  p.add_option("-a", "--apikey", default=apiKey, action="store")
  p.add_option("-e", "--email", action="store")
  p.add_option("-v", "--debug", action="store_true", default=False)
  opts, args = p.parse_args()

  if opts.debug:
    logging.basicConfig(level=logging.DEBUG)

  if not args:
    args = [630992] # Street Photos from Moon River Photography

  password = getpass() if opts.email else None
  m = login(opts.apikey, opts.email, password)

  unittest.TextTestRunner(verbosity=2).run(suite(m))

if __name__ == '__main__':
  main()
