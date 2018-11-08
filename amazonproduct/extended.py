
import logging

import lxml.objectify
import lxml.etree

from . import core
from .exceptions import (
    InvalidClientTokenId, InternalError, MissingClientTokenId, TooManyRequests, DeprecatedOperation,
    NoExactMatchesFound, AccountLimitExceeded, InvalidCartItem, CartInfoMismatch, ParameterOutOfRange, InvalidAccount,
    InvalidSignature, MissingParameters, InvalidParameterValue, InvalidParameterCombination, ItemAlreadyInCart,
    InvalidEnumeratedParameter, AWSError
)

log = logging.getLogger(__name__)


def xml_parser(resp):
    xml = resp.content
    log.debug("XML to be parsed: %s", xml)
    return lxml.objectify.fromstring(xml)


ERROR_MAP = {
    'AccountLimitExceeded': AccountLimitExceeded,
    'AWS.ECommerceService.CartInfoMismatch': CartInfoMismatch,
    'AWS.ECommerceService.ItemAlreadyInCart': ItemAlreadyInCart,
    'AWS.ECommerceService.ItemNotEligibleForCart': InvalidCartItem,
    'AWS.ECommerceService.NoExactMatches': NoExactMatchesFound,
    'AWS.InvalidAccount': InvalidAccount,
    'AWS.InvalidEnumeratedParameter': InvalidEnumeratedParameter,
    'AWS.InvalidParameterValue': InvalidParameterValue,
    'AWS.MissingParameters': MissingParameters,
    'AWS.ParameterOutOfRange': ParameterOutOfRange,
    'AWS.RestrictedParameterValueCombination': InvalidParameterCombination,
    'Deprecated': DeprecatedOperation,
    'InternalError': InternalError,
    'InvalidClientTokenId': InvalidClientTokenId,
    'MissingClientTokenId': MissingClientTokenId,
    'RequestThrottled': TooManyRequests,
    'SignatureDoesNotMatch': InvalidSignature,
}


def error_parser(root):
    """
    Extracts general AWS errors (global error messages like InvalidAccount)
    and raises the appropriate exceptions. This DOES NOT apply for item-related
    errors. ItemLookup, for instance, can return several valid results together
    with invalid ones.
    """
    def _extract_error():
        try:
            return root.Error.Code, root.Error.Message
        except AttributeError:
            return None, None

    code, msg = _extract_error()
    if code:
        klass = ERROR_MAP.get(code, AWSError)
        raise klass(msg)

    log.debug("No errors found.")
    return root


def result_parser(root):
    log.debug("XML result to be parsed: %s", lxml.etree.tostring(root, pretty_print=False))
    return root


def anonymiser(root):
    """
    Removes access key, signature and associate tag from XML.
    """
    try:
        xml = lxml.etree.tostring(root).decode("utf-8")
        arguments = {
            arg.get("Name"): arg.get("Value")
            for arg in root.OperationRequest.Arguments.Argument
        }
        access_key = arguments.get("AWSAccessKeyId")
        associate = arguments.get("AssociateTag")
        signature = arguments.get("Signature")
        xml = xml.replace(access_key, "XXXX")\
                 .replace(associate, "XXX")\
                 .replace(signature, "XXXXXXXXXX")
        return lxml.objectify.fromstring(xml)
    except AttributeError:
        return root


class _LayeredAPI(core.CoreAPI):

    def __call__(self, **parameters):
        result = core.CoreAPI.__call__(self, **parameters)
        for fnc in self.processors:
            log.debug("Apply processor: %s", fnc)
            result = fnc.__call__(result)
            log.debug("Processor result: %r", result)
        return result

    processors = [
        xml_parser,
        anonymiser,
        error_parser,
        result_parser,
    ]

