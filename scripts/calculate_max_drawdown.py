"""JSON entry point for calculate_max_drawdown.

The library function still returns a float. This script only adapts one JSON
object on stdin to that function and writes one JSON object on stdout.
Diagnostics go to stderr. The process exits nonzero when it cannot return a
result.
"""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Sequence
from typing import cast

from quant_software_factory import calculate_max_drawdown


def _reject_constant(constant: str) -> None:
    raise ValueError(f"non-finite JSON value: {constant}")


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw, parse_constant=_reject_constant)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"invalid input JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict) or set(payload) != {"equity_curve"}:
        print("input must be a JSON object with exactly equity_curve", file=sys.stderr)
        return 2
    curve = payload["equity_curve"]
    if not isinstance(curve, list):
        print("equity_curve must be a list", file=sys.stderr)
        return 2
    try:
        result = calculate_max_drawdown(cast(Sequence[float], curve))
    except (TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if (
        isinstance(result, bool)
        or not isinstance(result, float)
        or not math.isfinite(result)
    ):
        print("library returned a non-finite result", file=sys.stderr)
        return 1
    json.dump({"max_drawdown": result}, sys.stdout, allow_nan=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
