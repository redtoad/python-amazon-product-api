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


def test_add_multiple_lookup_operations():
    ops = [Operation('ItemLookup', ItemId='%03i' % (i+1), IdType='ASIN') for i in range(10)]
    res = functools.reduce(lambda a,b: a+b, ops)
    assert res.parameters == {
        'ItemLookup.1.ItemId': '001',
        'ItemLookup.2.ItemId': '002',
        'ItemLookup.3.ItemId': '003',
        'ItemLookup.4.ItemId': '004',
        'ItemLookup.5.ItemId': '005',
        'ItemLookup.6.ItemId': '006',
        'ItemLookup.7.ItemId': '007',
        'ItemLookup.8.ItemId': '008',
        'ItemLookup.9.ItemId': '009',
        'ItemLookup.10.ItemId': '010',
        'ItemLookup.Shared.IdType': 'ASIN'
    }
