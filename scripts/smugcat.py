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
import logging
import compiler

_log = logging.getLogger("smugcat")

_fields = {
 u'Backprinting': None,
 u'CanRank': None,
 u'Category': [u'id', u'Name'],
 u'Clean': None,
 u'Comments': None,
 u'DefaultColor': None,
 u'Description': None,
 u'EXIF': None,
 u'External': None,
 u'FamilyEdit': None,
 u'Filenames': None,
 u'FriendEdit': None,
 u'Geography': None,
 u'Header': None,
 u'HideOwner': None,
 u'Highlight': [u'id', u'Key'],
 u'ImageCount': None,
 u'Key': None,
 u'Keywords': None,
 u'Larges': None,
 u'LastUpdated': None,
 u'Originals': None,
 u'Password': None,
 u'PasswordHint': None,
 u'Passworded': None,
 u'Position': None,
 u'Printable': None,
 u'ProofDays': None,
 u'Protected': None,
 u'Public': None,
 u'Share': None,
 u'SmugSearchable': None,
 u'SortDirection': None,
 u'SortMethod': None,
 u'SquareThumbs': None,
 u'SubCategory': [u'id', u'Name'],
 u'Template': [u'id'],
 u'Theme': [u'id'],
 u'Title': None,
 u'UnsharpAmount': None,
 u'UnsharpRadius': None,
 u'UnsharpSigma': None,
 u'UnsharpThreshold': None,
 u'Watermark': [u'id'],
 u'Watermarking': None,
 u'WorldSearchable': None,
 u'X2Larges': None,
 u'X3Larges': None,
 u'XLarges': None,
 u'id': None
}

class Names:
  def __init__(self):
    self.names = []
  
  def visitName(self, node):
    self.names.append(node.name)

class Predicate(object):
  def __init__(self, predicate):
    self.predicate = predicate
    for name in self.names:
      if name not in _fields:
        raise ValueError("{%s} not a valid field name" % (name))
  
  def __str__(self):
    return self.predicate
  
  def test(self, entity):
    return eval(self.predicate, entity)
  
  @property
  def names(self):
    ast = compiler.parse(self.predicate)
    return compiler.walk(ast, Names()).names

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
  
  def cat(self, fields=None, idkeys=None, predicate=None):
    b = self.m.batch()
    
    if not idkeys:
      idkeys = list()
      for album in self.m.albums_get()["Albums"]:
        idkeys.append((album["id"], album["Key"]))
    
    for aid, akey in idkeys:
      b.albums_getInfo(AlbumID=aid, AlbumKey=akey)
    
    for params, results in b():
      album = results["Album"]
      name = album["Title"]
      
      if predicate:
        try:
          if not predicate.test(album):
            continue
        except Exception, e:
          _log.warn("{%s} : predicate {%s} for album '%s'", e, predicate, name)
          continue
      
      category = album.get("Category", {}).get("Name", None)
      subcategory = album.get("SubCategory", {}).get("Name", None)
      m = [(category or u"", subcategory or u"", name)]
      
      if fields:
        for field in fields:
          m.append((field, album[field]))
      yield m

if __name__ == '__main__':
  from optparse import OptionParser
  p = OptionParser()
  p.add_option("-s", "--sharegroups", dest="sharegroups", default=False, action="store_true", help="display sharegroup")
  p.add_option("-f", "--fields", dest="fields", default=[], action="append", help="list of fields to display for each entity")
  p.add_option("-l", "--list", dest="list", default=False, action="store_true", help="available list of fields to display")
  p.add_option("-p", "--predicate", dest="predicate", default=None, action="store", help="predicate to evaluate")
  opts, args = p.parse_args()
  
  sd = SmugCat()
  if opts.list:
    for item in _fields.items():
      print item
  elif opts.sharegroups:
    for sg, albums in sd.sharegroups(opts.fields):
      print sg
      for a in albums:
        print "", a
  else:
    p = opts.predicate and Predicate(opts.predicate) or None
    for a in sd.cat(fields=opts.fields, predicate=p):
      print a
