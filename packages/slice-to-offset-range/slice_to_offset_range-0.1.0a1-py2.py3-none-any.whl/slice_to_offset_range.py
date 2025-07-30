# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from numbers import Integral

from canonicalize_range import normalize_stop


def slice_to_offset_range(slice_object, n):
    if n < 0:
        raise ValueError('n must be a non-negative integer')

    raw_start = slice_object.start
    raw_stop = slice_object.stop
    raw_step = slice_object.step

    # Extract `step` first
    if raw_step is None:
        step = 1
    elif isinstance(raw_step, Integral):
        step = int(raw_step)
        if step == 0:
            raise ValueError('step must be a non-zero integer')
    else:
        raise ValueError('step must be a non-zero integer')

    # Extract `start_offset` and `stop_offset`
    if raw_start is None:
        if step > 0:
            start_offset = 0
        else:
            start_offset = n - 1
    elif isinstance(raw_start, Integral):
        start_index = int(raw_start)
        if start_index < 0:
            start_offset = start_index + n
        else:
            start_offset = start_index
    else:
        raise ValueError('start must be an integer or None')

    if raw_stop is None:
        if step > 0:
            stop_offset = n
        else:
            stop_offset = -1
    elif isinstance(raw_stop, Integral):
        stop_index = int(raw_stop)
        if stop_index < 0:
            stop_offset = stop_index + n
        else:
            stop_offset = stop_index
    else:
        raise ValueError('stop must be an integer or None')

    normalized_stop_offset = normalize_stop(start_offset, stop_offset, step)

    return start_offset, normalized_stop_offset, step
