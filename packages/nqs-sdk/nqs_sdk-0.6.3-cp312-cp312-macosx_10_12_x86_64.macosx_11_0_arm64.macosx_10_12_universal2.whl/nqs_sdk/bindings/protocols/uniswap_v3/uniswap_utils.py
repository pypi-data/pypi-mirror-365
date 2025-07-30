import math
from decimal import Decimal


# Maximum tick value for Uniswap V3 pools
MAX_TICK = 887272


class InvalidPriceError(ValueError):
    """Raised when price value is invalid (not strictly positive and finite)."""

    pass


def price_to_tick(price: Decimal, decimals0: int, decimals1: int, tick_spacing: int = 1, lower: bool = True) -> int:
    """
    Convert a price to a tick value for Uniswap V3.

    Args:
        price: The price to convert (must be strictly positive and finite)
        decimals0: Number of decimals for token0
        decimals1: Number of decimals for token1
        tick_spacing: Spacing between valid ticks (default: 1)
        lower: Whether to round down (True) or up (False) when between ticks

    Returns:
        The corresponding tick value

    Raises:
        InvalidPriceError: When the price is not strictly positive and finite
                          (e.g., negative, zero, infinity, or NaN)
    """
    # Validate that price is strictly positive and finite
    if price <= 0 or not price.is_finite():
        raise InvalidPriceError(f"Price must be strictly positive and finite, got: {price}")

    # Compute tick as log base sqrt(1.0001) of sqrt_price
    ic = price.scaleb(decimals1 - decimals0).sqrt().ln() / Decimal("1.0001").sqrt().ln()

    if lower:
        tick = max(math.floor(round(ic) / tick_spacing) * tick_spacing, -MAX_TICK)
    else:
        tick = min(math.ceil(round(ic) / tick_spacing) * tick_spacing, MAX_TICK)

    return tick


def tick_to_price(tick: int, decimals0: int, decimals1: int) -> Decimal:
    return (Decimal(1.0001) ** tick).scaleb(-(decimals1 - decimals0))


def price_to_sqrtp(p: Decimal) -> int:
    return int(p.sqrt() * Decimal("2") ** 96)


def calculate_max_amounts(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, amount0: Decimal, amount1: Decimal
) -> Decimal:
    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    assert sqrt_price_lower < sqrt_price_upper

    if sqrt_price <= sqrt_price_lower:
        liquidity = amount0 / (1 / sqrt_price_lower - 1 / sqrt_price_upper)
    elif sqrt_price <= sqrt_price_upper:
        liquidity_0 = amount0 / (1 / sqrt_price - 1 / sqrt_price_upper)
        liquidity_1 = amount1 / (sqrt_price - sqrt_price_lower)
        liquidity = min(liquidity_0, liquidity_1)
    else:
        liquidity = amount1 / (sqrt_price_upper - sqrt_price_lower)

    return liquidity


def calculate_optimal_rebalancing(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, amount0: Decimal, amount1: Decimal
) -> tuple[Decimal, Decimal]:
    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    x_unit = (sqrt_price_upper - sqrt_price) / (sqrt_price * sqrt_price_upper)
    y_unit = sqrt_price - sqrt_price_lower

    v_wallet = amount0 * price + amount1
    v_unit = x_unit * price + y_unit
    n_units = v_wallet / v_unit

    x_pos = n_units * x_unit
    y_pos = n_units * y_unit

    return x_pos, y_pos
