
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
  smexample.main(Example)

