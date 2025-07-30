from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Self,
    TypedDict,
    TypeVar,
    assert_never,
    overload,
    override,
)
from zoneinfo import ZoneInfo

from whenever import Date, DateDelta, PlainDateTime, Time, TimeDelta, ZonedDateTime

from utilities.dataclasses import replace_non_sentinel
from utilities.functions import get_class_name
from utilities.sentinel import Sentinel, sentinel
from utilities.whenever import format_compact
from utilities.zoneinfo import UTC, ensure_time_zone, get_time_zone_name

if TYPE_CHECKING:
    from utilities.types import TimeZoneLike

_TDate_co = TypeVar("_TDate_co", bound=Date | dt.date, covariant=True)
_TTime_co = TypeVar("_TTime_co", bound=Time | dt.time, covariant=True)
_TDateTime_co = TypeVar(
    "_TDateTime_co", bound=ZonedDateTime | dt.datetime, covariant=True
)


class PeriodDict[T: Date | Time | ZonedDateTime | dt.date | dt.time | dt.datetime](
    TypedDict
):
    start: T
    end: T


@dataclass(repr=False, order=True, unsafe_hash=True, kw_only=False)
class DatePeriod:
    """A period of dates."""

    start: Date
    end: Date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise _PeriodInvalidError(start=self.start, end=self.end)

    def __add__(self, other: DateDelta, /) -> Self:
        """Offset the period."""
        return self.replace(start=self.start + other, end=self.end + other)

    def __contains__(self, other: Date, /) -> bool:
        """Check if a date/datetime lies in the period."""
        return self.start <= other <= self.end

    @override
    def __repr__(self) -> str:
        cls = get_class_name(self)
        return f"{cls}({self.start}, {self.end})"

    def __sub__(self, other: DateDelta, /) -> Self:
        """Offset the period."""
        return self.replace(start=self.start - other, end=self.end - other)

    def at(
        self, obj: Time | tuple[Time, Time], /, *, time_zone: TimeZoneLike = UTC
    ) -> ZonedDateTimePeriod:
        """Combine a date with a time to create a datetime."""
        match obj:
            case Time() as time:
                start = end = time
            case Time() as start, Time() as end:
                ...
            case never:
                assert_never(never)
        tz = ensure_time_zone(time_zone).key
        return ZonedDateTimePeriod(
            self.start.at(start).assume_tz(tz), self.end.at(end).assume_tz(tz)
        )

    @property
    def delta(self) -> DateDelta:
        """The delta of the period."""
        return self.end - self.start

    def format_compact(self) -> str:
        """Format the period in a compact fashion."""
        fc, start, end = format_compact, self.start, self.end
        if self.start == self.end:
            return f"{fc(start)}="
        if self.start.year_month() == self.end.year_month():
            return f"{fc(start)}-{fc(end, fmt='%d')}"
        if self.start.year == self.end.year:
            return f"{fc(start)}-{fc(end, fmt='%m%d')}"
        return f"{fc(start)}-{fc(end)}"

    @classmethod
    def from_dict(cls, mapping: PeriodDict[_TDate_co], /) -> Self:
        """Convert the dictionary to a period."""
        match mapping["start"]:
            case Date() as start:
                ...
            case dt.date() as py_date:
                start = Date.from_py_date(py_date)
            case never:
                assert_never(never)
        match mapping["end"]:
            case Date() as end:
                ...
            case dt.date() as py_date:
                end = Date.from_py_date(py_date)
            case never:
                assert_never(never)
        return cls(start=start, end=end)

    def replace(
        self, *, start: Date | Sentinel = sentinel, end: Date | Sentinel = sentinel
    ) -> Self:
        """Replace elements of the period."""
        return replace_non_sentinel(self, start=start, end=end)

    def to_dict(self) -> PeriodDict[Date]:
        """Convert the period to a dictionary."""
        return PeriodDict(start=self.start, end=self.end)


@dataclass(repr=False, order=True, unsafe_hash=True, kw_only=False)
class TimePeriod:
    """A period of times."""

    start: Time
    end: Time

    @override
    def __repr__(self) -> str:
        cls = get_class_name(self)
        return f"{cls}({self.start}, {self.end})"

    def at(
        self, obj: Date | tuple[Date, Date], /, *, time_zone: TimeZoneLike = UTC
    ) -> ZonedDateTimePeriod:
        """Combine a date with a time to create a datetime."""
        match obj:
            case Date() as date:
                start = end = date
            case Date() as start, Date() as end:
                ...
            case never:
                assert_never(never)
        return DatePeriod(start, end).at((self.start, self.end), time_zone=time_zone)

    @classmethod
    def from_dict(cls, mapping: PeriodDict[_TTime_co], /) -> Self:
        """Convert the dictionary to a period."""
        match mapping["start"]:
            case Time() as start:
                ...
            case dt.time() as py_time:
                start = Time.from_py_time(py_time)
            case never:
                assert_never(never)
        match mapping["end"]:
            case Time() as end:
                ...
            case dt.time() as py_time:
                end = Time.from_py_time(py_time)
            case never:
                assert_never(never)
        return cls(start=start, end=end)

    def replace(
        self, *, start: Time | Sentinel = sentinel, end: Time | Sentinel = sentinel
    ) -> Self:
        """Replace elements of the period."""
        return replace_non_sentinel(self, start=start, end=end)

    def to_dict(self) -> PeriodDict[Time]:
        """Convert the period to a dictionary."""
        return PeriodDict(start=self.start, end=self.end)


@dataclass(repr=False, order=True, unsafe_hash=True, kw_only=False)
class ZonedDateTimePeriod:
    """A period of time."""

    start: ZonedDateTime
    end: ZonedDateTime

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise _PeriodInvalidError(start=self.start, end=self.end)
        if self.start.tz != self.end.tz:
            raise _PeriodTimeZoneError(
                start=ZoneInfo(self.start.tz), end=ZoneInfo(self.end.tz)
            )

    def __add__(self, other: TimeDelta, /) -> Self:
        """Offset the period."""
        return self.replace(start=self.start + other, end=self.end + other)

    def __contains__(self, other: ZonedDateTime, /) -> bool:
        """Check if a date/datetime lies in the period."""
        return self.start <= other <= self.end

    @override
    def __repr__(self) -> str:
        cls = get_class_name(self)
        return f"{cls}({self.start.to_plain()}, {self.end.to_plain()}[{self.time_zone.key}])"

    def __sub__(self, other: TimeDelta, /) -> Self:
        """Offset the period."""
        return self.replace(start=self.start - other, end=self.end - other)

    @property
    def delta(self) -> TimeDelta:
        """The duration of the period."""
        return self.end - self.start

    @overload
    def exact_eq(self, period: ZonedDateTimePeriod, /) -> bool: ...
    @overload
    def exact_eq(self, start: ZonedDateTime, end: ZonedDateTime, /) -> bool: ...
    @overload
    def exact_eq(
        self, start: PlainDateTime, end: PlainDateTime, time_zone: ZoneInfo, /
    ) -> bool: ...
    def exact_eq(self, *args: Any) -> bool:
        """Check if a period is exactly equal to another."""
        if (len(args) == 1) and isinstance(args[0], ZonedDateTimePeriod):
            return self.start.exact_eq(args[0].start) and self.end.exact_eq(args[0].end)
        if (
            (len(args) == 2)
            and isinstance(args[0], ZonedDateTime)
            and isinstance(args[1], ZonedDateTime)
        ):
            return self.exact_eq(ZonedDateTimePeriod(args[0], args[1]))
        if (
            (len(args) == 3)
            and isinstance(args[0], PlainDateTime)
            and isinstance(args[1], PlainDateTime)
            and isinstance(args[2], ZoneInfo)
        ):
            return self.exact_eq(
                ZonedDateTimePeriod(
                    args[0].assume_tz(args[2].key), args[1].assume_tz(args[2].key)
                )
            )
        raise _PeriodExactEqArgumentsError(args=args)

    def format_compact(self) -> str:
        """Format the period in a compact fashion."""
        fc, start, end = format_compact, self.start, self.end
        if start == end:
            if end.second != 0:
                return f"{fc(start)}="
            if end.minute != 0:
                return f"{fc(start, fmt='%Y%m%dT%H%M')}="
            return f"{fc(start, fmt='%Y%m%dT%H')}="
        if start.date() == end.date():
            if end.second != 0:
                return f"{fc(start.to_plain())}-{fc(end, fmt='%H%M%S')}"
            if end.minute != 0:
                return f"{fc(start.to_plain())}-{fc(end, fmt='%H%M')}"
            return f"{fc(start.to_plain())}-{fc(end, fmt='%H')}"
        if start.date().year_month() == end.date().year_month():
            if end.second != 0:
                return f"{fc(start.to_plain())}-{fc(end, fmt='%dT%H%M%S')}"
            if end.minute != 0:
                return f"{fc(start.to_plain())}-{fc(end, fmt='%dT%H%M')}"
            return f"{fc(start.to_plain())}-{fc(end, fmt='%dT%H')}"
        if start.year == end.year:
            if end.second != 0:
                return f"{fc(start.to_plain())}-{fc(end, fmt='%m%dT%H%M%S')}"
            if end.minute != 0:
                return f"{fc(start.to_plain())}-{fc(end, fmt='%m%dT%H%M')}"
            return f"{fc(start.to_plain())}-{fc(end, fmt='%m%dT%H')}"
        if end.second != 0:
            return f"{fc(start.to_plain())}-{fc(end)}"
        if end.minute != 0:
            return f"{fc(start.to_plain())}-{fc(end, fmt='%Y%m%dT%H%M')}"
        return f"{fc(start.to_plain())}-{fc(end, fmt='%Y%m%dT%H')}"

    @classmethod
    def from_dict(cls, mapping: PeriodDict[_TDateTime_co], /) -> Self:
        """Convert the dictionary to a period."""
        match mapping["start"]:
            case ZonedDateTime() as start:
                ...
            case dt.date() as py_datetime:
                start = ZonedDateTime.from_py_datetime(py_datetime)
            case never:
                assert_never(never)
        match mapping["end"]:
            case ZonedDateTime() as end:
                ...
            case dt.date() as py_datetime:
                end = ZonedDateTime.from_py_datetime(py_datetime)
            case never:
                assert_never(never)
        return cls(start=start, end=end)

    def replace(
        self,
        *,
        start: ZonedDateTime | Sentinel = sentinel,
        end: ZonedDateTime | Sentinel = sentinel,
    ) -> Self:
        """Replace elements of the period."""
        return replace_non_sentinel(self, start=start, end=end)

    @property
    def time_zone(self) -> ZoneInfo:
        """The time zone of the period."""
        return ZoneInfo(self.start.tz)

    def to_dict(self) -> PeriodDict[ZonedDateTime]:
        """Convert the period to a dictionary."""
        return PeriodDict(start=self.start, end=self.end)

    def to_tz(self, time_zone: TimeZoneLike, /) -> Self:
        """Convert the time zone."""
        tz = get_time_zone_name(time_zone)
        return self.replace(start=self.start.to_tz(tz), end=self.end.to_tz(tz))


@dataclass(kw_only=True, slots=True)
class PeriodError(Exception): ...


@dataclass(kw_only=True, slots=True)
class _PeriodInvalidError[T: Date | ZonedDateTime](PeriodError):
    start: T
    end: T

    @override
    def __str__(self) -> str:
        return f"Invalid period; got {self.start} > {self.end}"


@dataclass(kw_only=True, slots=True)
class _PeriodTimeZoneError(PeriodError):
    start: ZoneInfo
    end: ZoneInfo

    @override
    def __str__(self) -> str:
        return f"Period must contain exactly one time zone; got {self.start} and {self.end}"


@dataclass(kw_only=True, slots=True)
class _PeriodExactEqArgumentsError(PeriodError):
    args: tuple[Any, ...]

    @override
    def __str__(self) -> str:
        return f"Invalid arguments; got {self.args}"


__all__ = [
    "DatePeriod",
    "PeriodDict",
    "PeriodError",
    "TimePeriod",
    "ZonedDateTimePeriod",
]
