"""
Clean structured logging library with direct kwargs support.

Minimal and non-invasive core:
- Does not modify root logger handlers (third-party loggers remain intact).
- ``bind`` / ``unbind``.
- Declarative context managers:
  - ``logger.context(**fields)``
  - ``logger.trace_id(trace_id: str | None = None)``
  - ``logger.request_id(request_id: str | None = None)``
  - ``logger.tracing(trace_id: str | None = None, request_id: str | None = None)``
- Error tracebacks normalized to the ``traceback`` field in JSON output.
- Context priority: per-log kwargs > temporary context > persistent fields.
"""

import logging
from contextlib import contextmanager
from functools import partial
from typing import Any, Callable, Dict, Generator, Literal, Optional
from uuid import uuid4

import structlog

LogMethod = Callable[..., None]


class LoggerProxy:
    """Proxy logger"""

    __slots__ = ("_name", "_logger_fields", "_temporal_fields")

    def __init__(self, app_name: str, **extra_fields: Any) -> None:
        self._name = app_name
        self._logger_fields: Dict[str, Any] = {"app_name": app_name, **extra_fields}
        self._temporal_fields: Dict[str, Any] = dict()

    def bind(self, **fields: Any) -> "LoggerProxy":
        self._logger_fields.update(fields)
        return self

    def unbind(self, field: str) -> "LoggerProxy":
        self._logger_fields.pop(field, None)
        return self

    @property
    def logger_fields(self) -> Dict[str, Any]:
        """Return the persistent fields attached to the logger."""
        return {**self._logger_fields, **self._temporal_fields}

    @property
    def debug(self) -> Callable[..., None]:
        return partial(structlog.get_logger(self._name).bind(**self.logger_fields).debug)

    @property
    def info(self) -> Callable[..., None]:
        return partial(structlog.get_logger(self._name).bind(**self.logger_fields).info)

    @property
    def warning(self) -> Callable[..., None]:
        return partial(structlog.get_logger(self._name).bind(**self.logger_fields).warning)

    @property
    def error(self) -> Callable[..., None]:
        return partial(structlog.get_logger(self._name).bind(**self.logger_fields).error)

    @property
    def exception(self) -> Callable[..., None]:
        return partial(structlog.get_logger(self._name).bind(**self.logger_fields).exception)

    @property
    def critical(self) -> Callable[..., None]:
        return partial(structlog.get_logger(self._name).bind(**self.logger_fields).critical)

    @contextmanager
    def context(self, **extra_fields: Any) -> Generator["LoggerProxy", None, None]:
        """Add temporal fields to the logger context."""
        old = self._temporal_fields.copy()
        try:
            self._temporal_fields.update(extra_fields)
            yield self
        finally:
            self._temporal_fields = old

    @contextmanager
    def trace_id(self, trace_id: Optional[str] = None) -> Generator["LoggerProxy", None, None]:
        """Provide a ``trace_id`` within the context."""
        value = trace_id or str(uuid4())
        with self.context(trace_id=value) as logger:
            yield logger

    @contextmanager
    def request_id(self, request_id: Optional[str] = None) -> Generator["LoggerProxy", None, None]:
        """Provide a ``request_id`` within the context."""
        value = request_id or str(uuid4())
        with self.context(request_id=value) as logger:
            yield logger

    @contextmanager
    def tracing(
        self,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Generator["LoggerProxy", None, None]:
        """Provide both ``trace_id`` and ``request_id`` within the context.

        Args:
            trace_id (str | None): Trace identifier. Auto-generated if ``None``.
            request_id (str | None): Request identifier. Auto-generated if ``None``.

        Yields:
            LoggerProxy: The same logger instance with both identifiers set.
        """
        resolved_trace_id = trace_id or str(uuid4())
        resolved_request_id = request_id or str(uuid4())
        with self.context(trace_id=resolved_trace_id, request_id=resolved_request_id) as logger:
            yield logger

    def get_traceability_headers(self) -> Dict[str, str]:
        """Return HTTP headers for distributed tracing.

        Returns:
            Dict[str, str]: Mapping suitable for use as HTTP headers. Includes
            ``X-Trace-ID`` and ``X-Request-ID`` when present in the current context.
        """
        ctx = {**self._logger_fields, **self._temporal_fields}
        headers: Dict[str, str] = {}
        if "trace_id" in ctx:
            headers["X-Trace-ID"] = str(ctx["trace_id"])
        if "request_id" in ctx:
            headers["X-Request-ID"] = str(ctx["request_id"])
        return headers

    def get_current_trace_id(self) -> Optional[str]:
        """Return the active ``trace_id`` if set, otherwise ``None``."""
        return ({**self._logger_fields, **self._temporal_fields}).get("trace_id", None)

    def get_current_request_id(self) -> Optional[str]:
        """Return the active ``request_id`` if set, otherwise ``None``."""
        return ({**self._logger_fields, **self._temporal_fields}).get("request_id", None)


def _rename_exc_to_traceback(_: Any, __: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize exception fields to traceback.

    structlog.processors.format_exc_info may place the formatted traceback in
    exception or exc_info. This processor moves the value into a single
    canonical traceback key, which simplifies querying in backends such as
    Grafana/Loki.

    Args:
        _ (Any): Unused, required by structlog processor signature.
        __ (str): Unused event name.
        event_dict (Dict[str, Any]): Event payload to be mutated.

    Returns:
        Dict[str, Any]: The updated event payload.
    """
    if "exception" in event_dict and event_dict["exception"] is not None:
        event_dict["traceback"] = event_dict.pop("exception")
    elif "exc_info" in event_dict and event_dict["exc_info"] is not None:
        event_dict["traceback"] = event_dict.pop("exc_info")
    return event_dict


def configure_global_logging(level: Literal["DEBUG", "INFO"] = "INFO") -> None:
    """Configure structlog processors only.

    This function is non-invasive: it does not alter root logger handlers. Third-party
    logging configurations remain untouched. The configured processors control how
    structlog events are rendered.

    Args:
        level (Literal["DEBUG", "INFO"]): Rendering level. ``DEBUG`` enables a
            human-friendly console renderer. ``INFO`` outputs JSON.
    """

    processors = [
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        _rename_exc_to_traceback,
    ]

    match level:
        case "DEBUG":
            log_level = logging.DEBUG
            processors.append(structlog.dev.ConsoleRenderer())
        case "INFO":
            log_level = logging.INFO
            processors.append(structlog.processors.JSONRenderer())
        case _:
            raise ValueError(f"Invalid log level: {level}")

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )


def create_logger(name: str, **context: Any) -> LoggerProxy:
    """Create a structured logger instance.

    Args:
        name (str): Logger name. Emitted as ``app_name`` and used by stdlib logger.
        **context (Any): Persistent fields to attach to every log.

    Returns:
        LoggerProxy: Configured logger instance.
    """
    return LoggerProxy(name, **context)
