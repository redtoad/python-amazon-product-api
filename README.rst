====================================================
Python bindings for Amazon's Product Advertising API
====================================================

This module offers a light-weight access to the latest version of the Amazon
Product Advertising API without getting in your way. 

The `Amazon Product Advertising API`_ provides programmatic access to Amazon's
product selection and discovery functionality. It has search and look up
capabilities, provides information on products and other features such as
Reviews, Similar Products and New and Used listings.

.. _Amazon Product Advertising API:
   https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

Basic usage
===========

In order to use this API you'll obviously need an Amazon Associates Web Service
account for which you must with Amazon at http://aws.amazon.com. Each account
contains an *AWSAccessKeyId* and a *SecretKey*.

Create a file ``~/.amazon-product-api`` containing the following data::

    [Credentials]
    access_key = <your access key>
    secret_key = <your secret key>
    associate_tag = <your associate id>

Here is an example how to use the API to search for books of a certain
publisher::

    from amazonproduct import API
    api = API(locale='de')

    total_results = node.Items.TotalResults.pyval
    total_pages = node.Items.TotalPages.pyval

    # get all books from result set and
    # print author and title
    for book in api.item_search('Books', Publisher='Galileo Press'):
        print '%s: "%s"' % (book.ItemAttributes.Author,
                            book.ItemAttributes.Title)

In the background the API will iteratively retrieve all available result pages
from Amazon and return each book in turn as a `lxml.objectified`_ element.

In general, this module offers a number of convenience methods that will deal
with the nitty-gritty details like error checking so you won't have to. Please
refer to the extensive `documentation`_ for more details.

.. _lxml.objectified: http://codespeak.net/lxml/objectify.html
.. _documentation: http://packages.python.org/python-amazon-product-api/

Installation
============

In order to install python-amazon-product-api you can use::

    pip install python-amazon-product-api
    
or download the source package from 
http://pypi.python.org/pypi/python-amazon-product-api, untar it and run ::
    
    python setup.py install

You'll also find binaries there to make your life easier if you happen to use
a Windows system. If not, please send me an e-mail and complain loudly!

Development
===========

The development version is available `bitbucket.org`_. Feel free to clone the 
repository and add your own features. ::
    
    hg clone http://bitbucket.org/basti/python-amazon-product-api/
    
Patches are always welcome! Please make sure that your change does not break 
the tests!

.. _bitbucket.org: http://bitbucket.org/basti/python-amazon-product-api/

License
=======

This module is release under the BSD License. You can find the full text of
the license in the LICENSE file.

