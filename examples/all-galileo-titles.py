
"""
Get all books published by "Galileo Press".
"""

from amazonproduct.api import API

if __name__ == '__main__':
    
    # Don't forget to create file ~/.amazon-product-api
    # with your credentials (see docs for details)
    api = API(locale='de')

    result = api.item_search('Books', Publisher='Galileo Press',
        ResponseGroup='Large')

    # extract paging information
    total_results = result.results
    total_pages = len(result)  # or result.pages

    for book in result:

        print('page %d of %d' % (result.current, total_pages))
        
        #~ from lxml import etree
        #~ print etree.tostring(book, pretty_print=True)
        
        print(
            book.ASIN,
            book.ItemAttributes.Author,
            ':',
            book.ItemAttributes.Title, end='')
        if hasattr(book.ItemAttributes, 'ListPrice'):
            print(book.ItemAttributes.ListPrice.FormattedPrice)
        elif hasattr(book.OfferSummary, 'LowestUsedPrice'):
            print('(used from %s)' % book.OfferSummary.LowestUsedPrice.FormattedPrice)

