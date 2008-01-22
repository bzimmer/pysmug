
import smtest
import urllib
import datetime

class Test(smtest.Test):

  def test(self, *args, **kwargs):
    gn = "http://www.spreadfirefox.com/files/images/TMlogo_750x750.thumbnail.jpg"
    image = urllib.urlopen(gn).read()
    album = self.m.albums_create(Title="FooBar-%s" % datetime.datetime.now())
    albumId = album["Album"]["id"]

    b = self.m.batch()
    for i in range(50):
      b.images_upload(Data=image, FileName="image-%02d.jpg" % (i), AlbumID=albumId)
    for (params, result) in b():
      print params, result['Statistics']

    raw_input("check the gallery...")

    self.m.albums_delete(AlbumID=albumId)

if __name__ == '__main__':
  smtest.main(Test)

