"""The one response shape every function in this service returns:

    {
        "status":  "success" | "failed" | "pending",
        "error":   None on success, otherwise what went wrong / why not done yet,
        "message": short human-readable summary,
        "data":    optional details for the caller (e.g. what was deleted),
    }

Build it with ServiceResponse.success / .failed / .pending; to_dict() gives
the JSON-ready form.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


def describe_error(error: Union[str, Exception]) -> str:
    """Text for the "error" field. An OSError's text embeds the file path, so
    only its reason (e.g. "Permission denied") is kept."""
    if isinstance(error, OSError):
        return error.strerror or type(error).__name__
    return str(error)


class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass(frozen=True)
class ServiceResponse:
    status: Status
    message: str
    error: Optional[str] = None
    data: Optional[dict] = None

    def __post_init__(self):
        if self.status == Status.SUCCESS and self.error is not None:
            raise ValueError("a success response cannot carry an error")
        if self.status != Status.SUCCESS and not self.error:
            raise ValueError(f"a {self.status.value} response needs an error")

    @classmethod
    def success(cls, message: str, data: Optional[dict] = None) -> "ServiceResponse":
        return cls(Status.SUCCESS, message, None, data)

    @classmethod
    def failed(cls, message: str, error: Union[str, Exception], data: Optional[dict] = None) -> "ServiceResponse":
        return cls(Status.FAILED, message, describe_error(error), data)

    @classmethod
    def pending(cls, message: str, error: Union[str, Exception], data: Optional[dict] = None) -> "ServiceResponse":
        return cls(Status.PENDING, message, describe_error(error), data)

    def to_dict(self) -> dict:
        return {"status": self.status.value, "error": self.error, "message": self.message, "data": self.data}
