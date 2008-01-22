
import urllib
import datetime
import smexample
from pysmug import SmugMugException

class Example(smexample.Example):

  def example(self, *args, **kwargs):
    tree = self.m.users_getTree()

    categories = {}
    for q in self.m.categories_get()["Categories"]:
      categories[q["Name"]] = q["id"]

    categoryId = categories.get("Testing", None)
    if categoryId is None:
      category = self.m.categories_create(Name="Testing")
      categoryId = category["Category"]["id"]

    if not "ReTesting" in categories:
      self.m.categories_rename(CategoryID=categoryId, Name="ReTesting")

    title = "NewAlbum-%s" % (datetime.datetime.now())
    album = self.m.albums_create(Title=title, CategoryID=categoryId)
    albumId = album["Album"]["id"]
    try:
      images = self.m.images_get(AlbumID=albumId)
    except SmugMugException, e:
      assert e.code == 15 # empty set
    assert self.m.albums_getInfo(AlbumID=albumId)["Album"]["Category"]["id"] == categoryId
    google = urllib.urlopen("http://www.google.com/intl/en_ALL/images/logo.gif").read()
    image = self.m.images_upload(Data=google, FileName="google.gif", AlbumID=albumId)
    raw_input("check the album...")
    images = self.m.images_get(AlbumID=albumId, Heavy=1)
    for a in images["Images"]:
      print a
    self.m.albums_delete(AlbumID=albumId)
    self.m.categories_delete(CategoryID=categoryId)

if __name__ == '__main__':
  smexample.main(Example)

