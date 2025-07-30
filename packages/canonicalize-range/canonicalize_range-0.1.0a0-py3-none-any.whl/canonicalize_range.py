# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from __future__ import division


def normalize_stop(start, stop, step):
    # type: (int, int, int) -> int
    if step == 0:
        raise ValueError('step cannot be 0')
    elif step > 0:
        if start < stop:
            distance = stop - start
            n_steps, remainder = divmod(distance, step)
            if remainder:
                new_stop = start + (n_steps + 1) * step
            else:
                new_stop = stop
        else:
            new_stop = start
    else:
        if stop < start:
            distance = start - stop
            n_steps, remainder = divmod(distance, -step)
            if remainder:
                new_stop = start + (n_steps + 1) * step
            else:
                new_stop = stop
        else:
            new_stop = start

    return new_stop


def canonicalize_range(range_object):
    # type: (range) -> range
    start = range_object.start
    stop = range_object.stop
    step = range_object.step

    new_stop = normalize_stop(start, stop, step)

    return range(start, new_stop, step)
