
from config import AWS_KEY, SECRET_KEY
from amazonproduct.api import API
from amazonproduct.errors import AWSError

class ExceededMaxBatchRequestsPerOperation (Exception): 
    """
    You have exceeded the maximum number of batch requests per operation.  Each
    operation may include no more than 2 batch requests.
    """

class BatchModeAPI(API):

    """
    Custom API supporting Batch Requests
    
    http://docs.amazonwebservices.com/AWSECommerceService/2010-11-01/DG/index.html?BatchRequests.html
    """

    def __init__(self, *args, **kwargs):
        API.__init__(self, *args, **kwargs)
        self.batch_mode = False

    def call(self, **qargs):
        # if in batch mode collect all operations but do nothing else
        # TODO: Maybe use co-routines?
        if self.batch_mode:
            operation = qargs['Operation']
            del qargs['Operation']
            self._operations[operation] += [qargs]
            return
        
        # standard behaviour
        url = self._build_url(**qargs)
        fp = self._fetch(url)
        return self._parse(fp)

    def start_batch_request(self):
        """
        Starts collecting operations.
        """
        self.batch_mode = True
        from collections import defaultdict
        self._operations = defaultdict(list)

    def collect_batch_results(self):
        """
        Combines collected operations and returns parsed response.
        """
        arguments = {'Operation' : ','.join(self._operations.keys())}
        for key, operations in self._operations.items():
            for no, args in enumerate(operations):
                for arg, val in args.items():
                    arguments['%s.%i.%s' % (key, no+1, arg)] = val

        self.batch_mode = False
        del self._operations

        try:
            url = api._build_url(**arguments)
            fp = self._fetch(url)
            return self._parse(fp)
        except AWSError, e:
            if e.code == 'AWS.ExceededMaxBatchRequestsPerOperation':
                raise ExceededMaxBatchRequestsPerOperation
            # otherwise re-raise
            raise

if __name__ == '__main__':

    api = BatchModeAPI(AWS_KEY, SECRET_KEY, 'us')

    # batch operation: up to 2 operations with one request
    api.start_batch_request()
    api.item_lookup('0201896834') # The Art of Computer Programming Vol. 1
    api.item_lookup('0201896842') # The Art of Computer Programming Vol. 2
    # A third opration of the same type would raise an exception 
    #api.item_lookup('0201896842')
    root = api.collect_batch_results()

    from lxml.etree import tostring
    print tostring(root, pretty_print=True)

