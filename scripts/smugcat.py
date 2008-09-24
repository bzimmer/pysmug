#! /usr/bin/python

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

_fields = [
  "SquareThumbs", "Public", "Passworded",
  "PasswordHint", "Password", "SortMethod",
  "SortDirection"
]

class SmugCat(object):
  
  def __init__(self):
    self._albums = dict()
  
  def cat(self, fields=None):
    m = pysmug.login()
    b = m.batch()
    
    albums = dict()
    for album in m.albums_get()["Albums"]:
      category = album.get("Category", {}).get("Name", None)
      subcategory = album.get("SubCategory", {}).get("Name", None)
      albumId, name, key = album["id"], album["Title"], album["Key"]
      
      m = []
      if category:
        m.append(category)
      if subcategory:
        m.append(subcategory)
      m.append(name)
      albums[albumId] = " > ".join(m)
      if fields:
        b.albums_getInfo(AlbumID=albumId, AlbumKey=key)
    
    if fields:
      for params, results in b():
        albumId = params["AlbumID"]
        m = [albums[albumId]]
        if fields:
          for field in fields:
            m.append("%s=%s" % (field, results["Album"][field]))
        yield "; ".join(m)
    else:
      for a in albums.values():
        yield a

if __name__ == '__main__':
  from optparse import OptionParser
  p = OptionParser()
  p.add_option("-f", "--fields", dest="fields", default=[], action="append", help="list of fields to display")
  opts, args = p.parse_args()
  
  sd = SmugCat()
  for a in sd.cat(opts.fields):
    print a
