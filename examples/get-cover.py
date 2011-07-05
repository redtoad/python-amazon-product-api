
"""
Usage: %prog [Options] ID [ID ...]

Downloads cover images from Amazon. 
"""

from optparse import OptionParser
import os.path
import sys
import urllib2

from config import AWS_KEY, SECRET_KEY
from amazonproduct.api import API

ASIN = 'ASIN'
EAN = 'EAN'
SKU = 'SKU'
UPC = 'UPC'

def fetch_image(url, dest_path):
    """
    Downloads image and saves it to ``dest_path``.
    """
    fp = open(dest_path, 'wb')
    fp.write(urllib2.urlopen(url).read())
    fp.close()

if __name__ == '__main__':
    
    parser = OptionParser(__doc__.strip())
    parser.set_defaults(id_type=EAN, verbose=True)
    parser.add_option('--ean', action='store_const', dest='id_type', const=EAN,
        help='ID is an European Article Number (EAN) [default]')
    parser.add_option('--asin', action='store_const', dest='id_type', const=ASIN,
        help='ID is an Amazon Standard Identification Number (ASIN).')
    parser.add_option('--upc', action='store_const', dest='id_type', const=UPC,
        help='ID is an Universal Product Code (UPC).')
    parser.add_option('--sku', action='store_const', dest='id_type', const=SKU,
        help='ID is an Stock Keeping Unit (SKU).')
    parser.add_option('-q', '--quiet', action='store_false', dest='verbose', 
        help='Suppress output.')
    
    (options, ids) = parser.parse_args(sys.argv[1:])
    
    if len(ids) == 0:
        parser.error('No IDs specified!')
    
    api = API(AWS_KEY, SECRET_KEY, 'de')
    
    params = {
        'ResponseGroup' : 'Images',
        'SearchIndex' : 'All',
        'IdType' : options.id_type, 
    }
    
    # When IdType equals ASIN, SearchIndex cannot be present.
    if options.id_type == ASIN:
        del params['SearchIndex']

    for id in ids:
        
        id = id.replace('-', '')
        
        if options.verbose: print 'Fetching info for %s...' % id
        root = api.item_lookup(id, **params)
        
        #~ from lxml import etree
        #~ print etree.tostring(root, pretty_print=True)
        
        url = root.Items.Item.LargeImage.URL.pyval
        name, ext = os.path.splitext(url)
        path = '%s%s' % (id, ext)
        if options.verbose: print 'Downloading %s to %s ...' % (url, path)
        fetch_image(url, path)
        
