
======================================================
Python Bindings for the Amazon Product Advertising API
======================================================

.. image:: static/banner.png
    :width: 633
    :height: 122

Amazon's Product Advertising API provides...

    [...] programmatic access to Amazon's product selection and discovery
    functionality so that developers like you can advertise Amazon products to
    monetize your website.
    
    The Product Advertising API helps you advertise Amazon products using
    product search and look up capability, product information and features
    such as Customer Reviews, Similar Products, Wish Lists and New and Used
    listings. You can make money using the Product Advertising API to advertise
    Amazon products in conjunction with the Amazon Associates program. Be sure
    to join the Amazon Associates program to earn up to 15% in referral fees
    when the users you refer to Amazon sites buy qualifying products. [#amazon]_ 

.. [#amazon] https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

Features
--------

This module offers a light-weight access to the latest version of the Amazon 
Product Advertising API without getting in your way. All requests are signed
as required since August 15, 2009.

.. 
   By default the XML response is returned as a object parsed by `lxml.objectify`_. 
   However, you can substitute this with your own parsing method if you so wish.

Status
------

This module is still undergoing development. The support for the Amazon Product
API is currently limited to a number of operations. More functionality is to 
follow as development progresses. 

Supported so far are:
   
- ItemLookup
- ItemSearch
- SimilarityLookup

Installation
------------

The easiest way to get the python bindings is if you have setuptools_ 
installed. ::

    easy_install python-amazon-product-api
    
Without setuptools, it's still pretty easy. Download the .tgz file from 
`Cheeseshop`_, untar it and run::
    
    python setup.py install

You'll also find binaries there to make your life easier if you happen to use
a Windows system.

.. _Cheeseshop: http://pypi.python.org/pypi/python-amazon-product-advertising-api/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

License
-------

.. include:: ../LICENSE

Development
-----------

Development happens over at `bitbucket.org`_. Feel free to clone the repository
and add your own features.  If you like what you see, drop me a line at 
`basti at redtoad dot de`.

.. _bitbucket.org: http://bitbucket.org/basti/python-amazon-product-api/ 

Contents
--------

.. toctree::
   :maxdepth: 2
   
   why
   basic-usage
   pagination
   operations
   
   changes
	
Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

