
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

Status
------

This module is still undergoing development. The support for the Amazon Product
API is currently limited to a number of operations. More functionality is to 
follow as development progresses. 

Supported so far are:
   
- ItemLookup
- ItemSearch
- SimilarityLookup
    

Features
--------

...

Installation
------------

The easiest way to get the python bindings is if you have setuptools_ 
installed.

``easy_install python-product-advertising-api``

Without setuptools, it's still pretty easy. Download the .tgz file from 
`Cheeseshop`_, untar it and run:

``python setup.py install``

.. _Cheeseshop: http://pypi.python.org/pypi/python-amazon-product-advertising-api/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

License
-------

This module is licensed under a BSD license. See the `LICENSE` file in the 
distribution.

Contents
--------

.. toctree::
   :maxdepth: 2
   
   why
   basic-usage
   pagination
   operations
	
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

