
Basic usage
===========

In order to use this API you'll obviously need an Amazon Associates Web Service
account for which you must `register with Amazon`_. Each account contains an
*AWSAccessKeyId* and a *SecretKey*. As of API version 2011-08-01 you will also
need to `register for an AssociateTag`_.

.. _register with Amazon: https://affiliate-program.amazon.com/gp/advertising/api/detail/your-account.html
.. _register for an AssociateTag: https://affiliate-program.amazon.com/

Here is an example how to use the API to search for books of a certain 
publisher. Of course, you'll need to replace ``AWS_KEY``, ``SECRET_KEY`` and
``ASSOCIATE_TAG`` with the appropriate values! ::

    AWS_KEY = '...'
    SECRET_KEY = '...'
    ASSOCIATE_TAG = 'mytag-12'
    
    api = API(AWS_KEY, SECRET_KEY, 'us', ASSOCIATE_TAG)
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


Dealing with errors
-------------------

One of the advatages of using this wrapper is that all error messages from 
Amazon will raise Python exceptions with meaningful messages. ::

    try:
        node = api.similarity_lookup('0451462009', '0718155157')
        # ...
    except NoSimilarityForASIN, e:
        print 'There is no book similar to %s!' % e.args[0]
    except AWSError, e:
        print 'Amazon complained about yout request!'
        print e.code
        print e.msg

A list of exceptions can be found in :ref:`error-handling`.


.. _config:

Configuration
-------------

.. versionadded:: 0.2.6


More information on the API
---------------------------

* Amazon Product Advertising API Best Practices: 
  http://aws.amazon.com/articles/1057