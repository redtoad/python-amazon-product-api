
Basic usage
===========

In order to use this API you'll obviously need an Amazon Associates Web Service
account for which you must `register with Amazon`_. Each account contains an
*AWSAccessKeyId* and a *SecretKey*. 

.. _register with Amazon: https://affiliate-program.amazon.com/gp/advertising/api/detail/your-account.html

Here is an example how to use the API to search for books of a certain 
publisher::

    AWS_KEY = '...'
    SECRET_KEY = '...'
    
    api = API(AWS_KEY, SECRET_KEY, 'us')
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

All anticipated errors are caught and raised with meaningful error
messages. ::

    try:
        node = api.similarity_lookup('0451462009', '0718155157')
        # ...
    except NoSimilarityForASIN, e:
        print 'There is no book similar to %s!' % e.args[0]

The most basic error is ``AWSError``, which has attributes ``code`` and 
``message``. Almost all operations raise specialies exceptions. Below is a 
short list:

- ``InvalidSearchIndex``
- ``InvalidResponseGroup``
- ``InvalidParameterValue``
- ``InvalidListType``
- ``NoSimilarityForASIN``
- ``NoExactMatchesFound``
- ``TooManyRequests``
- ``NotEnoughParameters``
- ``InvalidParameterCombination``
