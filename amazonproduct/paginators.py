
class BaseResultPaginator (object):

    """
    Wrapper class for paginated results. This class will call the passed
    function iteratively until either the specified limit is reached or all
    result pages are fetched.

    Although probably only useful in theory, it can be used by itself to 
    manually iterate over paginated results. A small example fetching reviews
    for a book::

        api = API(AWS_KEY, SECRET_KEY)
        class ReviewPaginator (BasePaginator):
            # specify attributes counter and limit, as well as and methods 
            # get_current_page, get_total_pages and get_total_results
            # ...

        paginator = ReviewPaginator()
        for root in paginator(api.item_lookup, id=isbn, IdType='ISBN',
                             SearchIndex='Books', ResponseGroup='Reviews'):
            print root.Review.AttributeOfInterest

    """

    def __init__(self, counter, limit=400):
        """
        :param counter: counter variable passed to AWS.
        :param limit: limit fetched pages to this amount (restricted to a 
        maximum of 400 pages by API itself).
        """
        self.counter = counter
        self.limit = limit

    def __call__(self, fun, *args, **kwargs):
        """
        Iterate over all paginated results of ``fun``.
        """
        current_page = 0
        total_pages = 1
        total_results = 0

        kwargs[self.counter] = kwargs.get(self.counter, 1)
        limit = kwargs.get('limit', self.limit)

        while (current_page < total_pages
        and (limit is None or current_page < limit)):

            root = fun(*args, **kwargs)

            current_page = self.get_current_page(root)
            total_pages = self.get_total_pages(root)
            total_results = self.get_total_results(root)

            yield root

            kwargs[self.counter] += 1

    def get_current_page(self, node):
        """
        Extracts current page (as ``int``) from XML node.
        """
        raise NotImplementedError

    def get_total_pages(self, node):
        """
        Extracts number of total result pages (as ``int``) from XML node.
        """
        raise NotImplementedError

    def get_total_results(self, node):
        """
        Extracts number of total results (as ``int``) from XML node.
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
            paginator = getattr(processor, '%s_paginator' % fnc.__name__)
            return paginator(fnc, api, *args, **kwargs)
        except AttributeError:
            return fnc(api, *args, **kwargs)
    return wrapped


class LxmlPaginator (BaseResultPaginator):

    """
    A small example fetching reviews for a book::

        api = API(AWS_KEY, SECRET_KEY)
        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')

        for root in paginator(api.item_lookup, id=isbn, IdType='ISBN',
                             SearchIndex='Books', ResponseGroup='Reviews'):
            ...

    .. note: All three XPath expressions have to return integer values for the
       pagination to work!
    """

    def __init__(self, counter, current_page, total_pages, total_results,
                 limit=400):
        """
        :param counter: counter variable passed to AWS.
        :param current_page: XPath expression locating current paginator page.
        :param total_pages: XPath expression locating total number of pages.
        :param total_results: XPath expression locating total number of results.
        :param limit: limit fetched pages to this amount (restricted to a 
        maximum of 400 pages by API itself).
        :param nspace: used XML name space.
        """
        super(LxmlPaginator, self).__init__(counter, limit)
        self.current_page_xpath = current_page
        self.total_pages_xpath = total_pages
        self.total_results_xpath = total_results
        self.nspace = None

    def namespace(fnc):
        """
        Decorator extracting default namespace which is required for XPath
        expressions.
        """
        def wrapped(obj, root):
            obj.nspace = root.nsmap.get(None, '')
            return fnc(obj, root)
        return wrapped

    @namespace
    def get_total_pages(self, root):
        try:
            node = root.xpath(self.total_pages_xpath,
                          namespaces={'aws' : self.nspace})[0]
            return node.pyval
        except AttributeError:
            # node has no attribute pyval so it better be a number
            return int(node)
        except IndexError:
            return 0

    @namespace
    def get_current_page(self, root):
        try:
            node = root.xpath(self.current_page_xpath,
                          namespaces={'aws' : self.nspace})[0]
            return node.pyval
        except AttributeError:
            # node has no attribute pyval so it better be a number
            return int(node)
        except IndexError:
            return 1

    @namespace
    def get_total_results(self, root):
        try:
            node = root.xpath(self.total_results_xpath,
                          namespaces={'aws' : self.nspace})[0]
            return node.pyval
        except AttributeError:
            # node has no attribute pyval so it better be a number
            return int(node)
        except IndexError:
            return 0


