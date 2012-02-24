
.. _getting-started:

Getting started
===============

In order to use this API you'll obviously need an Amazon Associates Web Service
account for which you must `register with Amazon`_. Each account contains an
*AWSAccessKeyId* and a *SecretKey*. As of API version 2011-08-01 you will also
need to `register for an AssociateTag`_.

.. note:: It is assumed that you know what the Amazon Product Advertising API
   does. If you are unsure, read their `developer guide`_ (particularly the
   section *Introduction to the Product Advertising API*.  

.. _developer guide: http://docs.amazonwebservices.com/AWSECommerceService/
    2011-08-01/DG/Welcome.html?r=4324

Basic setup
-----------

If you haven't done so already, create a file ``~/.amazon-product-api``
(``C:\Users\You\.amazon-product-api`` if you're on Windows) and paste the
following content into it::

    [Credentials]
    access_key = <your access key>
    secret_key = <your secret key>
    associate_tag = <your associate id>

Of course, you'll need to fill in the appropriate values! More information on
how to configure the module can be found :ref:`later on <config>`.

.. _register with Amazon: https://affiliate-program.amazon.com/gp/advertising/
    api/detail/your-account.html
.. _register for an AssociateTag: https://affiliate-program.amazon.com/


Your first API request
----------------------

Here is an example how to use the API to search for books of a certain 
publisher.  ::

    api = API(locale='us')
    items = api.item_search('Books', Publisher="O'Reilly")

So what happens here? First you initialised your API wrapper to use Amazon.com.
There are, of course, `other locales available`_ should you wish to use a
different one. For instance, ``locale='de'`` will cause requests to be sent to
Amazon.de (Germany).

Afterwards you called the API operation *ItemSearch* to get a list of all books
that where published by O'Reilly. Now method ``item_search`` does several
things at once for you: 

1. It turns all your parameters into a validly signed URL and sends a request.
2. The returned XML document is parsed and if it contains any error message,
   the appropriate Python exception is raised (see :ref:`dealing-with-errors`). 
3. Amazon itself provides their results spread over several pages. If you were
   to do this manually you would have to make several calls. To make things
   easier for you :meth:`item_search` will iterate over all availabe results
   (see :ref:`pagination` for more information).

.. _other locales available: http://docs.amazonwebservices.com/
    AWSECommerceService/latest/DG/CHAP_LocaleConsiderations.html

You can now iterate over the ``items`` and will get a number of parsed XML
nodes (by default and if available `lxml.objectify`_ is used). With it you can
access all elements and attributes in a Pythonic way::
    
    # get all books from result set and 
    # print author and title
    for book in items:
        print '%s: "%s"' % (book.ItemAttributes.Author, 
                            book.ItemAttributes.Title)

Please refer to the `lxml.objectify`_ documentation for more details. If you
cannot/will not use lxml, see :ref:`pagination` for alternatives.

You can find more API operations later in :ref:`operations`.

.. _lxml.objectify: http://codespeak.net/lxml/objectify.html


.. _dealing-with-errors:

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

