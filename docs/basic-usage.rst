
Basic usage
===========

In order to use this API you'll obviously need an Amazon Associates Web Service
account for which you must with Amazon at http://aws.amazon.com. Each account
contains an *AWSAccessKeyId* and a *SecretKey*. 

Here is an example how to use the API to search for books of a certain 
publisher::

    AWS_KEY = '...'
    SECRET_KEY = '...'
    
    api = API(AWS_KEY, SECRET_KEY)
    node = api.item_search('Books', Publisher='Galileo Press')

The ``node`` object returned is a `lxml.objectified`__ element. All its 
attributes can be accessed the pythonic way::
    
    # .pyval will convert the node content into int here
    total_results = node.Items.TotalResults.pyval
    total_pages = node.Items.TotalPages.pyval
    
    # get all books from result set and 
    # print author and title
    for book in node.Items.Item:
        print '%s: "%s"' % (book.ItemAttributes.Author, 
                            book.ItemAttributes.Title)

Please refer to the `lxml.objectify`_ documentation for more details.

.. _lxml.objectify: http://codespeak.net/lxml/objectify.html
__ lxml.objectify_

Error handling
--------------

In general, all anticipated errors are caught and raised with meaningful error
messages. ::

    try:
        api.similarity_lookup('0451462009', '0718155157')
    except NoSimilarityForASIN, e:
        print 'There is no book similar to %s!' % e.args[0]

However, if something should slip through here is another quote from
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

