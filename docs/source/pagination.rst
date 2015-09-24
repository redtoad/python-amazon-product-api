
.. _pagination:

Result pagination
=================

.. versionadded:: 0.2.5
.. versionchanged:: 0.2.6

One of the main advantages of this wrapper is that it provides automatic pagination of results.
Rather than having to make 10 calls to get all available pages, you can simply iterate over the paginator instance that some operations return. ::

    >>> api = API(locale='de')
    >>> results = api.item_search('Books',
    ...     Publisher='Galileo Press', Sort='salesrank')
    >>> results
    <amazonproduct.processors._lxml.SearchPaginator object at 0x253af10>

The result is a :class:`~amazonproduct.processors._lxml.SearchPaginator` instance, which can be queried and iterated over ::

    >>> results.results
    286
    >>> results.pages
    29
    >>> for item in results:
    ...     print item.ASIN
    ...
    B004C04AOG
    B00K1ZG9V8
    B00SWJNV2K
    1408855658
    1408845644
    1783705485
    3551551677
    ...

New pages are loaded from Amazon (up to a maximum of 10 pages) as they are
required.

If you don't want to use pagination, you can disable this feature by passing ``paginate=False``. ::

    >>> results = api.item_search('Books',
    ...     Publisher='Galileo Press', Sort='salesrank',
    ...     ItemPage=3, paginate=False)
    >>> results
    <Element {http://webservices.amazon.com/AWSECommerceService/2013-08-01}ItemSearchResponse at 0xb5a845cc>
    >>> for item in results.Items.Item:  # now we have a normal result page!
    ...     print item.ASIN
    ...
    B00PQ63SUC
    B013STZW4S
    B00VJPQ9EG
    1783296038
    1455524182
    1608876861
    3551551936
    3551559015
    3833230347
    ...

.. note::
   Now we have a single result page

Paginator types
---------------

By default the items will be paginated over. However, there are other pagination methods available:

* :const:`~amazonproduct.processors.ITEMS_PAGINATOR` (default) - iterates over all items (default)
* :const:`~amazonproduct.processors.RELATEDITEMS_PAGINATOR` - iterates over all related items provided
* ``False`` - no pagination thank you very much

All paginator classes inherit from :class:`~amazonproduct.processors.BaseResultPaginator`:

.. autoclass:: amazonproduct.processors.BaseResultPaginator

Supported methods
-----------------

The following API methods support pagination:

* :meth:`~amazonproduct.api.API.item_lookup`
* :meth:`~amazonproduct.api.API.item_search`

