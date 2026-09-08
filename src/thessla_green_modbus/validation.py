"""Write validators also expose application-independent value metadata."""

import math
from dataclasses import dataclass
from enum import IntEnum


@dataclass(frozen=True, slots=True)
class NumberRange:
    """Validate physical units without clamping, truncating or coercing strings."""

    minimum: float
    maximum: float
    step: float = 1.0

    def __post_init__(self) -> None:
        if (
            not all(math.isfinite(v) for v in (self.minimum, self.maximum, self.step))
            or self.minimum > self.maximum
            or self.step <= 0
        ):
            raise ValueError("Invalid numeric range")

    def __call__(self, value: object) -> int | float:
        if type(value) not in (int, float):
            raise ValueError("Expected a number, not a boolean, enum or string")
        # This narrowing is for static type checkers; the exact type was checked.
        assert isinstance(value, (int, float))
        if not self.minimum <= value <= self.maximum:
            raise ValueError(f"Expected {self.minimum} <= value <= {self.maximum}")
        steps = (value - self.minimum) / self.step
        if not math.isclose(steps, round(steps), rel_tol=0.0, abs_tol=1e-9):
            raise ValueError(f"Expected a multiple of step {self.step}")
        return value


@dataclass(frozen=True, slots=True)
class EnumValues[E: IntEnum]:
    """Reject unknown codes and unrelated enum classes before any I/O."""

    enum_type: type[E]

    def __call__(self, value: object) -> E:
        if type(value) is not int and not isinstance(value, self.enum_type):
            raise ValueError(f"Expected {self.enum_type.__name__} or an integer code")
        assert isinstance(value, int)
        return self.enum_type(value)


def boolean_value(value: object) -> bool:
    """Require an actual boolean; bool('false') must never switch a device on."""
    if not isinstance(value, bool):
        raise ValueError("Expected True or False")
    return value
