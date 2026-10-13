"""Date helpers shared by the service functions."""

from datetime import date, datetime


def today() -> date:
    """Today's date from the system clock, in the machine's local timezone."""
    return date.today()


def to_local_date(timestamp: str) -> date:
    """Local calendar date of an ISO-8601 timestamp such as the admin API's
    "2026-10-05T12:01:40.717Z" (UTC). Python 3.10 cannot parse the "Z" itself.
    Raises ValueError for anything that is not a timestamp."""
    moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return moment.astimezone().date()
