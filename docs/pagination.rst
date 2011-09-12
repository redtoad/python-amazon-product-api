
.. _pagination:

Pagination
----------

.. index:: pagination
   single: results; pagination

.. attention:: The ``ResultPaginator`` only works with ``lxml``!

The Amazon Product Advertising API paginates some its results. In order to get
all reviews of a product, for instance, subsequent calls have to be made to the
API.  Let's have a look at an example:

We want to fetch all reviews for "Learning Python" (ASIN 0596513984).

You can, of course, do everthing by hand. For this an initial ::

    api.item_lookup('0596513984', SearchIndex='Books', ResponseGroup='Reviews')
    
is required to find out over just how many result pages the reviews stretch
(stored in the ``<TotalReviewPages>``) and then call to retrieve each and every
one of them individually (with an additional ``ReviewPage`` parameter).

However, rather than writing a looping mechanism yourself, this module provides
a handy generator method that can be iterated over. All you have to do is to
define the location of the necessary pagination information using XPath
expressions::

    paginator = ResultPaginator('ReviewPage',
        '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
        '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
        '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')

All that's left is to pass the use method as before and iterate over the 
result:: 

    for node in paginator(api.item_lookup, '0596513984', 
            SearchIndex='Books', ResponseGroup='Reviews'):
        
        # ...
        
And that's it!
