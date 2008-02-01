
import smexample

class Example(smexample.Example):
  
  def example(self, albumId):
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

    # execute the batch request
    for (params, value) in b():
      try:
        exc = value.get("exception", None)
        if exc:
          raise exc
      except Exception, e:
        print str(params) + " -->"
        print "", e

if __name__ == "__main__":
  smexample.main(Example)

