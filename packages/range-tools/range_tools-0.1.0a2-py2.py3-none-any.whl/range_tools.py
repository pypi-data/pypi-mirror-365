# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from __future__ import division

from typing import Tuple


def contains(start, stop, step, element):
    # type: (int, int, int, int) -> bool
    """Checks if a given element is part of a range."""
    if step == 0:
        raise ValueError('step cannot be 0')
    elif step > 0:
        return start <= element < stop and (element - start) % step == 0
    else:
        return stop < element <= start and (start - element) % (-step) == 0


def get_length(start, stop, step):
    # type: (int, int, int) -> int
    """
    Get the length of a range (how many elements it contains).
    """
    if step == 0:
        raise ValueError('step cannot be 0')
    elif step > 0:
        if start < stop:
            distance = stop - start
            n_step, remainder = divmod(distance, step)
            if remainder:
                return n_step + 1
            else:
                return n_step
        else:
            return 0
    else:
        if stop < start:
            distance = start - stop
            n_step, remainder = divmod(distance, -step)
            if remainder:
                return n_step + 1
            else:
                return n_step
        else:
            return 0


def canonicalize_stop(start, stop, step):
    # type: (int, int, int) -> int
    length = get_length(start, stop, step)
    return start + length * step


def canonicalize_range(start, stop, step):
    # type: (int, int, int) -> Tuple[int, int, int]
    """
    Canonicalize a range to ensure it contains complete steps from its start value.
    """
    return start, canonicalize_stop(start, stop, step), step


def reverse_range(start, stop, step):
    # type: (int, int, int) -> Tuple[int, int, int]
    """
    Create a canonicalized, reversed version of a range.
    """
    normalized_stop = canonicalize_stop(start, stop, step)

    if start == normalized_stop:
        return start, normalized_stop, -step
    else:
        return normalized_stop - step, start - step, -step


def extend_range(start, stop, step, k):
    # type: (int, int, int, int) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]
    """
    Extend a range by k steps and return both the canonicalized, extended range and the canonicalized extension.
    """
    normalized_stop = canonicalize_stop(start, stop, step)

    extended_range_stop = normalized_stop + k * step

    normalized_extended_range_stop = canonicalize_stop(start, extended_range_stop, step)
    normalized_extended_by_stop = canonicalize_stop(normalized_stop, extended_range_stop, step)

    extended_range = (start, normalized_extended_range_stop, step)
    extended_by = (normalized_stop, normalized_extended_by_stop, step)

    return extended_range, extended_by


def slice_to_offset_range(sequence_length, slice_object):
    # type: (int, slice) -> Tuple[int, int, int]
    """Given a sequence length, converts a Python slice object to a canonicalized offset range `(offset_start, offset_stop, offset_step)` describing which elements would be selected by that slice object."""
    if sequence_length < 0:
        raise ValueError('sequence length must be non-negative')

    raw_start = slice_object.start
    raw_stop = slice_object.stop
    raw_step = slice_object.step

    # Extract `step` first
    if raw_step is None:
        step = 1
    elif isinstance(raw_step, int):
        step = raw_step
        if step == 0:
            raise ValueError('step must be non-zero')
    else:
        raise ValueError('step must be a non-zero int or None')

    # Extract `start_offset` and `stop_offset`
    if raw_start is None:
        if step > 0:
            offset_start = 0
        else:
            offset_start = sequence_length - 1
    elif isinstance(raw_start, int):
        start_index = raw_start
        if start_index < 0:
            offset_start = start_index + sequence_length
        else:
            offset_start = start_index
    else:
        raise ValueError('start must be an int or None')

    if raw_stop is None:
        if step > 0:
            offset_stop = sequence_length
        else:
            offset_stop = -1
    elif isinstance(raw_stop, int):
        stop_index = raw_stop
        if stop_index < 0:
            offset_stop = stop_index + sequence_length
        else:
            offset_stop = stop_index
    else:
        raise ValueError('stop must be an int or None')

    return offset_start, canonicalize_stop(offset_start, offset_stop, step), step


def slice_range(start, stop, step, slice_object):
    # type: (int, int, int, slice) -> Tuple[int, int, int]
    """Applies a slice operation to an existing range, returning a canonicalized new range."""
    range_length = get_length(start, stop, step)
    offset_start, offset_stop, offset_step = slice_to_offset_range(range_length, slice_object)

    new_start = start + step * offset_start
    new_stop = start + step * offset_stop
    new_step = step * offset_step

    return new_start, new_stop, new_step
