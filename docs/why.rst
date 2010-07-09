Why yet another implementation?
===============================

.. index:: pyaws, pyamazon, boto, pyecs, bottlenose

There are a number of alternatives available:

- `PyAmazon <http://www.josephson.org/projects/pyamazon/>`_, originally written
  by Mark Pilgrim, then taken over by Michael Josephson. Development seems to
  have stalled, with the last release in August 2004.
  
- Kung Xi's `pyaws <http://pyaws.sf.net>`_ forked pyamazon to support the then
  most recent Amazon Web Service and give developers more control of the 
  incoming data. Sometime after version 0.2.0, development over at sourceforge
  was dropped without warning and continued at http://trac2.assembla.com/pyaws
  with version 0.3.0, which was released in May 2008.
   
  This module seems to be the most widely used. It hasn't been updated however
  in quite some time. A fork of this project is maintained 
  `here <http://bitbucket.org/johnpaulett/pyaws>`_.

- In October 2008 David Jane started `pyecs <http://code.google.com/p/pyecs/>`_
  after stumbling accross pyamazon. He decided that "a new, more class and
  iterator-oriented approach would be better." However, it only supports a
  subset. Last commit was in November 2008. 
  
- There is a `clever hack <http://jjinux.blogspot.com/2009/06/python-amazon-product-advertising-api.html>`_
  using `boto <http://code.google.com/p/boto/>`_ to create the URL, although
  this library is originally designed to allow communication with Amazon's 
  cloud APIs.

So why write your own then? First and foremost, since August 15, 2009 all calls
to Amazon's Product Advertising API must be authenticated using request 
signatures. The afore mentioned libraries did not support this out of the box at
the time. And yes... writing something from scratch is always more appealing.

More recently I stumbled across another alternative:

- Dan Loewenherz's `bottlenose <http://pypi.python.org/pypi/bottlenose>`_ makes 
  sending requests to Amazon as easy as ::
    
    import bottlenose
    amazon = bottlenose.Amazon("access_key_id", "secret_access_key")
    response = amazon.ItemSearch(ItemId="0596520999", ResponseGroup="Images", 
        SearchIndex="Books", IdType="ISBN")
    
  It has a straight-forward API, is easy to use and supports all operations out
  of the box. You only have to take care of processing the response. I must 
  steal some ideas from this module! 