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

"""This module provides some lower-level metadata used to communicate with the
SmugMug API.
"""

methods = set([
    'smugmug.albums.applyWatermark',
    'smugmug.albums.changeSettings',
    'smugmug.albums.create',
    'smugmug.albums.delete',
    'smugmug.albums.get',
    'smugmug.albums.getInfo',
    'smugmug.albums.getStats',
    'smugmug.albums.reSort',
    'smugmug.albums.removeWatermark',
    'smugmug.albumtemplates.changeSettings',
    'smugmug.albumtemplates.create',
    'smugmug.albumtemplates.delete',
    'smugmug.albumtemplates.get',
    'smugmug.categories.create',
    'smugmug.categories.delete',
    'smugmug.categories.get',
    'smugmug.categories.rename',
    'smugmug.communities.get',
    'smugmug.communities.getAvailable',
    'smugmug.communities.join',
    'smugmug.communities.leave',
    'smugmug.communities.leaveAll',
    'smugmug.family.add',
    'smugmug.family.get',
    'smugmug.family.remove',
    'smugmug.family.removeAll',
    'smugmug.friends.add',
    'smugmug.friends.get',
    'smugmug.friends.remove',
    'smugmug.friends.removeAll',
    'smugmug.images.applyWatermark',
    'smugmug.images.changePosition',
    'smugmug.images.changeSettings',
    'smugmug.images.crop',
    'smugmug.images.delete',
    'smugmug.images.get',
    'smugmug.images.getEXIF',
    'smugmug.images.getInfo',
    'smugmug.images.getStats',
    'smugmug.images.getURLs',
    'smugmug.images.pricing',
    'smugmug.images.removeWatermark',
    'smugmug.images.rotate',
    #'smugmug.images.upload',
    'smugmug.images.uploadFromURL',
    'smugmug.images.zoomThumbnail',
    'smugmug.login.anonymously',
    'smugmug.login.withHash',
    'smugmug.login.withPassword',
    'smugmug.orders.get',
    'smugmug.orders.ship',
    'smugmug.propricing.getAlbum',
    'smugmug.propricing.getImage',
    'smugmug.propricing.getPortfolio',
    'smugmug.propricing.setAlbum',
    'smugmug.propricing.setImage',
    'smugmug.propricing.setPortfolio',
    'smugmug.sharegroups.addAlbum',
    'smugmug.sharegroups.changeSettings',
    'smugmug.sharegroups.create',
    'smugmug.sharegroups.delete',
    'smugmug.sharegroups.get',
    'smugmug.sharegroups.getInfo',
    'smugmug.sharegroups.removeAlbum',
    'smugmug.styles.getTemplates',
    'smugmug.subcategories.create',
    'smugmug.subcategories.delete',
    'smugmug.subcategories.get',
    'smugmug.subcategories.getAll',
    'smugmug.subcategories.rename',
    'smugmug.themes.get',
    'smugmug.users.getDisplayName',
    'smugmug.users.getTransferStats',
    'smugmug.users.getTree',
    'smugmug.watermarks.changeSettings',
    'smugmug.watermarks.createnew',
    'smugmug.watermarks.delete',
    'smugmug.watermarks.get',
    'smugmug.watermarks.getInfo'
])
"""Valid methods for the SmugMug (+ extended) API.
"""

