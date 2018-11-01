

class Operation(object):

    """
    An operation holds all parameters required for an API request.

    >>> lookup = Operation('ItemLookup', ItemId='0976925524', IdType='ASIN')
    >>> lookup.parameters
    {'ItemId': '0976925524', 'IdType': 'ASIN'}

    Operations can be combined to form a single `batch requests`_:

    >>> batch = lookup + Operation('ItemLookup', ItemId='80348287843', IdType='ASIN')
    >>> batch.parameters
    {'ItemLookup.1.ItemId': '0976925524', 'ItemLookup.2.ItemId': '80348287843', 'ItemLookup.Shared.IdType': 'ASIN'}

    .. _batch requests: https://docs.aws.amazon.com/AWSECommerceService/latest/DG/BatchandMultipleOperationRequests.html
    """

    def __init__(self, name, **params):
        self.name = name
        self._params = [params]

    @property
    def parameters(self):
        if len(self._params) == 1:
            return self._params[0]
        keys = {key for pset in self._params for key in pset.keys()}
        args = {}
        while keys:
            key = keys.pop()
            values = [pset[key] for pset in self._params if key in pset]
            if len(values) == len(self._params) and len(set(values)) == 1:
                args["%s.Shared.%s" % (self.name, key)] = values[0]
            else:
                for no, pset in enumerate(self._params, start=1):
                    if key in pset:
                        args["%s.%i.%s" % (self.name, no, key)] = pset[key]
        return args

    def __add__(self, other):
        # https://docs.aws.amazon.com/AWSECommerceService/latest/DG/BatchandMultipleOperationRequests.html
        if self.name != other.name:
            raise ValueError("Only operations of same type can be combined!")
        if "Cart" in self.name or "Cart" in other.name:
            raise ValueError("Cart operations cannot be combined!")
        self._params += other._params
        return self


