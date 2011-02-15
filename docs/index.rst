
Amazon's Product Advertising API provides programmatic access to Amazon's
product selection and discovery functionality. it has search and look up 
capabilities, provides information on products and other features such as 
Customer Reviews, Similar Products, Wish Lists and New and Used listings. 

This module offers a light-weight access to the latest version of the Amazon 
Product Advertising API without getting in your way. All requests are signed
as required since August 15, 2009.

More information about the API can be found at
https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

Status
------

This module is still undergoing development. The support for the Amazon Product
API is currently limited to a number of operations:
   
- ``ItemLookup``
- ``ItemSearch``
- ``SimilarityLookup``
- ``ListLookup``
- ``ListSearch``
- ``Help``
- ``BrowseNodeLookup``

More functionality is to follow as development progresses. 

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

The development version is available `bitbucket.org`_. Feel free to clone the 
repository and add your own features. ::
    
    hg clone http://bitbucket.org/basti/python-amazon-product-api/
    
If you like what you see, drop me a line at `basti at redtoad dot de`.

.. _Cheeseshop: http://pypi.python.org/pypi/python-amazon-product-api/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _bitbucket.org: http://bitbucket.org/basti/python-amazon-product-api/

Contents
--------

.. toctree::
   :maxdepth: 2
   
   why
   basic-usage
   operations
   pagination
   use-your-own
   
   faq
   
   changes
   license
   
Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

