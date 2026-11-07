"""Structured failures stored in execution records."""

from __future__ import annotations

from typing import Any


class Failure(Exception):
    """An honest, structured error. Not inferred from an exit code."""

    def __init__(
        self,
        category: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.message = message
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "category": self.category,
            "message": self.message,
        }
        if self.details:
            body["details"] = self.details
        return body
