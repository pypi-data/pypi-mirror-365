# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from numbers import Integral


def parse_slice(slice_object):
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

    # Depending on the sign of `step`,
    # Parse and normalize `raw_start` and `raw_stop`
    if step > 0:
        if raw_start is None:
            start = None
        elif isinstance(raw_start, Integral):
            start = int(raw_start)
        else:
            raise ValueError('start must be an integer or None')

        if raw_stop is None:
            stop = None
        elif isinstance(raw_stop, Integral):
            stop = int(raw_stop)
        else:
            raise ValueError('stop must be an integer or None')

        if start is not None and stop is not None and stop < start:
            stop = start
    else:
        if raw_start is None:
            start = None
        elif isinstance(raw_start, Integral):
            start = int(raw_start)
        else:
            raise ValueError('start must be an integer or None')

        if raw_stop is None:
            stop = None
        elif isinstance(raw_stop, Integral):
            stop = int(raw_stop)
        else:
            raise ValueError('stop must be an integer or None')

        if start is not None and stop is not None and start < stop:
            stop = start

    return start, stop, step
