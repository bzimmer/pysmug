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
import __builtin__
from optparse import OptionParser

from pysmug.keywords import smugmug_keyword

logger = logging.getLogger(__name__)

_fields = {
    u'Backprinting': None,
    u'CanRank': None,
    u'Category': (u'id', u'Name'),
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
    u'Highlight': (u'id', u'Key'),
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
    u'SubCategory': (u'id', u'Name'),
    u'Template': (u'id'),
    u'Theme': (u'id'),
    u'Title': None,
    u'UnsharpAmount': None,
    u'UnsharpRadius': None,
    u'UnsharpSigma': None,
    u'UnsharpThreshold': None,
    u'Watermark': (u'id'),
    u'Watermarking': None,
    u'WorldSearchable': None,
    u'X2Larges': None,
    u'X3Larges': None,
    u'XLarges': None,
    u'id': None
}

_names = set(dir(__builtin__) + _fields.keys())

class Predicate(object):
    """Evaluator of Python expressions.
    """
    def __init__(self, predicate):
        """Initializes the predicate.

        If the expression contains unknown names a ValueError is raised.
        """
        self.predicate = predicate
        # for name in self.names:
        #     if name not in _names:
        #         raise ValueError("{%s} not a valid field name" % (name))

    def __str__(self):
        return self.predicate

    def test(self, entity):
        return eval(self.predicate, entity)

    @property
    def names(self):
        """Returns all the variable names found in the expression.
        """
        class _Names:
            def __init__(self):
                self.names = []

            def visitName(self, node):
                self.names.append(node.name)

        ast = compiler.parse(self.predicate)
        names = compiler.walk(ast, _Names()).names
        return names

class SmugFind(object):
    """Queries SmugMug for albums and sharegroups.
    """

    def __init__(self):
        self.m = pysmug.login()
        self.fields = dict(_fields)

    def has_field(self, field):
        if field == "id": return True
        return smugmug_keyword(field) in self.fields

    def sharegroups(self, fields=None):
        """Finds sharegroups.

        @keyword fields: a list of fields to return, if None, returns (ShareKey, ShareGroupID, ShareName)
        @return: sequence of sharegroups with the requested fields
        """
        sgs = dict()
        b = self.m.batch()
        for sg in self.m.sharegroups_get()["ShareGroups"]:
            gid, gkey = sg["id"], sg["ShareTag"]
            sgs[(gid, gkey)] = sg["Name"]
            b.sharegroups_getInfo(ShareTag=gkey, ShareGroupID=gid)

        for params, results in b():
            gid, gkey = params["ShareGroupID"], params["ShareTag"]
            idkeys = [(x["id"], x["Key"]) for x in results["ShareGroup"]["Albums"]]

            p = [("ShareKey", gkey), ("ShareGroupID", gid), ("ShareName", sgs[(gid, gkey)])]

            yield (p, self.albums(fields, idkeys))

    def albums(self, fields=None, idkeys=None, predicate=None):
        """Finds albums, optionally matching a predicate.

        @keyword fields: a list of fields to return, if None, returns (Category, SubCategory, Name)
        @keyword idkeys: sequence of (AlbumID, AlbumKey) tuples to filter returned albums
        @keyword predicate: a Python expression evaluated in the context of the album data
                            if the expression evaluates False, the album is rejected
        @return: sequence of albums matching both C{idkeys} and C{predicate}, with the requested fields
        """
        # format the keyword names correctly
        def smk(x):
            if x == "id": return x
            return smugmug_keyword(x)
        fields = [smk(x) for x in fields] if fields else []
        for i in range(len(fields)-1, -1, -1):
            f = fields[i]
            if not self.has_field(f):
                logger.warn("field {%s} doesn't exist" % (f))
                del fields[i]
                continue

        # if idkeys, fetch only those albums otherwise get them all
        if not idkeys:
            idkeys = list()
            for album in self.m.albums_get()["Albums"]:
                idkeys.append((album["id"], album["Key"]))

        # get the albums
        b = self.m.batch()
        for aid, akey in idkeys:
            b.albums_getInfo(AlbumID=aid, AlbumKey=akey)

        # work the results
        for params, results in b():
            album = results["Album"]
            name = album["Title"]

            if predicate:
                try:
                    if not predicate.test(album):
                        continue
                except Exception, e:
                    logger.warn("{%s} : predicate {%s} for album '%s'", e, predicate, name)
                    continue

            m = []
            if fields:
                for field in fields:
                    m.append((field, album.get(field, None)))
            else:
                category = album.get("Category", {}).get("Name", None)
                subcategory = album.get("SubCategory", {}).get("Name", None)
                m.append((category or u"", subcategory or u"", name))
            yield m

def main(argv=None):

    p = OptionParser()
    p.add_option("-s", "--sharegroups", dest="sharegroups",
        default=False, action="store_true", help="display sharegroup")
    p.add_option("-f", "--fields", dest="fields",
        default=[], action="append", help="list of fields to display for each entity")
    p.add_option("-l", "--list", dest="list",
        default=False, action="store_true", help="available list of fields to display")
    p.add_option("-p", "--predicate", dest="predicate",
        default=None, action="store", help="predicate to evaluate")
    p.add_option("-a", "--all", dest="all",
        default=False, action="store_true", help="display all fields")
    p.add_option("", "--pretty", dest="pretty",
        default=False, action="store_true", help="pretty print results")
    opts, args = p.parse_args()

    sd = SmugFind()

    if opts.all:
        opts.fields = sd.fields.keys()

    def printer(x):
        print x

    if opts.pretty:
        from pprint import pprint as printer

    if opts.list:
        for item in sd.fields.items():
            print item
    elif opts.sharegroups:
        for sg, albums in sd.sharegroups(opts.fields):
            for a in albums:
                print (sg, sorted(a))
    else:
        p = opts.predicate and Predicate(opts.predicate) or None
        for a in sd.albums(fields=opts.fields, predicate=p):
            printer(sorted(a))

