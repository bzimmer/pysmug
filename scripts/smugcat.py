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
    self.m = pysmug.login()
  
  def sharegroups(self, fields=None):
    sgs = dict()
    b = self.m.batch()
    for sg in self.m.sharegroups_get()["ShareGroups"]:
      gid, gkey = sg["id"], sg["ShareTag"]
      sgs[(gid, gkey)] = sg["Name"]
      b.sharegroups_getInfo(ShareTag=gkey, ShareGroupID=gid)
    
    for params, results in b():
      gid, gkey = params["ShareGroupID"], params["ShareTag"]
      idkeys = [(x["id"], x["Key"]) for x in results["ShareGroup"]["Albums"]]

      yield (sgs[(gid, gkey)], list(self.cat(fields, idkeys)))

  def cat(self, fields=None, idkeys=None):
    b = self.m.batch()
    
    if not idkeys:
      idkeys = list()
      for album in self.m.albums_get()["Albums"]:
        idkeys.append((album["id"], album["Key"]))

    for aid, akey in idkeys:
      b.albums_getInfo(AlbumID=aid, AlbumKey=akey)

    for params, results in b():
      album = results["Album"]
      albumId = params["AlbumID"]

      name = album["Title"]
      category = album.get("Category", {}).get("Name", None)
      subcategory = album.get("SubCategory", {}).get("Name", None)

      m = [(category or "", subcategory or "", name)]
  
      if fields:
        for field in fields:
          m.append((field, results["Album"][field]))
      yield m

if __name__ == '__main__':
  from optparse import OptionParser
  p = OptionParser()
  p.add_option("-s", "--sharegroups", dest="sharegroups", default=False, action="store_true", help="display sharegroup")
  p.add_option("-f", "--fields", dest="fields", default=[], action="append", help="list of fields to display")
  opts, args = p.parse_args()
  
  sd = SmugCat()
  if opts.sharegroups:
    for sg, albums in sd.sharegroups(opts.fields):
      print sg
      for a in albums:
        print "", a
  else:
    for a in sd.cat(opts.fields):
      print a
