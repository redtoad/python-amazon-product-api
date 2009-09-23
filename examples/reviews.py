# ~*~ encoding: iso-8859-1

"""
Get all reviews for books with the specified ISBNs.
"""
from heapq import nsmallest

import sys
from textwrap import fill
from config import AWS_KEY, SECRET_KEY
from amazon.product import API

if __name__ == '__main__':
    
    if len(sys.argv[1:]) == 0:
        print __doc__
        print 'Usage: %s ISBN' % sys.argv[0]
        sys.exit(1)
    
    for isbn in sys.argv[1:]:

        isbn = isbn.replace('-', '')
        
        api = API(AWS_KEY, SECRET_KEY)
        root = api.item_lookup(isbn, IdType='ISBN', SearchIndex='Books', 
                            ResponseGroup='Reviews', ReviewPage=1)
        
        rating = root.Items.Item.CustomerReviews.AverageRating.pyval
        total_reviews = root.Items.Item.CustomerReviews.TotalReviews.pyval
        review_pages = root.Items.Item.CustomerReviews.TotalReviewPages.pyval
        try:
            current_page = root.Items.Request.ItemLookupRequest.ReviewPage.pyval
        except AttributeError:
            current_page = 1
        
        print 'ISBN %s' % isbn
        print '%d reviews' % total_reviews,
        print 'with avg. rating of %d stars' % rating
        print 'displaying page %d of %d' % (current_page, review_pages)
        print 
        
        nspace = root.nsmap.get(None, '')
        reviews = root.xpath('//aws:CustomerReviews/aws:Review', 
                            namespaces={'aws' : nspace})
        
        for review in reviews:
            #print review.ASIN
            print unicode(review.Reviewer.Name),
            print '*' * review.Rating.pyval,
            print review.Date
            print unicode(review.Summary)
            print '-'*80
            print fill(unicode(review.Content), 80)
            print '%i von %i fanden das hilfreich' % (review.HelpfulVotes, 
                                                    review.TotalVotes)
            print
            
