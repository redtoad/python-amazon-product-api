
.. _operations:

Operations
==========

All functionality of the Amazon Product Advertising API is provided by
*operations* each of which will accept a number of different parameters both
required and optional. A special signed URL has to be constructed from which the
result of an operation can be retrieved as a XML document.

Building the individual URL can be quite cumbersome when done repeatedly by
hand. That's the main reason why this module came into being. Any operation
listed in the `API documentation`_ can thus be called with :meth:`~API.call()`.
To look up information on an article, one could for instance call ItemLookup_
in the following way::

    api.call(Operation='ItemLookup', ItemId='B00008OE6I')
    
However, this module offers a few *convenience methods* which can make your life
easier by producing clearer error messages or even :ref:`paginating
<pagination>` over the returned results. For the above call you would simply use
:meth:`~amazonproduct.api.API.item_lookup`.

Below is a list of all the operations which are specifically supported in this
module.

.. _API documentation: http://docs.amazonwebservices.com/AWSECommerceService/
        latest/DG/CHAP_OperationListAlphabetical.html
.. _ItemLookup: http://docs.amazonwebservices.com/AWSECommerceService/latest/
        DG/ItemLookup.html


Lookup and search operations
----------------------------

These operations are the heart and soul of the API. With these you can search
for products and retreive their data.

.. automethod:: amazonproduct.api.API.item_search(searchindex, **query)
.. automethod:: amazonproduct.api.API.item_lookup(id [, id2, ...], **extra)
.. automethod:: amazonproduct.api.API.similarity_lookup(id [, id2, ...], **extra)

Amazon als structures their products in categories, so called *BrowseNodes*,
each with its unique ID. You can find a list of these nodes here_.

.. _here: http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/
        index.html?BrowseNodeIDs.html>`_.

.. automethod:: amazonproduct.api.API.browse_node_lookup


Cart operations
---------------

Since the Amazon Product Advertising API is all about generating revenue for
Amazon, of course, there is also the possibility to create remote shopping
baskets. The operations below are staight-forward and need little explanation.
You may, however, have a look at the :mod:`amazonproduct.contrib.cart` module
which provides a generic :class:`~amazonproduct.contrib.cart.Cart` class to deal
with the responses from these operations.

.. automethod:: amazonproduct.api.API.cart_create
.. automethod:: amazonproduct.api.API.cart_get
.. automethod:: amazonproduct.api.API.cart_add
.. automethod:: amazonproduct.api.API.cart_modify
.. automethod:: amazonproduct.api.API.cart_clear


.. _common-request-parameters:

Common request parameters
-------------------------

There are a number of *optional* keyword parameters which you can use to any of
the afore mentioned operations.

``ContentType``
    Specifies the format of the content in the response. Generally,
    ``ContentType``  should only be changed for REST requests when the
    ``Style`` parameter is set to an XSLT stylesheet. For example, to transform
    your Product Advertising API response into HTML, set ``ContentType`` to
    ``text/html``. See ``Style``.

    Valid Value: ``text/xml`` (default), ``text/html``

``MarketplaceDomain``
    Specifies the Marketplace Domain where the request will be directed. For
    more information, see
    http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/index.html?MarketplaceDomainParameter.html.

``MerchantId``
    An optional parameter that can be used to filter search results and offer
    listings to only include items sold by Amazon. By default, the API will
    return items sold by various merchants including Amazon.

``Style``
    Controls the format of the data returned in Product Advertising API
    responses. ``Style`` only pertains to REST requests. Set this parameter to
    ``XML`` (default), to generate a pure XML response. Set this parameter to
    the URL of an XSLT stylesheet to have Product Advertising API transform the
    XML response. See ``ContentType``.

    Valid Values: URL of an XSLT stylesheet

``Validate``
    Prevents an operation from executing. Set the ``Validate`` parameter to
    ``True`` to test your request without actually executing it. When present,
    ``Validate`` must equal ``True``; the default value is ``False``. If a
    request is not actually executed (``Validate=True``), only a subset of the
    errors for a request may be returned because some errors (for example,
    :exc:`NoExactMatchesFound`) are only generated during the execution of a
    request.

    Valid Values: ``True``, ``False`` (default)

``Version``
    The version of the Product Advertising API software and WSDL to use. By
    default, the ``2005-10-05`` version is used. Alternately, specify a
    software version, such as ``2011-08-01``. For a list of valid version
    numbers, refer to the Product Advertising API `Release Notes`_. Note that
    the latest version of Product Advertising API is not used by default.

    Valid Values: Valid WSDL version date, for example, ``2011-08-01``.
    Default: ``2005-10-05``

    .. note:: If you want to adjust your ``Version`` more easily, have a look
       at :ref:`adjusting-api-version`.

``XMLEscaping``
    Specifies whether responses are XML-encoded in a single pass or a double
    pass. By default, ``XMLEscaping`` is ``Single``, and Product Advertising
    API responses are encoded only once in XML. For example, if the response
    data includes an ampersand character (&), the character is returned in its
    regular XML encoding (&). If ``XMLEscaping`` is ``Double``, the same
    ampersand character is XML-encoded twice (&amp;). The ``Double`` value for
    ``XMLEscaping`` is useful in some clients, such as PHP, that do not decode
    text within XML elements.

    Valid Values: ``Single`` (default), ``Double``

Please refer to
http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/index.html?CommonRequestParameters.html
for an up-to-date list of parameters.


.. _Release Notes: http://aws.amazon.com/releasenotes
