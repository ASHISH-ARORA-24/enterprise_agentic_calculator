from decimal import Decimal

import pytest
from app.domain.calculator import add, divide, multiply, subtract
from app.domain.errors import DIVIDE_BY_ZERO, DivideByZeroError

# ---------------------------------------------------------------------------
# Addition
# ---------------------------------------------------------------------------


def test_add_positive_numbers() -> None:
    assert add(Decimal("2"), Decimal("3")) == Decimal("5")


def test_add_negative_numbers() -> None:
    assert add(Decimal("-4"), Decimal("-6")) == Decimal("-10")


def test_add_mixed_sign() -> None:
    assert add(Decimal("-3"), Decimal("7")) == Decimal("4")


def test_add_decimal_precision() -> None:
    # With float: 0.1 + 0.2 = 0.30000000000000004 (wrong)
    # With Decimal: 0.1 + 0.2 = 0.3 (correct)
    assert add(Decimal("0.1"), Decimal("0.2")) == Decimal("0.3")


def test_add_large_numbers() -> None:
    assert add(Decimal("999999999"), Decimal("1")) == Decimal("1000000000")


# ---------------------------------------------------------------------------
# Subtraction
# ---------------------------------------------------------------------------


def test_subtract_positive_numbers() -> None:
    assert subtract(Decimal("10"), Decimal("4")) == Decimal("6")


def test_subtract_results_in_negative() -> None:
    assert subtract(Decimal("3"), Decimal("7")) == Decimal("-4")


def test_subtract_negative_from_positive() -> None:
    assert subtract(Decimal("5"), Decimal("-3")) == Decimal("8")


# ---------------------------------------------------------------------------
# Multiplication
# ---------------------------------------------------------------------------


def test_multiply_positive_numbers() -> None:
    assert multiply(Decimal("6"), Decimal("7")) == Decimal("42")


def test_multiply_by_zero() -> None:
    assert multiply(Decimal("999"), Decimal("0")) == Decimal("0")


def test_multiply_negative_numbers() -> None:
    assert multiply(Decimal("-3"), Decimal("-4")) == Decimal("12")


def test_multiply_positive_and_negative() -> None:
    assert multiply(Decimal("5"), Decimal("-3")) == Decimal("-15")


def test_multiply_decimal_precision() -> None:
    assert multiply(Decimal("0.1"), Decimal("0.2")) == Decimal("0.02")


# ---------------------------------------------------------------------------
# Division
# ---------------------------------------------------------------------------


def test_divide_even() -> None:
    assert divide(Decimal("10"), Decimal("2")) == Decimal("5")


def test_divide_with_remainder() -> None:
    assert divide(Decimal("10"), Decimal("4")) == Decimal("2.5")


def test_divide_negative() -> None:
    assert divide(Decimal("-10"), Decimal("2")) == Decimal("-5")


def test_divide_both_negative() -> None:
    assert divide(Decimal("-10"), Decimal("-2")) == Decimal("5")


# ---------------------------------------------------------------------------
# Divide by zero — must raise a typed DivideByZeroError
# ---------------------------------------------------------------------------


def test_divide_by_zero_raises_domain_error() -> None:
    with pytest.raises(DivideByZeroError):
        divide(Decimal("5"), Decimal("0"))


def test_divide_by_zero_has_correct_error_code() -> None:
    # The error code must be exactly DIVIDE_BY_ZERO — the API layer
    # depends on this to return the right response to the client.
    with pytest.raises(DivideByZeroError) as exc_info:
        divide(Decimal("5"), Decimal("0"))
    assert exc_info.value.code == DIVIDE_BY_ZERO


def test_divide_by_zero_has_message() -> None:
    with pytest.raises(DivideByZeroError) as exc_info:
        divide(Decimal("5"), Decimal("0"))
    assert exc_info.value.message != ""
