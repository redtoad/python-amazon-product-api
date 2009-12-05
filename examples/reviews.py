# ~*~ encoding: iso-8859-1

"""
Get all reviews for books with the specified ISBNs.
"""

import sys
from textwrap import fill

from config import AWS_KEY, SECRET_KEY
from amazonproduct import API
from amazonproduct import ResultPaginator

if __name__ == '__main__':
    
    if len(sys.argv[1:]) == 0:
        print __doc__
        print 'Usage: %s ISBN' % sys.argv[0]
        sys.exit(1)
    
    for isbn in sys.argv[1:]:

        isbn = isbn.replace('-', '')
        
        api = API(AWS_KEY, SECRET_KEY)
        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')
        
        for root in paginator(api.item_lookup, isbn, IdType='ISBN', 
                             SearchIndex='Books', ResponseGroup='Reviews'):
        
            rating = root.Items.Item.CustomerReviews.AverageRating.pyval
            total_reviews = root.Items.Item.CustomerReviews.TotalReviews.pyval
            review_pages = root.Items.Item.CustomerReviews.TotalReviewPages.pyval
            try:
                current_page = root.Items.Request.ItemLookupRequest.ReviewPage.pyval
            except AttributeError:
                current_page = 1
                
            print '%d reviews' % total_reviews,
            print 'requested page %d of %d' % (current_page, review_pages)
            
            nspace = root.nsmap.get(None, '')
            reviews = root.xpath('//aws:CustomerReviews/aws:Review', 
                                namespaces={'aws' : nspace})
            for review in reviews:
                print '%s %-5s %s: %s' % (review.Date, '*' * review.Rating.pyval,  
                                          unicode(review.Reviewer.Name),
                                          unicode(review.Summary))
