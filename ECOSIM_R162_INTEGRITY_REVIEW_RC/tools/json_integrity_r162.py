#!/usr/bin/env python3
"""R162: shared strict JSON parser for read-only EcoSim inputs.

No claim of server-origin authentication. The caller still validates its schema.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

MAX_JSON_BYTES = 10_000_000


def _pairs(items):
    data = {}
    for key, value in items:
        if key in data:
            raise ValueError('R162_DUPLICATE_JSON_KEY: '+repr(key))
        data[key] = value
    return data


def _constant(value):
    raise ValueError('R162_NONSTANDARD_JSON_CONSTANT: '+str(value))


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('R162_OVERFLOWING_JSON_NUMBER: '+value)
    return result


def loads_strict(data):
    return json.loads(data, object_pairs_hook=_pairs,
                      parse_constant=_constant, parse_float=_float)


def read_json(path, max_bytes=MAX_JSON_BYTES):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > max_bytes:
        raise ValueError('R162_JSON_NOT_FILE_OR_OVERSIZED')
    with p.open('r', encoding='utf-8') as source:
        return loads_strict(source.read())
