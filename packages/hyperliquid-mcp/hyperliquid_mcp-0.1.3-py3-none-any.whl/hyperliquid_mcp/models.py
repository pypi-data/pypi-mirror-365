"""Pydantic models for Hyperliquid MCP server - Request validation only."""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class OrderType(str, Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    TRIGGER = "trigger"


class TimeInForce(str, Enum):
    """Time in force enumeration."""

    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate Or Cancel
    ALO = "ALO"  # Add Liquidity Only


class CandleInterval(str, Enum):
    """Candle interval enumeration."""

    ONE_MINUTE = "1m"
    THREE_MINUTES = "3m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    EIGHT_HOURS = "8h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    THREE_DAYS = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


# Request Models - Only for input validation
class PlaceOrderRequest(BaseModel):
    """Request model for placing orders."""

    asset: str = Field(..., description="Asset symbol (e.g., 'BTC', 'ETH')")
    is_buy: bool = Field(..., description="True for buy order, False for sell order")
    size: float = Field(..., gt=0, description="Order size/quantity")
    order_type: OrderType = Field(default=OrderType.MARKET, description="Order type")
    price: Optional[float] = Field(
        None, gt=0, description="Order price (required for limit/trigger)"
    )
    time_in_force: TimeInForce = Field(
        default=TimeInForce.GTC, description="Time in force"
    )
    reduce_only: bool = Field(
        default=False, description="Whether this is a reduce-only order"
    )
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")

    @model_validator(mode="after")
    def validate_price_for_order_type(self):
        """Validate price is provided for limit/trigger orders."""
        if (
            self.order_type in [OrderType.LIMIT, OrderType.TRIGGER]
            and self.price is None
        ):
            raise ValueError(f"Price is required for {self.order_type} orders")
        return self


class CancelOrderRequest(BaseModel):
    """Request model for canceling orders."""

    asset: str = Field(..., description="Asset symbol")
    order_id: int = Field(..., description="Order ID to cancel")


class ModifyOrderRequest(BaseModel):
    """Request model for modifying orders."""

    asset: str = Field(..., description="Asset symbol")
    order_id: int = Field(..., description="Order ID to modify")
    new_price: Optional[float] = Field(None, gt=0, description="New order price")
    new_size: Optional[float] = Field(None, gt=0, description="New order size")
    new_time_in_force: Optional[TimeInForce] = Field(
        None, description="New time in force"
    )

    @model_validator(mode="after")
    def at_least_one_field(self):
        """Ensure at least one field is provided for modification."""
        if all(
            field is None
            for field in [self.new_price, self.new_size, self.new_time_in_force]
        ):
            raise ValueError(
                "At least one parameter (new_price, new_size, or new_time_in_force) must be provided"
            )
        return self


class BulkCancelRequest(BaseModel):
    """Request model for bulk order cancellation."""

    orders: List[Dict[str, Union[str, int]]] = Field(
        ..., description="List of orders to cancel with 'asset' and 'order_id' fields"
    )

    @field_validator("orders")
    @classmethod
    def validate_orders(cls, v):
        """Validate order format."""
        for order in v:
            if not isinstance(order, dict):
                raise ValueError("Each order must be a dictionary")
            if "asset" not in order or "order_id" not in order:
                raise ValueError("Each order must have 'asset' and 'order_id' fields")
        return v


class UpdateLeverageRequest(BaseModel):
    """Request model for updating leverage."""

    asset: str = Field(..., description="Asset symbol")
    leverage: float = Field(..., gt=0, le=100, description="New leverage value")
    is_isolated: bool = Field(
        default=True, description="Whether to use isolated margin"
    )


class TransferRequest(BaseModel):
    """Request model for transfers."""

    amount: float = Field(..., gt=0, description="Amount to transfer")
    to_perp: bool = Field(
        ..., description="True to transfer from spot to perp, False for perp to spot"
    )


class UsdTransferRequest(BaseModel):
    """Request model for USD transfers."""

    destination: str = Field(..., description="Destination wallet address")
    amount: float = Field(..., gt=0, description="Amount of USDC to transfer")

    @field_validator("destination")
    @classmethod
    def validate_ethereum_address(cls, v):
        """Basic Ethereum address validation."""
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid Ethereum address format")
        return v


class WithdrawRequest(BaseModel):
    """Request model for withdrawals."""

    destination: str = Field(
        ..., description="Destination wallet address for withdrawal"
    )
    amount: float = Field(
        ...,
        gt=1.0,
        description="Amount of USDC to withdraw (minimum $1.01 due to $1 fee)",
    )

    @field_validator("destination")
    @classmethod
    def validate_ethereum_address(cls, v):
        """Basic Ethereum address validation."""
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid Ethereum address format")
        return v


class SubAccountTransferRequest(BaseModel):
    """Request model for sub-account transfers."""

    sub_account: str = Field(..., description="Sub-account address")
    amount: float = Field(..., gt=0, description="Amount to transfer")
    is_deposit: bool = Field(
        ..., description="True to deposit to sub-account, False to withdraw"
    )

    @field_validator("sub_account")
    @classmethod
    def validate_ethereum_address(cls, v):
        """Basic Ethereum address validation."""
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid Ethereum address format")
        return v


class GetCandleDataRequest(BaseModel):
    """Request model for candle data."""

    asset: str = Field(..., description="Asset symbol")
    interval: CandleInterval = Field(..., description="Time interval")
    start_time: int = Field(..., description="Start time in epoch milliseconds")
    end_time: int = Field(..., description="End time in epoch milliseconds")

    @model_validator(mode="after")
    def validate_time_range(self):
        """Validate end time is after start time."""
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


class GetUserFillsRequest(BaseModel):
    """Request model for user fills by time."""

    start_time: int = Field(..., description="Start time in epoch milliseconds")
    end_time: Optional[int] = Field(None, description="End time in epoch milliseconds")
    user: Optional[str] = Field(None, description="User address to query")


class GetFundingRatesRequest(BaseModel):
    """Request model for funding rates."""

    asset: Optional[str] = Field(None, description="Asset symbol to filter by")
    include_history: bool = Field(
        default=False, description="Include historical funding data"
    )
    start_time: Optional[int] = Field(
        None, description="Start time for historical data"
    )

    @model_validator(mode="after")
    def validate_start_time_for_history(self):
        """Validate start time is provided when including history."""
        if self.include_history and self.start_time is None:
            raise ValueError("start_time is required when include_history is True")
        return self


class SimulateOrderRequest(BaseModel):
    """Request model for order simulation."""

    asset: str = Field(..., description="Asset symbol")
    is_buy: bool = Field(..., description="True for buy order, False for sell order")
    size: float = Field(..., gt=0, description="Order size/quantity")
    price: Optional[float] = Field(
        None,
        gt=0,
        description="Order price (uses current market price if not provided)",
    )


class GetL2OrderbookRequest(BaseModel):
    """Request model for L2 orderbook."""

    asset: str = Field(..., description="Asset symbol")
    significant_figures: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Number of significant figures for price aggregation",
    )


class GetMarketDataRequest(BaseModel):
    """Request model for market data."""

    asset: str = Field(..., description="Asset symbol")


class CalculateMinOrderSizeRequest(BaseModel):
    """Request model for minimum order size calculation."""

    asset: str = Field(..., description="Asset symbol")
    min_value_usd: float = Field(
        default=10.0, gt=0, description="Minimum order value in USD"
    )


class UserAddressRequest(BaseModel):
    """Request model for operations requiring user address."""

    user: Optional[str] = Field(None, description="User address to query (optional)")

    @field_validator("user")
    @classmethod
    def validate_ethereum_address(cls, v):
        """Basic Ethereum address validation."""
        if v is not None and (not v.startswith("0x") or len(v) != 42):
            raise ValueError("Invalid Ethereum address format")
        return v


class AssetFilterRequest(BaseModel):
    """Request model for operations with optional asset filter."""

    asset: Optional[str] = Field(
        None, description="Asset symbol to filter by (optional)"
    )


class OrderStatusRequest(BaseModel):
    """Request model for order status."""

    order_id: int = Field(..., description="Order ID to check status for")
    user: Optional[str] = Field(None, description="User address (optional)")

    @field_validator("user")
    @classmethod
    def validate_ethereum_address(cls, v):
        """Basic Ethereum address validation."""
        if v is not None and (not v.startswith("0x") or len(v) != 42):
            raise ValueError("Invalid Ethereum address format")
        return v
