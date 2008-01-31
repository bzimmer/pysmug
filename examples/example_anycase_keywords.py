import smexample
from pysmug import SmugMugException

class Example(smexample.Example):

  def example(self, *args, **kwargs):
    albums = self.m.albums_get()["Albums"]
    print len(albums)
    albumId = albums[0]["id"]
    print self.m.albums_getInfo(albumId=albumId)
    images = self.m.images_get(albumId=albumId)["Images"]

    imageId = images[0]["id"]

    print self.m.images_getEXIF(imaGeiD=imageId)

if __name__ == '__main__':
  smexample.main(Example)

