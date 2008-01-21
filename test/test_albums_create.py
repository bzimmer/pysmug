
import pysmug
import logging, urllib, datetime
logging.basicConfig(level=logging.DEBUG)

m = pysmug.login()
tree = m.users_getTree()

categories = {}
for q in m.categories_get()["Categories"]:
  categories[q["Name"]] = q["id"]

categoryId = categories.get("Testing", None)
if categoryId is None:
  category = m.categories_create(Name="Testing")
  categoryId = category["Category"]["id"]

if not "ReTesting" in categories:
  m.categories_rename(CategoryID=categoryId, Name="ReTesting")

album = m.albums_create(Title="NewAlbum-%s" % (datetime.datetime.now()), CategoryID=categoryId)
albumId = album["Album"]["id"]
try: images = m.images_get(AlbumID=albumId)
except pysmug.SmugMugException, e: print e.message
assert m.albums_getInfo(AlbumID=albumId)["Album"]["Category"]["id"] == categoryId
google = urllib.urlopen("http://www.google.com/intl/en_ALL/images/logo.gif").read()
image = m.images_upload(Data=google, FileName="google.gif", AlbumID=albumId)
x = raw_input("check the album...")
images = m.images_get(AlbumID=albumId, Heavy=1)
for a in images["Images"]:
  print a
m.albums_delete(AlbumID=albumId)
m.categories_delete(CategoryID=categoryId)

