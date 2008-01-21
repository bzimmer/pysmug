
import urllib
import pysmug
import datetime

image = urllib.urlopen("http://www.seattlesrestaurants.info/www.seattlesrestaurants.info/images/large/The-Seattle-Art-Museum-443x590.jpg").read()

m = pysmug.login()
album = m.albums_create(Title="FooBar-%s" % datetime.datetime.now())
albumId = album["Album"]["id"]

b = m.batch()
for i in range(50):
  b.images_upload(Data=image, FileName="image-%02d.jpg" % (i), AlbumID=albumId)
for (params, result) in b():
  print params, result['Statistics']

