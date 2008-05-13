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

import pysmug
import collections

class SmugTool(pysmug.SmugMug):

  def categories_getTree(self):
    """Return the tree of categories and sub-categories.

    The format of the response tree::

      {u'Categories': [{u'Name': u'Other', 'SubCategories': {}, u'id': 0},
                       {u'Name': u'Airplanes', 'SubCategories': {}, u'id': 41},
                       {u'Name': u'Animals', 'SubCategories': {}, u'id': 1},
                       {u'Name': u'Aquariums', 'SubCategories': {}, u'id': 25},
                       {u'Name': u'Architecture', 'SubCategories': {}, u'id': 2},
                       {u'Name': u'Art', 'SubCategories': {}, u'id': 3},
                       {u'Name': u'Arts and Crafts', 'SubCategories': {}, u'id': 43},
                       ...,
                       ],
       u'method': u'pysmug.categories.getTree',
       u'stat': u'ok'}
    """
    b = self.batch()
    b.categories_get()
    b.subcategories_getAll()

    methods = dict()
    for params, results in b():
      methods[params["method"]] = results

    subcategories = collections.defaultdict(list)
    for subcategory in methods["smugmug.subcategories.getAll"]["SubCategories"]:
      category = subcategory.pop("Category")
      subcategories[category["id"]].append(subcategory)

    categories = methods["smugmug.categories.get"]["Categories"]
    for category in categories:
      category["SubCategories"] = subcategories.get(category["id"], {})

    return {u"method":u"pysmug.categories.getTree", u"Categories":categories, u"stat":u"ok"}

  @pysmug.smugmug_keywords
  def albums_details(self, **kwargs):
    """Returns the full details of an album including EXIF data for all images.  It
    is the composition of calls to C{albums_getInfo}, C{images_getInfo} and
    C{images_getEXIF} where the C{images_*} calls are done in batch. The primary purpose
    for this method is to provide easy access to a full album worth of metadata quickly.

    The format of the response tree::

      {'Album': {'Attribute1': 'Value1',
                 'AttributeN': 'ValueN',
                 'Images': [{'EXIF': {'EXIFAttribute1': 'EXIFValue1',
                                      'EXIFAttributeN': 'EXIFValueN'},
                             'ImageAttribute1': 'ImageValue1',
                             'ImageAttributeN': 'ImageAttributeN'},
                            {'EXIF': {'EXIFAttribute1': 'EXIFValue1',
                                      'EXIFAttributeN': 'EXIFValueN'},
                             'ImageAttribute1': 'ImageValue1',
                             'ImageAttributeN': 'ImageAttributeN'}]},
       'Statistics': {},
       'method': 'pysmug.albums.details',
       'stat': 'ok'}

    @keyword albumId: the id of the album to query
    @keyword albumKey: the key of the album to query
    @keyword exif: returns EXIF metadata about each image
    @return: a dictionary of the album and image details
    """
    albumId = kwargs.get("AlbumID")
    albumKey = kwargs.get("AlbumKey")
    exif = kwargs.get("Exif")
    album = self.albums_getInfo(albumId=albumId, albumKey=albumKey)
    images = self.images_get(albumId=albumId, albumKey=albumKey)

    # map
    b = self.batch()
    for imageId, imageKey in ((image["id"], image["Key"]) for image in images["Images"]):
      # add each image to the batch
      b.images_getInfo(imageID=imageId, imageKey=imageKey)
      if exif:
        b.images_getEXIF(imageID=imageId, imageKey=imageKey)

    # combine
    responses = collections.defaultdict(dict)
    for (params, value) in b():
      imageIdKey = (params["ImageID"], params["ImageKey"])
      responses[imageIdKey][params["method"]] = value

    # reduce
    album[u"Album"][u"Images"] = images = []
    for value in responses.values():
      img = value["smugmug.images.getInfo"]["Image"]
      if exif:
        img[u"EXIF"] = value["smugmug.images.getEXIF"]["Image"]
      images.append(img)

    # return
    album.update({u"method":u"pysmug.albums.details", u"stat":u"ok", u"Statistics":{}})
    return album

  def unused_albums(self):
    """Returns a generator of albums with ImageCount == 0.
    
    @return: a generator of albums with an image count == 0
    """
    b = self.batch()
    for album in self.albums_get()["Albums"]:
      b.albums_getInfo(albumId=album["id"], albumKey=album["Key"])
    return (info["Album"] for params, info in b() if info["Album"]["ImageCount"] == 0)

  def unused_categories(self):
    """Returns a generator of categories or subcategories with no
    albums.
    
    @return: a generator of [sub]categories with no associated albums
    """
    used = dict()
    albums = self.albums_get()["Albums"]
    for album in albums:
      category = album["Category"]
      used[("category", category["id"])] = category
      subcategory = album.get("SubCategory", None)
      if subcategory:
        used[("subcategory", album["SubCategory"]["id"])] = subcategory
    tree = self.categories_getTree()
    for c in tree["Categories"]:
      cid = ("category", c["id"])
      if not cid in used:
        c["Type"] = "Category"
        yield c
      for s in c["SubCategories"]:
        sid = ("subcategory", s["id"])
        if not sid in used:
          s["Type"] = "SubCategory"
          yield s

