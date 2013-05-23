.. _error-handling:

Error handling
==============

The most basic error is ``AWSError``, which has attributes ``code`` and 
``message``. Almost all operations raise specialised exceptions. 

.. autoexception:: amazonproduct.errors.AWSError

Sometimes you may still want to access the original response. An example::

    try:
        result = api.item_lookup(
            ['644209004461', '009800895250', '301357583001'], IdType='UPC')
    except InvalidParameterValue, e:
        print 'There was an invalid ItemId!' # '301357583001'
        result = e.xml

Although UPC ``301357583001`` will cause an error to be raised, you can
retrieve the parsed response (here ``result`` is simply replaced with
``e.xml``) and continue working on it as if nothing has happened.


Occurring exceptions
--------------------

.. autoexception:: amazonproduct.errors.CartInfoMismatch
.. autoexception:: amazonproduct.errors.DeprecatedOperation
.. autoexception:: amazonproduct.errors.InternalError
.. autoexception:: amazonproduct.errors.InvalidCartId
.. autoexception:: amazonproduct.errors.InvalidCartItem
.. autoexception:: amazonproduct.errors.InvalidClientTokenId
.. autoexception:: amazonproduct.errors.InvalidListType
.. autoexception:: amazonproduct.errors.InvalidOperation
.. autoexception:: amazonproduct.errors.InvalidParameterCombination
.. autoexception:: amazonproduct.errors.InvalidParameterValue
.. autoexception:: amazonproduct.errors.InvalidResponseGroup
.. autoexception:: amazonproduct.errors.InvalidSearchIndex
.. autoexception:: amazonproduct.errors.ItemAlreadyInCart
.. autoexception:: amazonproduct.errors.MissingClientTokenId
.. autoexception:: amazonproduct.errors.MissingParameters
.. autoexception:: amazonproduct.errors.NoExactMatchesFound
.. autoexception:: amazonproduct.errors.NoSimilarityForASIN
.. autoexception:: amazonproduct.errors.NotEnoughParameters
.. autoexception:: amazonproduct.errors.TooManyRequests
.. autoexception:: amazonproduct.errors.UnknownLocale
