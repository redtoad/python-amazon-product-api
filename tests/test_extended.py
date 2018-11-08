import os.path

import lxml.objectify
import pytest

from amazonproduct import extended
from amazonproduct.exceptions import (
    InvalidClientTokenId, InvalidSignature, TooManyRequests, InternalError, AccountLimitExceeded)

_here = os.path.dirname(os.path.abspath(__file__))

GENERAL_API_ERRORS = [
    (InvalidClientTokenId, "error-InvalidClientTokenId.xml"),
    (InvalidSignature, "error-SignatureDoesNotMatch.xml"),
    (TooManyRequests, "error-RequestThrottled.xml"),
    (InternalError, "error-InternalError.xml"),
    (AccountLimitExceeded, "error-AccountLimitExceeded.xml"),
]


@pytest.mark.parametrize(
    "exc,xml", GENERAL_API_ERRORS,
    ids=[cls.__name__ for cls, _ in GENERAL_API_ERRORS])
def test_error_parser_raises_all_general_errors(exc, xml):
    with pytest.raises(exc):
        path = os.path.join(_here, xml)
        root = lxml.objectify.fromstring(open(path).read())
        extended.error_parser(root)


def test_error_parser_does_not_raise_an_error_if_there_isnt_one():
    path = os.path.join(_here, "ItemSearch-test-page-1.xml")
    root = lxml.objectify.fromstring(open(path).read())
    extended.error_parser(root)

