"""Pluggable authentication for the research workstation API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class AuthContext:
    subject: str
    method: str
    claims: dict[str, Any]


@runtime_checkable
class AuthPlugin(Protocol):
    name: str

    def authenticate(self, authorization: str | None, api_key: str | None) -> AuthContext | None:
        """Return AuthContext if ok, None if this plugin does not apply, raise/deny via false."""
        ...


class AuthError(Exception):
    def __init__(self, message: str = "unauthorized", status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
