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
import datetime

class SmugSupport(object):
  def __init__(self):
    self.m = pysmug.login()
  
  def tool(self):
    return pysmug.SmugTool(sessionId=self.m.sessionId)

  def image(self):
    basedir = os.path.dirname(__file__)
    return os.path.join(basedir, "586d23772af1e918220df957f670fefd.jpg")

  def create_category(self, name="PySmug"):
    categories = self.m.categories_get()["Categories"]
    for category in categories:
      if category["Name"] == name:
        return category["id"]
    category = self.m.categories_create(name=name)
    return category["Category"]["id"]

  def create_album(self):
    title = "TestAlbum-%s" % (datetime.datetime.now())
    categoryId = self.create_category()
    return self.m.albums_create(Title=title, categoryId=categoryId, public=False)["Album"]

  def delete_album(self, album):
    aid, akey = album if isinstance(album, tuple) else (album["id"], album["Key"])
    self.m.albums_delete(albumId=aid, albumKey=akey)
