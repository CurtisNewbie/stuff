#!/usr/bin/env python3
"""
Hutool-compatible Snowflake ID generator.
Usage: python snowflake.py <prefix> [worker_id] [datacenter_id]
"""
import sys
import time

# Hutool default epoch: 2010-11-04 09:42:54.657 UTC
TWEPOCH = 1288834974657

WORKER_BITS     = 5
DATACENTER_BITS = 5
SEQUENCE_BITS   = 12

MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1  # 4095

_last_ts = -1
_sequence = 0


def next_id(worker_id=0, datacenter_id=0):
    global _last_ts, _sequence

    ts = int(time.time() * 1000)

    if ts == _last_ts:
        _sequence = (_sequence + 1) & MAX_SEQUENCE
        if _sequence == 0:
            while ts <= _last_ts:
                ts = int(time.time() * 1000)
    else:
        _sequence = 0

    _last_ts = ts

    return (
        ((ts - TWEPOCH) << (DATACENTER_BITS + WORKER_BITS + SEQUENCE_BITS))
        | (datacenter_id << (WORKER_BITS + SEQUENCE_BITS))
        | (worker_id << SEQUENCE_BITS)
        | _sequence
    )


if __name__ == "__main__":
    prefix       = sys.argv[1] if len(sys.argv) > 1 else ""
    worker_id    = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    datacenter_id = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    print(f"{prefix}{next_id(worker_id, datacenter_id)}")
