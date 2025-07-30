# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from typing import Tuple

from canonicalize_range import normalize_stop

if sys.version_info < (3,):
    XRange = xrange
else:
    XRange = range


def reverse_range(range_object):
    # type: (XRange) -> XRange
    """
    Create a canonicalized, reversed version of the input range.

    Args:
        range_object: The input range to be reversed.

    Returns:
        A new range object that represents the reverse of the input range.
        The step size will be negated while maintaining the same sequence of numbers.
    """
    start = range_object.start
    stop = range_object.stop
    step = range_object.step

    normalized_stop = normalize_stop(start, stop, step)

    if start == normalized_stop:
        return XRange(start, normalized_stop, -step)
    else:
        return XRange(normalized_stop - step, start - step, -step)


def extend_range(range_object, k):
    # type: (XRange, int) -> Tuple[XRange, XRange]
    """
    Extend a range by k steps and return both the canonicalized, extended range and the canonicalized extension.

    Args:
        range_object: The input range to be extended.
        k: The number of steps to extend the range by.

    Returns:
        A tuple containing two range objects:
        1. The extended range (original range + k steps)
        2. The extension part (just the added k steps)
    """
    start = range_object.start
    stop = range_object.stop
    step = range_object.step

    normalized_stop = normalize_stop(start, stop, step)

    extended_range_stop = normalized_stop + k * step

    normalized_extended_range_stop = normalize_stop(start, extended_range_stop, step)
    normalized_extended_by_stop = normalize_stop(normalized_stop, extended_range_stop, step)

    extended_range = XRange(start, normalized_extended_range_stop, step)
    extended_by = XRange(normalized_stop, normalized_extended_by_stop, step)

    return extended_range, extended_by
