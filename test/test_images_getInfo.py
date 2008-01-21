
import optparse
from pysmug import SmugMug

APIKey = "1XhqbbxNfSygsmVReGQ8nek8D2Dz8F61"

def test(albumId=630992):
  # login
  m = SmugMug().login_anonymously(APIKey=APIKey)
  b = m.batch()
  
  album = m.albums_getInfo(AlbumID=albumId)
  print
  print "Album:", album["Album"]["Title"]

  images = m.images_get(AlbumID=albumId)
  for image in images["Images"]:
    # add each image to the batch
    b.images_getInfo(ImageID=image["id"], Heavy=1)

  count = 0
  max_time = 0.0
  total_time = 0.0

  # execute the batch request
  for (params, value) in b():
    count += 1
    stats = value["Statistics"]
    max_time = max(max_time, stats["total-time"])
    total_time += stats["total-time"]

  # print some stats
  print "Number of photos:", count
  print "Synchronously:", total_time
  print "Asynchronously:", max_time

p = optparse.OptionParser()
opts, args = p.parse_args()
if not args:
  args = [630992] # Street Photos from Moon River Photography

for arg in args:
  test(int(arg))
raise SystemExit()

