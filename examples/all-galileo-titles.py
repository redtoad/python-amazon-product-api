
"""
Get all books published by "Galileo Press".
"""

from config import AWS_KEY, SECRET_KEY
from amazonproduct import API
from amazonproduct import ResultPaginator

if __name__ == '__main__':
    
    api = API(AWS_KEY, SECRET_KEY, 'us')
    
    paginator = ResultPaginator('ItemPage',
        '//aws:Items/aws:Request/aws:ItemSearchRequest/aws:ItemPage',
        '//aws:Items/aws:TotalPages',
        '//aws:Items/aws:TotalResults', 
        limit=5)
    
    for root in paginator(api.item_search, search_index='Books', 
                          Publisher='Galileo Press'):
    
        total_results = root.Items.TotalResults.pyval
        total_pages = root.Items.TotalPages.pyval
        try:
            current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
        except AttributeError:
            current_page = 1
            
        print 'page %d of %d' % (current_page, total_pages)
        
        #~ from lxml import etree
        #~ print etree.tostring(root, pretty_print=True)
        
        nspace = root.nsmap.get(None, '')
        books = root.xpath('//aws:Items/aws:Item', 
                             namespaces={'aws' : nspace})
        
        for book in books:
            print book.ASIN,
            print unicode(book.ItemAttributes.Author), ':', 
            print unicode(book.ItemAttributes.Title)
            