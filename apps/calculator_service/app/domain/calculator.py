from decimal import Decimal

from .errors import DivideByZeroError

# ---------------------------------------------------------------------------
# Pure arithmetic functions.
#
# Rules:
#   - Use Decimal for all arithmetic — never float.
#     Float cannot represent all decimal numbers exactly (0.1 + 0.2 != 0.3).
#     Decimal is exact, which is what a calculator must be.
#   - No eval(), exec(), or any dynamic code execution — ever.
#     eval() would let a caller inject arbitrary Python code.
#   - Each function does exactly one thing.
#   - Typed domain errors, not raw Python exceptions.
# ---------------------------------------------------------------------------


def add(a: Decimal, b: Decimal) -> Decimal:
    """Return the sum of a and b."""
    return a + b


def subtract(a: Decimal, b: Decimal) -> Decimal:
    """Return a minus b."""
    return a - b


def multiply(a: Decimal, b: Decimal) -> Decimal:
    """Return a multiplied by b."""
    return a * b


def divide(a: Decimal, b: Decimal) -> Decimal:
    """
    Return a divided by b.

    Raises DivideByZeroError if b is zero.
    We raise a typed domain error rather than letting Python's ZeroDivisionError
    bubble up — this keeps the API layer independent of Python internals.
    """
    if b == Decimal("0"):
        raise DivideByZeroError()
    return a / b
