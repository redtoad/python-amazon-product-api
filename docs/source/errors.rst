.. _error-handling:

Error handling
==============

The most basic error is ``AWSError``, which has attributes ``code`` and 
``message``. Almost all operations raise specialised exceptions. 

.. autoexception:: amazonproduct.errors.AWSError

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
