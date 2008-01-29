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

import os
import pysmug

#####
#
# 1) scan directory structure computing (year, date) pairs in existence
# 2) query all albums looking for Category=Backup
# 3) find missing, deleted albums
# 4) *optional* for each deleted directory, delete album
# 5) for each additional directory, create album
# 6) query albums again to make sure smugmug has them all
#
######

class SmugSync:
  """Synchronize a local directory with SmugMug albums.
  """
  def __init__(self, smugmug=None):
    self.m = smugmug or pysmug.login()

  def filesystem(self, directory):
    """Scan the file system to produce a ((subcategory, title), filename) generator.

    @param directory: the root of the directory tree
    """
    while directory[-1] == os.sep:
      source = source[:-1]

    for root, dns, fns in os.walk(directory):
      if not fns:
        continue
      album = tuple([x for x in root.replace(directory, "").split(os.sep) if x])
      if not album:
        continue
      for fn in fns:
        yield (album, os.path.join(root, fn))

  def smugmug(self, category):
    """Scan the album tree to produce a ((subcategory, title), filename) generator.

    @param category: the root category for backup albums
    """
    smugmug = dict()
    b = self.m.batch()
    for a in self.m.albums_get()["Albums"]:
      if a["Category"]["Name"] == category:
        albumId = a["id"]
        smugmug[albumId] = (a["SubCategory"]["Name"], a["Title"])
        b.images_get(AlbumID=albumId, Heavy=1)
    for params, results in b():
      # the API can throw an exception if the album is empty!
      albumId = params["AlbumID"]
      for image in results.get("Images", []):
        yield (smugmug[albumId], image["FileName"])

