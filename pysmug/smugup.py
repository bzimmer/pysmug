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

import os
import pysmug
import logging
from optparse import OptionParser

logger = logging.getLogger(__name__)

def smugup(opts, args):
    albumId = opts.album
    if "_" in albumId:
        albumId, albumKey = albumId.split("_")
    logger.info("using album %s", albumId)

    # login
    m = pysmug.login()

    filenames = set()
    if not opts.overwrite:
        # get the current filenames
        images = m.images_get(albumId=albumId, albumKey=albumKey, heavy=True)
        [filenames.add(x["FileName"]) for x in images["Album"]["Images"]]

    # check for files to upload
    n = 0
    b = m.batch()
    b.concurrent = 2
    for arg in args:
        basename = os.path.basename(arg)
        if basename in filenames:
            logger.warning("skipping %s", arg)
            continue
        n += 1
        logger.info("uploading %s", arg)
        b.images_upload(albumId=albumId, filename=arg)

    # upload
    logger.info("uploading %d files", n)
    for i, (params, result) in enumerate(b()):
        logger.info("uploaded (%d/%d) %s", i, n, result)

def main(argv=None):
    fmt = '%(asctime)s|%(name)s|%(levelname)s|%(funcName)s|%(message)s'
    logging.basicConfig(format=fmt, level=logging.INFO)

    p = OptionParser()
    p.add_option("-a", "--album", dest="album",
        default=None, action="store", help="the album to store the images")
    p.add_option("-o", "--overwrite", dest="overwrite",
        default=False, action="store_true", help="overwrite existing files")
    opts, args = p.parse_args()

    if not opts.album:
        return

    smugup(opts, args)

