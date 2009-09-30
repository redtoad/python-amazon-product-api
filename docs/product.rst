==============================
Amazon Product Advertising API
==============================

The `Product Advertising API`_ provides...

    [...] programmatic access to Amazon's product selection and discovery
    functionality so that developers like you can advertise Amazon products to
    monetize your website.
    
    The Product Advertising API helps you advertise Amazon products using
    product search and look up capability, product information and features
    such as Customer Reviews, Similar Products, Wish Lists and New and Used
    listings. You can make money using the Product Advertising API to advertise
    Amazon products in conjunction with the Amazon Associates program. Be sure
    to join the Amazon Associates program to earn up to 15% in referral fees
    when the users you refer to Amazon sites buy qualifying products.  

.. _Product Advertising API: 
   https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

.. note:: The support for this API is currently limited to *ItemLookup* and
   *ItemSearch*. More functionality is to follow as development progresses.

Motivation
----------

Since August 15, 2009 all calls to the Product Advertising API must be
authenticated using request signatures. All existing libraries did not support
this at the time. Plus I felt that they were very cumbersome to work with (if
that is indeed a word).

Basic usage
-----------

In order to use this API you'll obviously need an Amazon Associates Web Service
account for which you must with Amazon at http://aws.amazon.com. Each account
contains an *AWSAccessKeyId* and a *SecretKey*. 

The API itself can used like this::

    AWS_KEY = '...'
    SECRET_KEY = '...'
    
    api = API(AWS_KEY, SECRET_KEY)
    node = api.item_search('Books', Publisher='Galileo Press')

The ``node`` object returned is a `lxml.objectified`__ element. All its content
can be accessed using the lxml.objectify API::
    
    # .pyval will convert the node content into int here
    total_results = root.Items.TotalResults.pyval
    total_pages = root.Items.TotalPages.pyval
    
    # get all books from result set and 
    # print author and title
    for book in node.Items.Item:
        print '%s: "%s"' % (book.ItemAttributes.Author, 
                            book.ItemAttributes.Title)

Please refer to the `lxml.objectify`_ documentation for more examples.

.. _lxml.objectify: http://codespeak.net/lxml/objectify.html
__ lxml.objectify_


Error handling
--------------

In general, all anticipated errors are caught and raised with meaningful error
messages. However, if something should slip through here is another quote from
the `Amazon Associates Web Service Best Practices`_:

  Amazon Associates Web Service returns errors in three categories so that you
  can easily determine how best to handle the problem:
  
  * 2XX errors are caused by mistakes in the request. For example, your request
    might be missing a required parameter. The error message in the response
    gives a clear indication what is wrong.
  * 4XX errors are non-transient errors. Upon receiving this error, resubmit
    the request.
  * 5XX errors are transient errors reflecting an error internal to Amazon. A
    503 error means that you are submitting requests too quickly and your
    requests are being throttled. If this is the case, you need to slow your
    request rate to one request per second.

.. _Amazon Associates Web Service Best Practices:
   http://developer.amazonwebservices.com/connect/entry.jspa?externalID=1057

