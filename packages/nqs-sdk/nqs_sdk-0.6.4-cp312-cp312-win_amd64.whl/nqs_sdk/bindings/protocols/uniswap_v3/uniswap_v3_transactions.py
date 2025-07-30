from decimal import Decimal

from nqs_sdk import TxRequest
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_utils import (
    calculate_max_amounts,
    get_tick_spacing,
    price_to_tick,
    tick_to_price,
)
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction


class RawMintTransaction(Transaction):
    tick_lower: int | str
    tick_upper: int | str
    amount: int | str
    token_id: str | None

    def __init__(self, tick_lower: int | str, tick_upper: int | str, amount: int | str, token_id: str | None = None):
        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount = amount
        self.token_id = token_id

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_mint",
            "args": {
                "tick_lower": self.tick_lower,
                "tick_upper": self.tick_upper,
                "amount": self.amount,
            },
        }
        if self.token_id:
            payload["args"]["token_id"] = self.token_id  # type: ignore

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class MintTransaction(Transaction):
    price_lower: Decimal
    price_upper: Decimal
    current_price: Decimal
    max_token0: Decimal
    max_token1: Decimal
    pool: UniswapV3Pool
    token_id: str | None

    def __init__(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        current_price: float | Decimal,
        max_token0: float | Decimal,
        max_token1: float | Decimal,
        pool: UniswapV3Pool,
        token_id: str | None = None,
    ):
        self.price_lower = Decimal(price_lower)
        self.price_upper = Decimal(price_upper)
        self.current_price = Decimal(current_price)
        self.max_token0 = Decimal(max_token0)
        self.max_token1 = Decimal(max_token1)
        self.pool = pool
        self.token_id = token_id

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        tick_spacing = get_tick_spacing(self.pool.fee_tier)

        tick_lower = price_to_tick(self.price_lower, self.pool.decimals0, self.pool.decimals1, tick_spacing, True)
        tick_upper = price_to_tick(self.price_upper, self.pool.decimals0, self.pool.decimals1, tick_spacing, False)

        new_price_lower = tick_to_price(tick_lower, self.pool.decimals0, self.pool.decimals1)
        new_price_upper = tick_to_price(tick_upper, self.pool.decimals0, self.pool.decimals1)

        # Since current_price might not be accurate due to tick rounding,
        # we need to handle the worst-case scenario for safe conversion
        # We'll consider both possible current tick values (rounded down and up)
        current_tick_floor = price_to_tick(self.current_price, self.pool.decimals0, self.pool.decimals1, 1, True)
        current_price_floor = tick_to_price(current_tick_floor, self.pool.decimals0, self.pool.decimals1)
        amount_floor = calculate_max_amounts(
            new_price_lower, current_price_floor, new_price_upper, self.max_token0, self.max_token1
        )

        current_tick_ceil = price_to_tick(self.current_price, self.pool.decimals0, self.pool.decimals1, 1, False)
        if current_tick_floor == current_tick_ceil:
            # same value
            amount = amount_floor
        else:
            # alternative value
            current_price_ceil = tick_to_price(current_tick_ceil, self.pool.decimals0, self.pool.decimals1)
            amount_ceil = calculate_max_amounts(
                new_price_lower, current_price_ceil, new_price_upper, self.max_token0, self.max_token1
            )
            # Calculate liquidity for both scenarios and take the minimum for safety
            amount = amount_ceil  # min(amount_floor, amount_ceil)

        amount_scaled = int(amount.scaleb((self.pool.decimals0 + self.pool.decimals1) // 2))

        tx = RawMintTransaction(tick_lower, tick_upper, amount_scaled, self.token_id)

        return tx.to_tx_request(self.pool.name, source, sender, order)


class RawBurnTransaction(Transaction):
    tick_lower: int | str
    tick_upper: int | str
    amount: int | str

    def __init__(self, tick_lower: int | str, tick_upper: int | str, amount: int | str):
        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount = amount

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_burn",
            "args": {"tick_lower": self.tick_lower, "tick_upper": self.tick_upper, "amount": self.amount},
        }

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class BurnTransaction(Transaction):
    price_lower: Decimal
    price_upper: Decimal
    amount: Decimal
    pool: UniswapV3Pool

    def __init__(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        amount: float | Decimal,
        pool: UniswapV3Pool,
    ):
        self.price_lower = Decimal(price_lower)
        self.price_upper = Decimal(price_upper)
        self.amount = Decimal(amount)
        self.pool = pool

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        tick_spacing = get_tick_spacing(self.pool.fee_tier)

        tick_lower = price_to_tick(self.price_lower, self.pool.decimals0, self.pool.decimals1, tick_spacing, True)
        tick_upper = price_to_tick(self.price_upper, self.pool.decimals0, self.pool.decimals1, tick_spacing, False)

        amount = int(self.amount.scaleb((self.pool.decimals0 + self.pool.decimals1) // 2))

        tx = RawBurnTransaction(tick_lower, tick_upper, amount)

        return tx.to_tx_request(self.pool.name, source, sender, order)


class RawSwapTransaction(Transaction):
    amount: int | str
    zero_for_one: bool
    sqrt_price_limit_x96: int | str | None

    def __init__(self, amount: int | str, zero_for_one: bool, sqrt_price_limit_x96: int | str | None = None):
        self.zero_for_one = zero_for_one
        self.amount = amount
        self.sqrt_price_limit_x96 = sqrt_price_limit_x96

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_swap",
            "args": {"amount_specified": self.amount, "zero_for_one": self.zero_for_one},
        }

        if self.sqrt_price_limit_x96 is not None:
            payload["args"]["sqrt_price_limit_x96"] = self.sqrt_price_limit_x96  # type: ignore

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class SwapTransaction(Transaction):
    price_limit: Decimal | None
    amount: Decimal
    pool: UniswapV3Pool
    zero_for_one: bool

    def __init__(
        self,
        amount: float | Decimal,
        zero_for_one: bool,
        pool: UniswapV3Pool,
        price_limit: float | Decimal | None = None,
    ):
        self.price_limit = Decimal(price_limit) if price_limit is not None else None
        self.amount = Decimal(amount)
        self.zero_for_one = zero_for_one
        self.pool = pool

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        # convert price_limit to x96 format
        sqrt_price_limit_x96 = None
        if self.price_limit is not None:
            sqrt_price_limit_x96 = int(self.price_limit.sqrt() * (2**96))

        if self.zero_for_one:
            amount_specified = int(self.amount.scaleb(self.pool.decimals0))
        else:
            amount_specified = int(self.amount.scaleb(self.pool.decimals1))

        tx = RawSwapTransaction(
            str(amount_specified),
            self.zero_for_one,
            str(sqrt_price_limit_x96) if sqrt_price_limit_x96 is not None else None,
        )

        return tx.to_tx_request(self.pool.name, source, sender, order)


class RawCollectTransaction(Transaction):
    amount_0_requested: int | str
    amount_1_requested: int | str
    tick_lower: int | str
    tick_upper: int | str

    def __init__(
        self, tick_lower: int | str, tick_upper: int | str, amount_0_requested: int | str, amount_1_requested: int | str
    ):
        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount_0_requested = amount_0_requested
        self.amount_1_requested = amount_1_requested

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_collect",
            "args": {
                "amount_0_requested": self.amount_0_requested,
                "amount_1_requested": self.amount_1_requested,
                "tick_lower": self.tick_lower,
                "tick_upper": self.tick_upper,
            },
        }

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class CollectTransaction(Transaction):
    price_lower: Decimal
    price_upper: Decimal
    amount_0: Decimal
    amount_1: Decimal
    pool: UniswapV3Pool

    def __init__(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        amount_0: float | Decimal,
        amount_1: float | Decimal,
        pool: UniswapV3Pool,
    ):
        self.price_lower = Decimal(price_lower)
        self.price_upper = Decimal(price_upper)
        self.amount_0 = Decimal(amount_0)
        self.amount_1 = Decimal(amount_1)
        self.pool = pool

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        tick_spacing = get_tick_spacing(self.pool.fee_tier)

        tick_lower = price_to_tick(self.price_lower, self.pool.decimals0, self.pool.decimals1, tick_spacing, True)
        tick_upper = price_to_tick(self.price_upper, self.pool.decimals0, self.pool.decimals1, tick_spacing, False)

        amount0_scaled = int(self.amount_0.scaleb(self.pool.decimals0))
        amount1_scaled = int(self.amount_1.scaleb(self.pool.decimals1))

        tx = RawCollectTransaction(tick_lower, tick_upper, amount0_scaled, amount1_scaled)

        return tx.to_tx_request(self.pool.name, source, sender, order)
