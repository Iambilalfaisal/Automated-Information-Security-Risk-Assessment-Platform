"""
utils.py — Shared helpers: JSON envelope, session id, rate limiting, HTML escaping.
"""

import html
import time
import uuid
from collections import defaultdict
from functools import wraps
from typing import Any, Callable

from flask import jsonify, request

import config

# In-memory rate limit store: ip -> list of timestamps
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def api_response(
    success: bool,
    data: Any = None,
    error: str | None = None,
    status: int = 200,
):
    """
    Build consistent JSON envelope {success, data, error}.

    Args:
        success: Whether the operation succeeded.
        data: Payload on success.
        error: Error message on failure.
        status: HTTP status code.

    Returns:
        Flask JSON response tuple.
    """
    body = {"success": success, "data": data, "error": error}
    return jsonify(body), status


def get_session_id() -> str:
    """
    Resolve session id from header X-Session-Id or query param session_id.
    Generates a new UUID if missing (client should persist it).
    """
    sid = request.headers.get("X-Session-Id") or request.args.get("session_id")
    if not sid:
        sid = str(uuid.uuid4())
    return sid


def validate_str_field(value: Any, field_name: str, max_len: int = 255, required: bool = True) -> str:
    """
    Validate and normalise a string input field.

    Args:
        value: Raw value from request body.
        field_name: Name used in error messages.
        max_len: Maximum allowed character length.
        required: Whether an empty value is rejected.

    Returns:
        The validated string.

    Raises:
        ValueError: If required-but-empty or exceeds max_len.
    """
    text = "" if value is None else str(value).strip()
    if required and not text:
        raise ValueError(f"{field_name} is required")
    if len(text) > max_len:
        raise ValueError(f"{field_name} exceeds maximum length of {max_len} characters")
    return text


def escape_output(value: Any) -> Any:
    """
    Recursively escape string values for XSS-safe API output.

    Args:
        value: Scalar, dict, or list to escape.

    Returns:
        Escaped structure of same shape.
    """
    if isinstance(value, str):
        return html.escape(value)
    if isinstance(value, dict):
        return {k: escape_output(v) for k, v in value.items()}
    if isinstance(value, list):
        return [escape_output(v) for v in value]
    return value


def _client_ip() -> str:
    """Best-effort client IP for rate limiting."""
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()


def rate_limit(max_requests: int | None = None, window_seconds: int | None = None) -> Callable:
    """
    Decorator enforcing per-IP request rate limit.

    Args:
        max_requests: Max requests per window (default from config).
        window_seconds: Window size in seconds.

    Returns:
        Decorated view function.
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            limit = max_requests or config.RATE_LIMIT_REQUESTS
            window = window_seconds or config.RATE_LIMIT_WINDOW_SECONDS
            ip = _client_ip()
            now = time.time()
            # Prune old entries
            _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if now - t < window]
            if len(_rate_limit_store[ip]) >= limit:
                return api_response(False, None, "Rate limit exceeded. Try again later.", 429)
            _rate_limit_store[ip].append(now)
            return f(*args, **kwargs)

        return wrapped

    return decorator
