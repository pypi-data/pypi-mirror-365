# SPDX-FileCopyrightText: © 2024 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Logging interface.
"""
import abc
import enum
import functools
import typing as t


_TLoggerModeResult = t.TypeVar("_TLoggerModeResult", bound=object)


class LoggerMode(abc.ABC, t.Generic[_TLoggerModeResult]):

    def debug(self, message: str, *, aux_name: str = "") -> _TLoggerModeResult:
        return self._log(message, Severity.DEBUG, aux_name)

    def info(self, message: str, *, aux_name: str = "") -> _TLoggerModeResult:
        return self._log(message, Severity.INFO, aux_name)

    def warning(self, message: str, *, aux_name: str = "") -> _TLoggerModeResult:
        return self._log(message, Severity.WARNING, aux_name)

    def fatal(self, message: str, *, aux_name: str = "") -> _TLoggerModeResult:
        return self._log(message, Severity.FATAL, aux_name)

    @abc.abstractmethod
    def _log(self, message: str, severity: "Severity", aux_name: str) -> _TLoggerModeResult:
        pass


class Logger(abc.ABC):

    @property
    @abc.abstractmethod
    def block(self) -> LoggerMode[t.ContextManager["Logger"]]:
        pass

    @property
    @abc.abstractmethod
    def message(self) -> LoggerMode[None]:
        pass


@functools.total_ordering
class Severity(enum.Enum):

    DEBUG = enum.auto()
    INFO = enum.auto()
    WARNING = enum.auto()
    FATAL = enum.auto()

    def __lt__(self, other):
        if type(self) is type(other):
            return self.value < other.value
