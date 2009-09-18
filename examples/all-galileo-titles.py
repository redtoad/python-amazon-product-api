
"""
Get all books published by "Galileo Press".
"""

from config import AWS_KEY, SECRET_KEY
from amazon.product import ProductAdvertisingAPI

if __name__ == '__main__':
    
    api = ProductAdvertisingAPI(AWS_KEY, SECRET_KEY)
    root = api.item_search('Books', Publisher='Galileo Press', ItemPage=2)
    
    #from lxml import etree
    #print etree.tostring(root, pretty_print=True)
    
    total_results = root.Items.TotalResults.pyval
    total_pages = root.Items.TotalPages.pyval
    try:
        current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
    except AttributeError:
        current_page = 1
        
    print '%d results' % total_results
    print 'page %d of %d' % (current_page, total_pages)
    
    nspace = root.nsmap.get(None, '')
    books = root.xpath('//aws:Items/aws:Item', 
                         namespaces={'aws' : nspace})
    
    for book in books:
        print book.ASIN,
        print unicode(book.ItemAttributes.Author), ':', 
        print unicode(book.ItemAttributes.Title)
