"""Math module for FlexFloat, similar to Python's math module.

This module provides mathematical functions that operate on FlexFloat instances,
mirroring the interface of Python's built-in math module where possible.
Most functions are designed to work with FlexFloat objects, enabling arbitrary-precision
floating-point arithmetic.

Example:
    from flexfloat.math import sqrt, exp, pow
    from flexfloat import FlexFloat
    a = FlexFloat.from_float(2.0)
    b = sqrt(a)
    print(b)
    # Output: FlexFloat(...)
"""

import math
from typing import Final, Iterable

from .core import FlexFloat

# Constants
e: Final[FlexFloat] = FlexFloat.from_float(math.e)
"""The mathematical constant e (Euler's number) as a FlexFloat."""
pi: Final[FlexFloat] = FlexFloat.from_float(math.pi)
"""The mathematical constant pi as a FlexFloat."""
inf: Final[FlexFloat] = FlexFloat.infinity()
"""Positive infinity as a FlexFloat."""
nan: Final[FlexFloat] = FlexFloat.nan()
"""Not-a-Number (NaN) as a FlexFloat."""
tau: Final[FlexFloat] = FlexFloat.from_float(math.tau)
"""The mathematical constant tau (2*pi) as a FlexFloat."""

_0_5: Final[FlexFloat] = FlexFloat.from_float(0.5)
"""The FlexFloat representation of 0.5."""
_1: Final[FlexFloat] = FlexFloat.from_float(1.0)
"""The FlexFloat representation of 1.0."""
_2: Final[FlexFloat] = FlexFloat.from_float(2.0)
"""The FlexFloat representation of 2.0."""
_10: Final[FlexFloat] = FlexFloat.from_float(10.0)
"""The FlexFloat representation of 10.0."""


def exp(x: FlexFloat) -> FlexFloat:
    """Return e raised to the power of x (where x is a FlexFloat).

    Args:
        x (FlexFloat): The exponent value.

    Returns:
        FlexFloat: The value of e**x as a FlexFloat.
    """
    return e**x


def pow(base: FlexFloat, exp: FlexFloat) -> FlexFloat:
    """Return base raised to the power of exp (both are FlexFloat instances).

    Args:
        base (FlexFloat): The base value.
        exp (FlexFloat): The exponent value.

    Returns:
        FlexFloat: The value of base**exp as a FlexFloat.
    """
    return base**exp


def copysign(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return a FlexFloat with the magnitude of x and the sign of y.

    Args:
        x (FlexFloat): The value whose magnitude is used.
        y (FlexFloat): The value whose sign is used.

    Returns:
        FlexFloat: A FlexFloat with the magnitude of x and the sign of y.
    """
    result = x.copy()
    result.sign = y.sign
    return result


def fabs(x: FlexFloat) -> FlexFloat:
    """Return the absolute value of x.

    Args:
        x (FlexFloat): The value to get the absolute value of.

    Returns:
        FlexFloat: The absolute value of x.
    """
    return abs(x)


def isinf(x: FlexFloat) -> bool:
    """Check if x is positive or negative infinity.

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is infinity, False otherwise.
    """
    return x.is_infinity()


def isnan(x: FlexFloat) -> bool:
    """Check if x is NaN (not a number).

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is NaN, False otherwise.
    """
    return x.is_nan()


def isfinite(x: FlexFloat) -> bool:
    """Check if x is neither an infinity nor NaN.

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is finite, False otherwise.
    """
    return not x.is_infinity() and not x.is_nan()


def sqrt(x: FlexFloat) -> FlexFloat:
    """Return the square root of x (using power operator).

    Args:
        x (FlexFloat): The value to compute the square root of.

    Returns:
        FlexFloat: The square root of x.
    """
    return x**_0_5


# Unimplemented functions
def acos(x: FlexFloat) -> FlexFloat:
    """Return the arc cosine of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the arc cosine of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("acos is not implemented for FlexFloat.")


def acosh(x: FlexFloat) -> FlexFloat:
    """Return the hyperbolic arc cosine of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the hyperbolic arc cosine of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("acosh is not implemented for FlexFloat.")


def asin(x: FlexFloat) -> FlexFloat:
    """Return the arc sine of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the arc sine of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("asin is not implemented for FlexFloat.")


def asinh(x: FlexFloat) -> FlexFloat:
    """Return the hyperbolic arc sine of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the hyperbolic arc sine of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("asinh is not implemented for FlexFloat.")


def atan(x: FlexFloat) -> FlexFloat:
    """Return the arc tangent of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the arc tangent of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("atan is not implemented for FlexFloat.")


def atan2(y: FlexFloat, x: FlexFloat) -> FlexFloat:
    """Return the arc tangent of y/x (not implemented).

    Args:
        y (FlexFloat): The numerator value.
        x (FlexFloat): The denominator value.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("atan2 is not implemented for FlexFloat.")


def atanh(x: FlexFloat) -> FlexFloat:
    """Return the hyperbolic arc tangent of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the hyperbolic arc tangent of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("atanh is not implemented for FlexFloat.")


def cbrt(x: FlexFloat) -> FlexFloat:
    """Return the cube root of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the cube root of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("cbrt is not implemented for FlexFloat.")


def ceil(x: FlexFloat) -> FlexFloat:
    """Return the ceiling of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the ceiling of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("ceil is not implemented for FlexFloat.")


# Not implemented functions
def dist(p: Iterable[FlexFloat], q: Iterable[FlexFloat]) -> FlexFloat:
    """Return the Euclidean distance between two points p and q (not implemented).

    Args:
        p (Iterable[FlexFloat]): The first point coordinates.
        q (Iterable[FlexFloat]): The second point coordinates.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("dist is not implemented for FlexFloat.")


def erf(x: FlexFloat) -> FlexFloat:
    """Return the error function of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the error function of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("erf is not implemented for FlexFloat.")


def erfc(x: FlexFloat) -> FlexFloat:
    """Return the complementary error function of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the complementary error function of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("erfc is not implemented for FlexFloat.")


def expm1(x: FlexFloat) -> FlexFloat:
    """Return e raised to the power of x, minus 1 (not implemented).

    Args:
        x (FlexFloat): The exponent value.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("expm1 is not implemented for FlexFloat.")


def factorial(x: FlexFloat) -> FlexFloat:
    """Return the factorial of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the factorial of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("factorial is not implemented for FlexFloat.")


def fmod(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return the remainder of x divided by y (not implemented).

    Args:
        x (FlexFloat): The dividend value.
        y (FlexFloat): The divisor value.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("fmod is not implemented for FlexFloat.")


def frexp(x: FlexFloat) -> tuple[FlexFloat, int]:
    """Return the mantissa and exponent of x (not implemented).

    Args:
        x (FlexFloat): The value to decompose into mantissa and exponent.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("frexp is not implemented for FlexFloat.")


def fsum(seq: Iterable[FlexFloat]) -> FlexFloat:
    """Return an accurate floating-point sum of the values in seq (not implemented).

    Args:
        seq (Iterable[FlexFloat]): The sequence of values to sum.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("fsum is not implemented for FlexFloat.")


def gamma(x: FlexFloat) -> FlexFloat:
    """Return the gamma function of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the gamma function of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("gamma is not implemented for FlexFloat.")


def gcd(*integers: FlexFloat) -> FlexFloat:
    """Return the greatest common divisor of the integers (not implemented).

    Args:
        *integers (FlexFloat): The integers to compute the gcd of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("gcd is not implemented for FlexFloat.")


def hypot(*coordinates: FlexFloat) -> FlexFloat:
    """Return the Euclidean norm, sqrt(x1*x1 + x2*x2 + ... + xn*xn)
    (not implemented).

    Args:
        *coordinates (FlexFloat): The coordinates to compute the norm of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("hypot is not implemented for FlexFloat.")


def isclose(
    a: FlexFloat,
    b: FlexFloat,
    *,
    rel_tol: FlexFloat = FlexFloat.from_float(1e-09),
    abs_tol: FlexFloat = FlexFloat.from_float(0.0),
) -> bool:
    """Check if two FlexFloat instances are close in value (not implemented).

    Args:
        a (FlexFloat): The first value to compare.
        b (FlexFloat): The second value to compare.
        rel_tol (FlexFloat, optional): The relative tolerance. Defaults to 1e-09.
        abs_tol (FlexFloat, optional): The absolute tolerance. Defaults to 0.0.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("isclose is not implemented for FlexFloat.")


def lcm(*integers: FlexFloat) -> FlexFloat:
    """Return the least common multiple of the integers (not implemented).

    Args:
        *integers (FlexFloat): The integers to compute the lcm of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("lcm is not implemented for FlexFloat.")


def ldexp(x: FlexFloat, i: int) -> FlexFloat:
    """Return x * (2**i) (not implemented).

    Args:
        x (FlexFloat): The value to scale.
        i (int): The exponent value.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("ldexp is not implemented for FlexFloat.")


def lgamma(x: FlexFloat) -> FlexFloat:
    """Return the natural logarithm of the absolute value of the gamma function of x
    (not implemented).

    Args:
        x (FlexFloat): The value to compute the natural logarithm of the gamma
          function of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("lgamma is not implemented for FlexFloat.")


def _ln_taylor_series(
    x: FlexFloat,
    max_iterations: int = 100,
    tolerance: FlexFloat = FlexFloat.from_float(1e-16),
) -> FlexFloat:
    """Compute the natural logarithm of x using a fast-converging Taylor series.

    Uses the identity:
        ln(x) = 2 * artanh((x-1)/(x+1))
    where artanh(y) = y + y³/3 + y⁵/5 + ... for |y| < 1.
    This converges rapidly for x near 1 (i.e., 0 < x ≤ 2).

    Args:
        x (FlexFloat): The input value (should be close to 1 for best convergence).
        max_iterations (int): Maximum number of terms in the series.
        tolerance (FlexFloat): Convergence tolerance.

    Returns:
        FlexFloat: The natural logarithm of x.
    """
    x_minus_1 = x - _1
    x_plus_1 = x + _1

    # Check for division by zero
    if x_plus_1.is_zero():
        return FlexFloat.nan()

    y = x_minus_1 / x_plus_1
    tolerance = tolerance.abs()

    # Initialize series: artanh(y) = y + y³/3 + y⁵/5 + ...
    result = y.copy()
    y_squared = y * y
    term = y.copy()

    for n in range(1, max_iterations):
        # Calculate next term: y^(2n+1) / (2n+1)
        term *= y_squared
        term_contribution = term / (2 * n + 1)
        result += term_contribution

        # Check for convergence (compare absolute values)
        if term_contribution.abs() < tolerance:
            break

    # Return 2 * artanh((x-1)/(x+1))
    return _2 * result


def _ln_range_reduction(x: FlexFloat) -> FlexFloat:
    """Compute natural logarithm using range reduction to improve convergence.

    Uses different strategies based on the magnitude of x:
    - For values near 1: direct Taylor series
    - For large values: iterative square roots
    - For small values: use ln(x) = -ln(1/x)

    Args:
        x (FlexFloat): The input value (must be positive).

    Returns:
        FlexFloat: The natural logarithm of x.
    """
    # For very small values, use ln(x) = -ln(1/x)
    if x < 0.1:
        reciprocal = _1 / x
        return -_ln_range_reduction(reciprocal)

    # For values close to 1, use direct Taylor series
    if x <= 2.0:
        return _ln_taylor_series(x)

    # For large values, use iterative square roots
    multiplier = _1

    max_reductions = 30
    for _ in range(max_reductions):
        if x <= 2.0:
            break
        x = sqrt(x)
        multiplier = multiplier * _2

    # Compute ln(current_x) using Taylor series
    ln_result = _ln_taylor_series(x)

    # Apply the multiplier
    return multiplier * ln_result


def log(x: FlexFloat, base: FlexFloat = e) -> FlexFloat:
    """Return the logarithm of x to the given base using Taylor series.

    Args:
        x (FlexFloat): The value to compute the logarithm of.
        base (FlexFloat, optional): The base of the logarithm. Defaults to e.

    Returns:
        FlexFloat: The logarithm of x to the given base.

    Raises:
        ValueError: If x is negative or zero, or if base is invalid.
    """
    # Handle special cases
    if x.is_nan() or base.is_nan():
        return FlexFloat.nan()

    if x.is_zero() or x.sign:  # x <= 0
        return FlexFloat.nan()

    if x.is_infinity():
        return FlexFloat.infinity(sign=False)

    # Handle base special cases
    if base.is_zero() or base.sign or base.is_infinity():
        return FlexFloat.nan()

    # Check if base is 1 (which would make logarithm undefined)
    if abs(base - 1.0) < 1e-15:
        return FlexFloat.nan()

    # If x is 1, log of any valid base is 0
    if abs(x - 1.0) < 1e-15:
        return FlexFloat.zero()

    # Compute natural logarithm using range reduction and Taylor series
    ln_x = _ln_range_reduction(x)

    # If base is e (natural logarithm), return directly
    if abs(base - math.e) < 1e-15:
        return ln_x

    # For other bases, use change of base formula: log_base(x) = ln(x) / ln(base)
    ln_base = _ln_range_reduction(base)
    return ln_x / ln_base


def log10(x: FlexFloat) -> FlexFloat:
    """Return the base-10 logarithm of x using Taylor series.

    Args:
        x (FlexFloat): The value to compute the base-10 logarithm of.

    Returns:
        FlexFloat: The base-10 logarithm of x.

    Raises:
        ValueError: If x is negative or zero.
    """
    return log(x, _10)


def log1p(x: FlexFloat) -> FlexFloat:
    """Return the natural logarithm of 1 + x using Taylor series.

    This function is more accurate than log(1 + x) for values of x close to zero.

    Args:
        x (FlexFloat): The value to compute the natural logarithm of 1 + x.

    Returns:
        FlexFloat: The natural logarithm of 1 + x.

    Raises:
        ValueError: If 1 + x is negative or zero.
    """
    # Handle special cases
    if x.is_nan():
        return FlexFloat.nan()

    # Check if 1 + x would be <= 0
    one_plus_x = _1 + x
    if one_plus_x.is_zero() or one_plus_x.sign:
        return FlexFloat.nan()

    if one_plus_x.is_infinity():
        return FlexFloat.infinity(sign=False)

    # For small x, use Taylor series directly: ln(1+x) = x - x²/2 + x³/3 - ...
    if abs(x) < 0.5:  # Direct Taylor series for better accuracy
        return _ln_taylor_series(one_plus_x)

    # For larger x, use the regular log function
    return log(one_plus_x)


def log2(x: FlexFloat) -> FlexFloat:
    """Return the base-2 logarithm of x using Taylor series.

    Args:
        x (FlexFloat): The value to compute the base-2 logarithm of.

    Returns:
        FlexFloat: The base-2 logarithm of x.

    Raises:
        ValueError: If x is negative or zero.
    """
    return log(x, _2)


def modf(x: FlexFloat) -> tuple[FlexFloat, FlexFloat]:
    """Return the fractional and integer parts of x (not implemented).

    Args:
        x (FlexFloat): The value to split into fractional and integer parts.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("modf is not implemented for FlexFloat.")


def nextafter(x: FlexFloat, y: FlexFloat, *, steps: int | None = None) -> FlexFloat:
    """Return the next representable FlexFloat value after x towards y
    (not implemented).

    Args:
        x (FlexFloat): The starting value.
        y (FlexFloat): The target value.
        steps (int | None, optional): The number of steps to take. Defaults to None.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("nextafter is not implemented for FlexFloat.")


def perm(n: FlexFloat, k: FlexFloat | None = None) -> FlexFloat:
    """Return the number of ways to choose k items from n items without repetition
    (not implemented).

    Args:
        n (FlexFloat): The total number of items.
        k (FlexFloat | None, optional): The number of items to choose. Defaults to None.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("perm is not implemented for FlexFloat.")


def radians(x: FlexFloat) -> FlexFloat:
    """Convert angle x from degrees to radians (not implemented).

    Args:
        x (FlexFloat): The angle in degrees.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("radians is not implemented for FlexFloat.")


def remainder(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return the remainder of x divided by y (not implemented).

    Args:
        x (FlexFloat): The dividend value.
        y (FlexFloat): The divisor value.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("remainder is not implemented for FlexFloat.")


def sin(x: FlexFloat) -> FlexFloat:
    """Return the sine of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the sine of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("sin is not implemented for FlexFloat.")


def sinh(x: FlexFloat) -> FlexFloat:
    """Return the hyperbolic sine of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the hyperbolic sine of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("sinh is not implemented for FlexFloat.")


def tan(x: FlexFloat) -> FlexFloat:
    """Return the tangent of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the tangent of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("tan is not implemented for FlexFloat.")


def tanh(x: FlexFloat) -> FlexFloat:
    """Return the hyperbolic tangent of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the hyperbolic tangent of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("tanh is not implemented for FlexFloat.")


def trunc(x: FlexFloat) -> FlexFloat:
    """Return the integer part of x (not implemented).

    Args:
        x (FlexFloat): The value to truncate.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("trunc is not implemented for FlexFloat.")


def ulp(x: FlexFloat) -> FlexFloat:
    """Return the value of the least significant bit of x (not implemented).

    Args:
        x (FlexFloat): The value to compute the least significant bit of.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("ulp is not implemented for FlexFloat.")


def fma(x: FlexFloat, y: FlexFloat, z: FlexFloat) -> FlexFloat:
    """Return x * y + z (not implemented).

    Args:
        x (FlexFloat): The first multiplicand.
        y (FlexFloat): The second multiplicand.
        z (FlexFloat): The value to add to the product.

    Raises:
        NotImplementedError: Always, as this function is not implemented.
    """
    raise NotImplementedError("fma is not implemented for FlexFloat.")
