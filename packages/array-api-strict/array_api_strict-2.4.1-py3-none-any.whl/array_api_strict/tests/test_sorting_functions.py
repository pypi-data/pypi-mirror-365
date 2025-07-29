import pytest

import array_api_strict as xp


@pytest.mark.parametrize(
    "obj, axis, expected",
    [
        ([0, 0], -1, [0, 1]),
        ([0, 1, 0], -1, [1, 0, 2]),
        ([[0, 1], [1, 1]], 0, [[1, 0], [0, 1]]),
        ([[0, 1], [1, 1]], 1, [[1, 0], [0, 1]]),
    ],
)
def test_stable_desc_argsort(obj, axis, expected):
    """
    Indices respect relative order of a descending stable-sort

    See https://github.com/numpy/numpy/issues/20778
    """
    x = xp.asarray(obj)
    out = xp.argsort(x, axis=axis, stable=True, descending=True)
    assert xp.all(out == xp.asarray(expected))


def test_argsort_device():
    x = xp.asarray([1., 2., -1., 3.141], device=xp.Device("device1"))
    y = xp.argsort(x)

    assert y.device == x.device


def test_sort_device():
    x = xp.asarray([1., 2., -1., 3.141], device=xp.Device("device1"))
    y = xp.sort(x)

    assert y.device == x.device