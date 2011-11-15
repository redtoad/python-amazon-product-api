
Operations
==========

Lookup and search operations
----------------------------

.. automethod:: amazonproduct.api.API.item_search(searchindex)
.. automethod:: amazonproduct.api.API.item_lookup
.. automethod:: amazonproduct.api.API.similarity_lookup

.. automethod:: amazonproduct.api.API.browse_node_lookup

Cart operations
---------------

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
