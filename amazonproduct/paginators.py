
class BaseResultPaginator (object):

    """
    Wrapper class for paginated results. This class will call the passed
    function iteratively until either the specified limit is reached or all
    result pages are fetched.

    Although probably only useful in theory, it can be used by itself to 
    manually iterate over paginated results. A small example fetching reviews
    for a book::

        api = API(AWS_KEY, SECRET_KEY)
        class ReviewPaginator (BaseResultPaginator):
            # specify attributes counter and limit, as well as and method
            # extract_data
            # ...

        paginator = ReviewPaginator()
        for root in paginator(api.item_lookup, id=isbn, IdType='ISBN',
                    SearchIndex='Books', ResponseGroup='Reviews', limit=10):
            print root.Review.AttributeOfInterest

    """

    def __init__(self, fun, args, kwargs, counter):
        """
        :param counter: counter variable passed to AWS.
        :param limit: limit fetched pages to this amount (restricted to a 
        maximum of 400 pages by API itself).
        """
        self.fun = fun
        self.args, self.kwargs = args, kwargs
        self.counter = counter
        self.limit = kwargs.get('limit', 400)

        # fetch first page to get pagination parameters
        self._first_page = self.page(1)

    def __iter__(self):
        """
        Iterate over all paginated results of ``fun``.
        """
        # return cached first page
        yield self._first_page
        while self.current < self.pages and self.current < self.limit:
            yield self.page(self.current + 1) 

    def page(self, index):
        """
        Fetch single page from results.
        """
        self.kwargs[self.counter] = index
        root = self.fun(*self.args, **self.kwargs)
        self.current, self.pages, self.results = self.extract_data(root)
        return root
        
    def extract_data(self, node):
        """
        Extracts pagination data from XML node.
        """
        raise NotImplementedError


def paginate(fnc):
    """
    Paginates over result pages by iteratively calling decorated method with
    corresponding paginator from response processor.
    """
    def wrapped(api, *args, **kwargs):
        processor = api.response_processor
        try:
            # try to return the OPERATION_paginator from API instance
            klass = getattr(processor, '%s_paginator' % fnc.__name__)
            method = lambda *a, **b: fnc(api, *a, **b)
            return klass(method, *args, **kwargs)
        except AttributeError:
            return fnc(api, *args, **kwargs)
    return wrapped


class LxmlPaginator (BaseResultPaginator):


    """
    Result paginator using lxml and XPath expressions to extract page and
    result information from XML.
    """

    counter = None
    current_page_xpath = None
    total_pages_xpath = None
    total_results_xpath = None

    def __init__(self, fun, *args, **kwargs):
        super(LxmlPaginator, self).__init__(fun, args, kwargs, self.counter)

    def extract_data(self, root):
        nspace = root.nsmap.get(None, '')
        values = []
        def fetch_value(xpath, default):
            try:
                node = root.xpath(xpath, namespaces={'aws' : nspace})[0]
                return node.pyval
            except AttributeError:
                # node has no attribute pyval so it better be a number
                return int(node)
            except IndexError:
                return default
        return map(lambda a: fetch_value(*a), [
            (self.current_page_xpath, 1),
            (self.total_pages_xpath, 0),
            (self.total_results_xpath, 0)
        ])


class LxmlItemSearchPaginator (LxmlPaginator):

    counter = 'ItemPage'
    current_page_xpath = '//aws:Items/aws:Request/aws:ItemSearchRequest/aws:ItemPage'
    total_pages_xpath = '//aws:Items/aws:TotalPages'
    total_results_xpath = '//aws:Items/aws:TotalResults'

    def __init__(self, fnc, *args, **kwargs):
        # Amazon limits returned pages to max 5
        # if SearchIndex "All" is used!
        try:
            search_index = args[0]
        except IndexError:
            search_index = kwargs['search_index']
        #print args, kwargs, search_index
        if search_index == 'All' and kwargs.get('limit', 400) > 5:
            kwargs['limit'] = 5
        super(LxmlItemSearchPaginator, self).__init__(fnc, *args, **kwargs)

