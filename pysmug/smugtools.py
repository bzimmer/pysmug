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

def unused_albums(smugmug=None):
  """Returns a generator of albums with ImageCount == 0.
  """
  m = smugmug or pysmug.login()

  b = m.batch()
  for album in m.albums_get()["Albums"]:
    b.albums_getInfo(albumId=album["id"], albumKey=album["Key"])
  for (params, info) in b():
    imageCount = info["Album"].get("ImageCount", 0)
    if imageCount == 0:
      yield info

def unused_categories(smugmug=None):
  """Returns a generator of categories or subcategories with no
  albums.
  """
  m = smugmug or pysmug.login()

  used = dict()
  albums = m.albums_get()["Albums"]
  for album in albums:
    category = album["Category"]
    used[("category", category["id"])] = category
    subcategory = album.get("SubCategory", None)
    if subcategory:
      used[("subcategory", album["SubCategory"]["id"])] = subcategory
  tree = m.categories_getTree()
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

