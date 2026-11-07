"""Trusted remote script-execution machinery.

The generic runner prepares an approved commit, executes one allowlisted
repository script, and writes a reproducible execution record. It does not
judge correctness.
"""

SCHEMA_VERSION = 1
