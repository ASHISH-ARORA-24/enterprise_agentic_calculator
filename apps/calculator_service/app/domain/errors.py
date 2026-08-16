from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Error codes — string constants used across the whole service.
#
# Why constants instead of raw strings?
# If we type "DIVIDE_BY_ZERO" in ten places and later rename it, we have to
# find and change all ten. With a constant, we change it in one place.
# Also, typos in a constant name cause an immediate NameError — a typo in a
# string silently produces wrong behaviour.
# ---------------------------------------------------------------------------

DIVIDE_BY_ZERO = "DIVIDE_BY_ZERO"
INVALID_OPERATION = "INVALID_OPERATION"
CALCULATOR_UNAVAILABLE = "CALCULATOR_UNAVAILABLE"
SIMULATED_FAILURE = "SIMULATED_FAILURE"
TOOL_TIMEOUT = "TOOL_TIMEOUT"


# ---------------------------------------------------------------------------
# Domain exceptions — typed errors raised by domain logic.
#
# We define our own exceptions instead of letting Python's built-in exceptions
# bubble up. This keeps the API layer independent of Python internals and makes
# error handling predictable.
# ---------------------------------------------------------------------------


@dataclass
class DomainError(Exception):
    """Base class for all calculator domain errors."""

    code: str
    message: str


@dataclass
class DivideByZeroError(DomainError):
    """Raised when a division by zero is attempted."""

    code: str = DIVIDE_BY_ZERO
    message: str = "Cannot divide by zero"


@dataclass
class InvalidOperationError(DomainError):
    """Raised when an unsupported operation is requested."""

    code: str = INVALID_OPERATION
    message: str = "Operation is not supported"
