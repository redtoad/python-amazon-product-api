
import base64
import datetime
import hmac
import hashlib
import time

try:
    import urllib.parse as urlparse
except ImportError:
    import urllib as urlparse

import requests

__version__ = "0.3.0-dev"

USER_AGENT = (
    "python-amazon-product-api/%s "
    "+https://pypi.org/project/python-amazon-product-api/" % __version__)


class UnknownLocale(Exception):
    """
    Raised when unknown locale is specified.
    """


#: Hosts for Product Advertising API Endpoints
#: http://docs.aws.amazon.com/AWSECommerceService/latest/DG/AnatomyOfaRESTRequest.html
HOSTS = {
    "au": "webservices.amazon.com.au",
    "br": "webservices.amazon.com.br",
    "ca": "webservices.amazon.ca",
    "cn": "webservices.amazon.cn",
    "de": "webservices.amazon.de",
    "es": "webservices.amazon.es",
    "fr": "webservices.amazon.fr",
    "in": "webservices.amazon.in",
    "it": "webservices.amazon.it",
    "jp": "webservices.amazon.jp",
    "mx": "webservices.amazon.com.mx",
    "uk": "webservices.amazon.co.uk",
    "us": "webservices.amazon.com",
}


class CoreAPI(object):

    """
    Support for core functionality of Product Advertising API.
    """

    DEFAULT_VERSION = "2011-08-01"  #: supported Amazon API version
    REQUESTS_PER_SECOND = 0.5  #: max requests per second
    TIMEOUT = 5  #: timeout in seconds

    def __init__(self, access_key, secret_key, locale, associate_tag):
        self.access_key = access_key
        self.secret_key = secret_key
        self.locale = locale
        self.associate_tag = associate_tag
        self.last_call = datetime.datetime(1970, 1, 1)

    @property
    def host(self):
        try:
            return HOSTS[self.locale]
        except KeyError:
            raise UnknownLocale(self.locale)

    OPERATIONS = [
        "ItemSearch",
        "ItemLookup",
        "SimilarityLookup",
        "BrowseNodeLookup",
        "CartAdd", 
        "CartModify",
        "CartGet",
        "CartClear",
    ]

    def __getattr__(self, name):
        # create operation shortcuts
        if name in self.OPERATIONS:
            def operation(**parameters):
                return self(Operation=name, **parameters)
            return operation
        raise AttributeError(name)  # pragma: no cover

    def __call__(self, **parameters):
        url = self._build_url(**parameters)
        return self._fetch(url)

    def _build_url(self, **qargs):
        """
        Builds a signed URL for querying Amazon AWS.  
        """
        # use the version this class was build for by default
        if "Version" not in qargs:
            qargs["Version"] = self.DEFAULT_VERSION

        if isinstance(qargs.get("ResponseGroup"), list):
            qargs["ResponseGroup"] = ",".join(qargs["ResponseGroup"])

        return signed_url(self.host, self.access_key, self.secret_key,
                          self.associate_tag, **qargs)

    def _fetch(self, url):
        """
        Calls the Amazon Product Advertising API and returns the response.
        """
        # Be nice and wait for some time
        # before submitting the next request
        delta = datetime.datetime.now() - self.last_call
        throttle = datetime.timedelta(seconds=1/self.REQUESTS_PER_SECOND)
        if delta < throttle:
            wait = throttle-delta
            time.sleep(wait.seconds+wait.microseconds/1000000.0)  # pragma: no cover
        self.last_call = datetime.datetime.now()

        response = requests.get(url, stream=True, headers={
            "User-Agent": USER_AGENT
        })
        # # https://github.com/kennethreitz/requests/issues/2155
        # response.raw.read = functools.partial(response.raw.read, decode_content=True)
        return response


def signed_url(host, access_key, secret_key, associate_tag, **qargs):
    """
    Returns a sign URL containing to the locale"s host containing the specified
    parameters. This function is based on code by Adam Cox (found at
    http://blog.umlungu.co.uk/blog/2009/jul/12/pyaws-adding-request-authentication/)
    """
    parameters = {key: val for key, val in qargs.items() if val is not None}
    parameters["Service"] = "AWSECommerceService"
    parameters["AWSAccessKeyId"] = access_key
    parameters["AssociateTag"] = associate_tag
    parameters["Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    keys = sorted(parameters.keys())
    args = "&".join("%s=%s" % (
        key, urlparse.quote(str(parameters[key]).encode("utf-8")))
        for key in keys)

    msg = "GET"
    msg += "\n" + host
    msg += "\n/onca/xml"
    msg += "\n" + args

    hsh = hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256)
    signature = urlparse.quote(base64.b64encode(hsh.digest()), safe="")
    return "https://%s/onca/xml?%s&Signature=%s" % (host, args, signature)
