import functools

import pytest

from amazonproduct.core import CoreAPI
from amazonproduct.operations import Operation


def test_parameters_for_single_operation():
    op = Operation('ItemSearch', ItemId='1')
    assert op.parameters == op._params[0]
    assert len(op._params) == 1


def test_add_mismatch_operations_fails():
    with pytest.raises(ValueError):
        _ = Operation('ItemSearch') + Operation('CartAdd')


UNSUPPORTED_OPERATIONS = "CartAdd CartClear CartCreate CartGet CartModify".split()


@pytest.mark.parametrize('op', UNSUPPORTED_OPERATIONS)
def test_add_unsupported_operations_fails(op):
    with pytest.raises(ValueError):
        _ = Operation(op) + Operation(op)


@pytest.mark.parametrize('op1', CoreAPI.OPERATIONS[:1])
@pytest.mark.parametrize('op2', CoreAPI.OPERATIONS[1:])
def test_add_different_operations_fails(op1,op2):
    with pytest.raises(ValueError):
        _ = Operation(op1) + Operation(op2)


def test_add_operations():
    op1 = Operation('ItemLookup', ItemId='0976925524', IdType='ASIN')
    op2 = Operation('ItemLookup', ItemId='80348287843', IdType='ASIN')
    res = op1 + op2
    assert res.parameters == {
        'ItemLookup.1.ItemId': '0976925524',
        'ItemLookup.2.ItemId': '80348287843',
        'ItemLookup.Shared.IdType': 'ASIN'
    }


def test_add_more_than_two_operations_fails():
    with pytest.raises(ValueError):
        _ = Operation('ItemSearch') + Operation('ItemSearch') + Operation('ItemSearch')


def test_add_more_than_ten_itemlookups_fails():
    with pytest.raises(ValueError):
        res = Operation('ItemLookup')
        for _ in range(10):
             res += Operation('ItemLookup')


def test_add_multiple_lookup_operations():
    ops = [Operation('ItemLookup', ItemId='%i' % (i+1), IdType='ASIN') for i in range(10)]
    res = functools.reduce(lambda a,b: a+b, ops)
    assert res.parameters == {
        'ItemId': '1,2,3,4,5,6,7,8,9,10',
        'IdType': 'ASIN'
    }
