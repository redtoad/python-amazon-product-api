
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

There is a growing list of configuration options for the library, many of which
can be passed directly to the API constructor at initialisation. Some options,
such as credentials, can also be read from environment variables (e.g.
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``).

The order of precedence for is always:

* Parameters passed into Connection class constructor.
* Parameters specified by environment variables
* Parameters specified as options in the config file.

The following table gives an overview which values can be defined where:

=============  ======================  =====================
config file    boto config             environment variable
=============  ======================  =====================
access_key     aws_access_key_id       AWS_ACCESS_KEY_ID
secret_key     aws_secret_access_key   AWS_SECRET_ACCESS_KEY
associate_tag                          AWS_ASSOCIATE_TAG
locale                                 AWS_LOCALE
=============  ======================  =====================


Config files
~~~~~~~~~~~~

Upon initialisation, the API looks for configuration files (similar to the
`boto config`_, where I have borrowed the idea from) in the following
locations and in the following order:

* any `boto config`_ files ``/etc/boto.cfg`` and ``~/.boto``
* ``/etc/amazon-product-api.cfg`` for site-wide settings that all users on
  this machine will use
* ``~/.amazon-product-api`` for user-specific settings

The options are merged into a single, in-memory configuration that is available.
Files from this wrapper will always take precedence over boto config files!

The following sections and options are currently recognized within the config
file.

``Credentials``
    The Credentials section is used to specify the AWS credentials used for
    all requests.


    ``access_key``
        Your AWS access key

    ``secret_key``
        Your AWS secret access key

    ``associate_tag``
        Your AWS associate ID

    Example::

        [Credentials]
        access_key = <your access key>
        secret_key = <your secret key>
        associate_tag = <your associate id>

.. _boto config: http://code.google.com/p/boto/wiki/BotoConfig


Environment variables
~~~~~~~~~~~~~~~~~~~~~

You can also set the following environment variables:

``AWS_ACCESS_KEY_ID``
    Your AWS access key

``AWS_SECRET_ACCESS_KEY``
    Your AWS secret access key

``AWS_ASSOCIATE_TAG``
    Your AWS associate ID

``AWS_LOCALE``
    Your API locale


More information on the API
---------------------------

* Amazon Product Advertising API Best Practices: 
  http://aws.amazon.com/articles/1057