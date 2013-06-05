
.. _pagination:

Result pagination
=================

.. versionadded:: 0.2.5
.. versionchanged:: 0.2.6

One of the main advantages of this wrapper is that it provides automatic pagination of results.
Rather than having to make 10 calls to get all available pages, you can simply iterate over the paginator instance that some operations return.

Example::

    >>> api = API(locale='de')
    >>> results = api.item_search('Books',
    ...     Publisher='Galileo Press', Sort='salesrank')
    >>> results
    <amazonproduct.processors._lxml.SearchPaginator object at 0x253af10>

The result is a :class:`~amazonproduct.processors._lxml.SearchPaginator`
instance, which can be queried

    >>> results.results
    286
    >>> results.pages
    29

and iterated over ::

    >>> for item in results:
    ...     print repr(item)
    ...
    <Element {http://webservices.amazon.com/AWSECommerceService/2011-08-01}Item at 0x25441e0>
    <Element {http://webservices.amazon.com/AWSECommerceService/2011-08-01}Item at 0x25442d0>
    <Element {http://webservices.amazon.com/AWSECommerceService/2011-08-01}Item at 0x2544550>
    <Element {http://webservices.amazon.com/AWSECommerceService/2011-08-01}Item at 0x2544500>
    ...

New pages are loaded from Amazon (up to a maximum of 10 pages) as they are
required.

.. autoclass:: amazonproduct.processors.BaseResultPaginator
