# Copyright (c) 2008 Brian Zimmer <bzimmer@ziclix.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pysmug import SmugMug, SmugBatch, SmugMugException
from pysmug.tests import SmugSupport

_support = None
def setup():
  global _support
  _support = SmugSupport()

def test_album_create():
  album = _support.create_album()
  _support.delete_album(album)
  try:
    album = _support.m.albums_getInfo(albumId=album["id"], albumKey=album["Key"])
    raise Exception("should fail to deleted query album")
  except SmugMugException, e:
    assert e.code == 5

def test_album_changeSettings():
  album = _support.create_album()
  album = _support.m.albums_getInfo(albumId=album["id"], albumKey=album["Key"])["Album"]
  assert album["Title"] != "PySmug!!"
  _support.m.albums_changeSettings(albumId=album["id"], albumKey=album["Key"], title="PySmug!!")
  album = _support.m.albums_getInfo(albumId=album["id"], albumKey=album["Key"])["Album"]
  assert album["Title"] == "PySmug!!"
  _support.delete_album(album)

def test_mixedcased_keywords():
  album = _support.m.albums_get()["Albums"][0]
  info = _support.m.albums_getInfo(albumid=album["id"], aLbUmKeY=album["Key"])
  assert album["id"] == info["Album"]["id"]

def test_unused_albums():
  tool = _support.tool()
  album = _support.create_album()
  albums = [(a["id"], a["Key"]) for a in tool.unused_albums()]
  assert (album["id"], album["Key"]) in albums, "expected to find album in unused albums"
  _support.delete_album(album)
  
def test_query_of_empty_album():
  album = _support.create_album()
  try:
    # this tests both strict raising an exception and the conversion of True to 1
    _support.m.images_get(albumid=album["id"], albumKey=album["Key"], strict=True)
    raise Exception("querying")
  except SmugMugException, e:
    pass

  # in version 1.2.2 of the API these should pass
  _support.m.images_get(albumid=album["id"], albumKey=album["Key"])
  _support.m.images_get(albumid=album["id"], albumKey=album["Key"], strict=0)
  _support.m.images_get(albumid=album["id"], albumKey=album["Key"], strict=False)
  _support.m.images_get(albumid=album["id"], albumKey=album["Key"], strict="false")

  _support.delete_album(album)

def test_image_upload():
  import os, uuid

  filenames = set()

  album = _support.create_album()
  filename = _support.image()
  filenames.add(os.path.split(filename)[-1])
  _support.m.images_upload(filename=filename, albumId=album["id"])

  image = open(filename, "rb").read()

  b = _support.m.batch()
  for i in range(3):
    filename = str(uuid.uuid1())
    filenames.add(filename)
    b.images_upload(filename=filename, data=image, albumId=album["id"])

  images = list(b())
  assert len(images) == 3

  tool = _support.tool()
  details = tool.albums_details(albumId=album["id"], albumKey=album["Key"], exif=False)
  for image in details["Album"]["Images"]:
    # the set will raise an exception if the filename is not a member
    filenames.remove(image["FileName"])
  assert len(filenames) == 0, filenames

  _support.delete_album(album)

def test_protocol():
  m = SmugMug(secure=True)
  assert m.protocol == "https", "expected https protocol"
  b = m.batch()
  assert b.protocol == "https", "expected https protocol"

def test_version():
  m = SmugMug()
  assert m.version == "1.2.2", "expected version 1.2.2"
  m.version = "1.2.1"
  assert m.version == "1.2.1", "expected version 1.2.1"
  b = m.batch()
  assert b.version == "1.2.1", "expected version 1.2.1"
  b = SmugBatch()
  assert b.version == "1.2.2", "expected version 1.2.2"

def test_concurrent():
  m = SmugBatch()
  assert m.concurrent == 10
  m = SmugBatch(concurrent=5)
  assert m.concurrent == 5

