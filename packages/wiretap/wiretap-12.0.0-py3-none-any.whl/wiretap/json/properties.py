import logging
import os
import traceback
from datetime import datetime, timezone
from typing import Protocol, Any

from wiretap.helpers import unpack


class JSONProperty(Protocol):
    def emit(self, record: logging.LogRecord) -> dict[str, Any] | None:
        pass


class TimestampProperty(JSONProperty):
    def __init__(self, tz: str = "utc"):
        super().__init__()
        match tz.casefold().strip():
            case "utc":
                self.tz = datetime.now(timezone.utc).tzinfo  # timezone.utc
            case "local" | "lt":
                self.tz = datetime.now(timezone.utc).astimezone().tzinfo

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        return {
            "timestamp": datetime.fromtimestamp(record.created, tz=self.tz)
        }


class ExecutionProperty(JSONProperty):

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        procedure, trace = unpack(record)
        if procedure:
            return {
                "execution": {
                    "id": procedure.execution.id,
                    "path": procedure.execution.path,
                    "elapsed": procedure.execution.elapsed,
                }
            }
        else:
            return {
                "execution": {
                    "id": None,
                    "path": None,
                    "elapsed": None,
                }
            }


class ProcedureProperty(JSONProperty):

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        procedure, trace = unpack(record)
        if procedure:
            return {
                "procedure": {
                    "id": procedure.id,
                    "name": procedure.name,
                    "data": procedure.data,
                    "tags": procedure.tags,
                    "elapsed": procedure.elapsed.current,
                    "depth": procedure.depth,
                    "times": procedure.times,
                }
            }
        else:
            return {
                "procedure": {
                    "id": None,
                    "name": record.funcName,
                    "data": None,
                    "tags": None,
                    "elapsed": None,
                    "depth": None,
                }
            }


class TraceProperty(JSONProperty):

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        procedure, trace = unpack(record)
        if trace:
            return {
                "trace": {
                    "name": trace.name,
                    "level": record.levelname.lower(),
                    "message": trace.message,
                    "data": trace.data,
                    "tags": sorted(trace.tags),
                }
            }
        else:
            return {
                "trace": {
                    "name": record.levelname.lower(),
                    "level": record.levelname.lower(),
                    "message": record.msg,
                    "data": None,
                    "tags": ["plain"]
                }
            }


class SourceProperty(JSONProperty):

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        procedure, trace = unpack(record)
        if procedure:
            if procedure.trace_count == 1:
                return {
                    "source": {
                        "func": procedure.func,
                        "file": procedure.file,
                        "line": procedure.line,
                    }
                }
            else:
                return {}
        else:
            return {
                "source": {
                    "func": record.funcName,
                    "file": record.filename,
                    "line": record.lineno
                }
            }


class ExceptionProperty(JSONProperty):

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        if record.exc_info:
            exc_cls, exc, exc_tb = record.exc_info
            # format_exception returns a list of lines. Join it a single sing or otherwise an array will be logged.
            return {
                "exception": {
                    "name": exc_cls.__name__,  # type: ignore
                    "message": str(exc),
                    "stack_trace": "".join(traceback.format_exception(exc_cls, exc, exc_tb))}
            }
        else:
            return {}


class EnvironmentProperty(JSONProperty):

    def __init__(self, names: list[str]):
        self.names = names

    def emit(self, record: logging.LogRecord) -> dict[str, Any]:
        return {"environment": {k: os.environ.get(k) for k in self.names}}
