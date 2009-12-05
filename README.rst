====================================================
Python bindings for Amazon's Product Advertising API
====================================================

The Product Advertising API provides programmatic access to Amazon's
product selection and discovery functionality so that developers like you
can advertise Amazon products to monetize your website.

The Product Advertising API helps you advertise Amazon products using
product search and look up capability, product information and features
such as Customer Reviews, Similar Products, Wish Lists and New and Used
listings. You can make money using the Product Advertising API to advertise
Amazon products in conjunction with the Amazon Associates program. Be sure
to join the Amazon Associates program to earn up to 15% in referral fees
when the users you refer to Amazon sites buy qualifying products.  

More info can be found at
https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

Features
--------

This module offers a light-weight access to the latest version of the Amazon 
Product Advertising API without getting in your way. All requests are signed
as required since August 15, 2009.

Installation
------------

In order to install python-amazon-product-api you can use::

    easy_install python-amazon-product-api
    
or download the source package from 
http://pypi.python.org/pypi/python-amazon-product-api, untar it and run ::
    
    python setup.py install

You'll also find binaries there to make your life easier if you happen to use
a Windows system.

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

Status
------

This module is still undergoing development. The support for the Amazon Product
API is currently limited to a number of operations. More functionality is to 
follow as development progresses. 

Supported so far are:
   
- ItemLookup
- ItemSearch
- SimilarityLookup

Development
-----------

Development happens over at `bitbucket.org`_. Feel free to clone the repository
and add your own features.  If you like what you see, drop me a line at 
`basti at redtoad dot de`.

.. _bitbucket.org: http://bitbucket.org/basti/python-amazon-product-api/ 