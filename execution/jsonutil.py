"""Strict JSON parsing and canonical record encoding."""

from __future__ import annotations

import hashlib
import json
import math
from typing import NoReturn

from execution.constants import MAX_JSON_DEPTH
from execution.errors import Failure


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    """Encode one JSON document with sorted keys and a trailing newline."""
    text = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def _reject_constant(constant: str) -> NoReturn:
    raise Failure(
        "nonfinite_json",
        "JSON contains a non-finite constant.",
        {"constant": constant},
    )


def _walk(value: object, depth: int) -> None:
    if depth > MAX_JSON_DEPTH:
        raise Failure(
            "input_rejected" if depth else "malformed_output",
            "JSON nesting exceeds the supported depth.",
            {"max_depth": MAX_JSON_DEPTH},
        )
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Failure(
                "nonfinite_json",
                "JSON contains a non-finite number.",
            )
        return
    if isinstance(value, dict):
        for nested in value.values():
            _walk(nested, depth + 1)
        return
    if isinstance(value, list):
        for nested in value:
            _walk(nested, depth + 1)


def parse_single_json(text: str, *, depth_category: str) -> object:
    """Parse exactly one finite JSON value. Trailing junk is rejected."""
    if text.strip() == "":
        raise Failure(depth_category, "JSON input is empty.")
    leading = text[: len(text) - len(text.lstrip(" \t\r\n"))]
    if leading and not leading.isspace():
        raise Failure(depth_category, "JSON has a non-whitespace prefix.")
    decoder = json.JSONDecoder(parse_constant=_reject_constant)
    try:
        value, index = decoder.raw_decode(text.lstrip(" \t\r\n"))
    except Failure:
        raise
    except json.JSONDecodeError as exc:
        raise Failure(
            depth_category, "JSON is malformed.", {"reason": exc.msg}
        ) from None
    trailing = text.lstrip(" \t\r\n")[index:]
    if trailing.strip() != "":
        raise Failure(depth_category, "JSON contains more than one value.")
    try:
        _walk(value, 0)
    except Failure as exc:
        if exc.category == "input_rejected":
            raise Failure(depth_category, exc.message, exc.details) from None
        raise
    return value
