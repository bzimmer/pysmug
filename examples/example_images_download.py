
import datetime
import smexample

class Example(smexample.Example):
  
  def example(self, albumId):
    b = self.m.batch()
    t = datetime.datetime.now()
    for a in b.images_download(AlbumID=albumId, Format="Tiny", Path="/tmp"):
      print a
    print datetime.datetime.now() - t

if __name__ == "__main__":
  smexample.main(Example)

