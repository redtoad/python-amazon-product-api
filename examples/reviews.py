# ~*~ encoding: iso-8859-1

"""
Get all editorial reviews for books with the specified ISBNs.
"""

import sys
from textwrap import fill

from config import AWS_KEY, SECRET_KEY
from amazonproduct.api import API

if __name__ == '__main__':
    
    if len(sys.argv[1:]) == 0:
        print __doc__
        print 'Usage: %s ISBN' % sys.argv[0]
        sys.exit(1)
    
    for isbn in sys.argv[1:]:

        isbn = isbn.replace('-', '')
        
        api = API(AWS_KEY, SECRET_KEY, 'us')
        for root in api.item_lookup(isbn, IdType='ISBN', 
                             SearchIndex='Books', ResponseGroup='EditorialReview'):
            nspace = root.nsmap.get(None, '')
            reviews = root.xpath('//aws:EditorialReview', 
                                namespaces={'aws' : nspace})
            for review in reviews:
                print str(review.Source)
                print '-' * 40
                print str(review.Content)
