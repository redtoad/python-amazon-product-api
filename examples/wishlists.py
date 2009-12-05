
"""
Find a wish list and get all items on it.
"""

from config import AWS_KEY, SECRET_KEY
from amazonproduct import API
from amazonproduct import ResultPaginator

api = API(AWS_KEY, SECRET_KEY)

lists_paginator = ResultPaginator('ListPage',
        '//aws:Lists/aws:Request/aws:ListSearchRequest/aws:ListPage',
        '//aws:Lists/aws:TotalPages',
        '//aws:Lists/aws:TotalResults')
items_paginator = ResultPaginator('ProductPage',
        '//aws:Lists/aws:Request/aws:ListLookupRequest/aws:ProductPage',
        '//aws:Lists/aws:List/aws:TotalPages',
        '//aws:Lists/aws:List/aws:TotalItems')

class WishList (object):
    """
    Dummy class for wish list search result.
    """
    
class Item (object):
    """
    Dummy class for wish list item.
    """

def get_wishlists(**params):
    """
    Gets all wish lists matching search parameters.  
    """
    for root in lists_paginator(api.list_search, 'WishList', **params):
    
        nspace = root.nsmap.get(None, '')
        lists = root.xpath('//aws:List', namespaces={'aws' : nspace})
        
        for result in lists:
            
            list = WishList()
            list.id = result.ListId.pyval
            list.url = result.ListURL.pyval
            list.name = result.ListName.pyval
            list.type = result.ListType.pyval
            list.total_items = result.TotalItems.pyval
            list.total_pages = result.TotalPages.pyval
            list.created = result.DateCreated.pyval
            list.last_modified = result.LastModified.pyval
            list.customer = result.CustomerName.pyval
            
            yield list
            
def get_wishlist_items(list_id, **params):
    """
    Gets all items on specified wish list.
    """
    for root in items_paginator(api.list_lookup, list_id, 'WishList', 
                                ResponseGroup='ListItems', **params):
        
        nspace = root.nsmap.get(None, '')
        items = root.xpath('//aws:ListItem', namespaces={'aws' : nspace})
        
        for result in items:
            
            item = Item()
            item.id = result.ListItemId.pyval
            item.added_on = result.DateAdded.pyval
            item.number_desired = result.QuantityDesired.pyval
            item.number_received = result.QuantityReceived.pyval
            item.priority = result.Priority.pyval
            item.asin = result.Item.ASIN.pyval
            item.title = result.Item.ItemAttributes.Title.pyval
            yield item
    
if __name__ == '__main__':
    
    for list in get_wishlists(FirstName='John', LastName='Doe'):
        print list.customer
        print '%(name)r with %(total_items)i items' % list.__dict__
        print 'created: %(created)s last modified: %(last_modified)s' % list.__dict__ 
        print list.url
        print
        
        for item in get_wishlist_items(list.id):
            
            number = item.number_desired - item.number_received
            print '%3ix %s (%s)' % (number, item.title, item.asin)
            
        print
    
 