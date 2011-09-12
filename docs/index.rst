=========================
python-amazon-product-api
=========================

This module offers a light-weight access to the latest version of the Amazon
Product Advertising API without getting in your way. No more worrying about
signing your URL, parsing your output and having to deciver possible error
messages!

To quote Amazon: "Amazon's Product Advertising API provides programmatic access
to Amazon's product selection and discovery functionality. It has search and
look up capabilities, provides information on products and other features such
as Similar Products, and New and Used listings." 

More information about the API can be found at
https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html


For the impatient
-----------------

Here is a quick example of how to get all books from Galileo Press (my current
employer)::

    from amazonproduct import API

    # your credentials from Amazon
    AWS_KEY  = '...'
    SECRET_KEY = '...'

    # we'll query Amazon Germany, hence 'de' 
    api = API(AWS_KEY, SECRET_KEY, 'de')

    # results are paginated and we are looking for all books
    # (SearchIndex='Books') from publisher 'Galileo Press'
    for page in api.item_search('Books', Publisher='Galileo Press'):

        # each page is an XML document, which (by default) has already been
        # parsed by lxml.objectify
        for itemnode in page.Items.Item:
            print itemnode.ASIN, itemnode.ItemAttributes.Title

Bear in mind that this module does not provide any additional logic but will
simply make calling the API a more pleasant experience.

If you want to know more, have a look at the `examples directory`_ or read on
to learn about the available `operations`_, `dealing with errors`_ or `using
your own XML parser`_.


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

The easiest way to get the python bindings is to use `pip`_::

    pip install python-amazon-product-api
    
Without setuptools, it's still pretty easy. Download the .tgz file from 
`Cheeseshop`_, untar it and run::
    
    python setup.py install

You'll also find binaries there to make your life easier if you happen to use
a Windows system.

The development version is available `bitbucket.org`_. Feel free to clone the 
repository and add your own features. ::
    
    hg clone http://bitbucket.org/basti/python-amazon-product-api/
    
If you like what you see, drop me a line at `basti at redtoad dot de`.

.. _pip: http://pip.openplans.org/
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

