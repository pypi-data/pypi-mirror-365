"""Hyperliquid client wrapper for MCP server."""

import os
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional

from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from loguru import logger


class HyperliquidClient:
    """Hyperliquid client wrapper with error handling and type safety."""

    def __init__(self) -> None:
        """Initialize the Hyperliquid client."""
        self._info: Optional[Info] = None
        self._exchange: Optional[Exchange] = None
        self._user_address: Optional[str] = None
        self._wallet_address: Optional[str] = None
        self._setup_clients()

    def _setup_clients(self) -> None:
        """Setup Hyperliquid API clients."""
        try:
            # Get configuration from environment
            private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
            user_address = os.getenv("HYPERLIQUID_USER_ADDRESS")
            testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"

            # Determine base URL
            base_url = (
                constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL
            )

            # Info client (read-only)
            self._info = Info(base_url=base_url, skip_ws=True)

            # Exchange client (requires private key)
            if private_key:
                if not private_key.startswith("0x"):
                    private_key = "0x" + private_key

                wallet = Account.from_key(private_key)
                self._exchange = Exchange(wallet=wallet, base_url=base_url)
                self._wallet_address = wallet.address
                logger.info(f"Exchange client initialized with wallet {wallet.address}")
            else:
                logger.warning(
                    "No private key provided - trading operations unavailable"
                )

            # Set user address
            self._user_address = user_address or self._wallet_address

            if self._user_address:
                logger.info(f"Using user address {self._user_address} for queries")

        except Exception as e:
            logger.error(f"Failed to initialize Hyperliquid clients: {e}")
            raise

    @property
    def info(self) -> Info:
        """Get the Info client."""
        if self._info is None:
            raise RuntimeError("Info client not initialized")
        return self._info

    @property
    def exchange(self) -> Exchange:
        """Get the Exchange client."""
        if self._exchange is None:
            raise RuntimeError("Exchange client not initialized - check private key")
        return self._exchange

    @property
    def user_address(self) -> Optional[str]:
        """Get the user address."""
        return self._user_address

    @property
    def wallet_address(self) -> Optional[str]:
        """Get the wallet address."""
        return self._wallet_address

    def is_trading_enabled(self) -> bool:
        """Check if trading operations are available."""
        return self._exchange is not None

    async def get_leverage_and_decimals(self, coin: str) -> tuple[int, int]:
        """Get leverage and decimals for a coin."""
        meta = self.info.meta()
        coin_info = next((m for m in meta["universe"] if m["name"] == coin), None)
        if not coin_info:
            raise ValueError(f"Coin {coin} not found")
        return coin_info["maxLeverage"], coin_info["szDecimals"]

    async def round_to_tick_size(self, coin: str, price: float) -> float:
        """Round price to comply with Hyperliquid's price validation rules."""
        meta = self.info.meta()
        coin_info = next((m for m in meta["universe"] if m["name"] == coin), None)
        if not coin_info:
            raise ValueError(f"Coin {coin} not found")

        sz_decimals = coin_info.get("szDecimals", 0)
        price_decimal = Decimal(str(price))

        # Rule 1: Max 5 significant figures for non-integers
        if price_decimal != price_decimal.to_integral_value():
            # This calculates the correct exponent to round to 5 significant figures
            precision = 5 - (price_decimal.adjusted() + 1)
            rounding_exp = Decimal("1e-" + str(precision))
            price_decimal = price_decimal.quantize(rounding_exp, rounding=ROUND_HALF_UP)

        # Rule 2: Max (6 - szDecimals) decimal places
        max_decimal_places = 6 - sz_decimals
        if max_decimal_places >= 0:
            quantize_pattern = Decimal("1e-" + str(max_decimal_places))
            price_decimal = price_decimal.quantize(
                quantize_pattern, rounding=ROUND_HALF_UP
            )

        rounded_price = float(price_decimal)
        logger.debug(
            f"Rounded price for {coin}: {price} -> {rounded_price} (max_sig_figs: 5, max_decimals: {max_decimal_places})"
        )
        return rounded_price

    def _slippage_price(self, coin: str, is_buy: bool, slippage: float = 0.05) -> float:
        """Calculate price with slippage for market orders."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled - check private key configuration")
        return self.exchange._slippage_price(coin, is_buy, slippage)

    async def _check_order(self, order_response: Dict[str, Any]) -> bool:
        """Check if order was placed successfully."""
        try:
            if order_response.get("status") != "ok":
                return False

            api_response = (
                order_response.get("response", {}).get("data", {}).get("statuses", [])
            )
            for status in api_response:
                if "error" in status:
                    return False
            return True
        except Exception as e:
            logger.error(f"Error checking order: {e}")
            return False

    def _extract_order_id(self, order_response: Dict[str, Any]) -> Optional[int]:
        """Extract order ID from order response."""
        try:
            statuses = (
                order_response.get("response", {}).get("data", {}).get("statuses", [])
            )
            for status in statuses:
                if "resting" in status:
                    return status["resting"]["oid"]
                if "filled" in status:
                    return status["filled"]["oid"]
            return None
        except (KeyError, TypeError, IndexError) as e:
            logger.error(f"Error extracting order ID: {e}")
            return None

    # Account Operations
    async def get_positions(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get current positions."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.user_state(user_address)

    async def get_account_info(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get account information."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.user_state(user_address)

    async def update_leverage(
        self, asset: str, leverage: float, is_isolated: bool = True
    ) -> Dict[str, Any]:
        """Update leverage for an asset."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        leverage_int = int(leverage)
        is_cross = not is_isolated

        return self.exchange.update_leverage(leverage_int, asset, is_cross)

    async def transfer_between_spot_and_perp(
        self, amount: float, to_perp: bool
    ) -> Dict[str, Any]:
        """Transfer funds between spot and perpetual accounts."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        return self.exchange.usd_class_transfer(amount=amount, to_perp=to_perp)

    async def usd_transfer(self, destination: str, amount: float) -> Dict[str, Any]:
        """Transfer USDC to another wallet address."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        # Convert amount to string as required by Hyperliquid API
        amount_str = f"{amount:.6f}"

        return self.exchange.usd_send(
            destination=destination,
            amount=amount_str,
        )

    async def withdraw(self, destination: str, amount: float) -> Dict[str, Any]:
        """Withdraw USDC to external wallet."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        if amount <= 1.0:
            raise ValueError(
                "Withdrawal amount must be greater than $1.00 (withdrawal fee)"
            )

        # Convert amount to string as required by Hyperliquid API
        amount_str = f"{amount:.6f}"

        return self.exchange.withdraw_usdc(
            destination=destination,
            amount=amount_str,
        )

    async def get_spot_user_state(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get spot account state."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.spot_user_state(user_address)

    async def sub_account_transfer(
        self, sub_account: str, amount: float, is_deposit: bool
    ) -> Dict[str, Any]:
        """Transfer funds between main account and sub-account."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        # Convert amount to string as required by Hyperliquid API
        amount_str = f"{amount:.6f}"

        return self.exchange.sub_account_transfer(
            sub_account=sub_account,
            amount=amount_str,
            is_deposit=is_deposit,
        )

    async def get_user_portfolio(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get user portfolio information."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.user_state(user_address)

    async def get_user_fees(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get user fee information."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.user_fees(user_address)

    # Market Operations
    async def get_market_data(self, asset: str) -> Dict[str, Any]:
        """Get market data for an asset."""
        all_mids = self.info.all_mids()
        meta = self.info.meta()

        universe = meta.get("universe", [])
        asset_info = next((a for a in universe if a["name"] == asset), None)

        if not asset_info:
            raise ValueError(f"Asset {asset} not found")

        return {
            "all_mids": all_mids,
            "meta": meta,
            "asset": asset,
        }

    async def calculate_min_order_size(
        self, asset: str, min_value_usd: float = 10.0
    ) -> Dict[str, Any]:
        """Calculate minimum order size to meet minimum order value requirement."""
        # Get current price
        all_mids = self.info.all_mids()
        current_price = float(all_mids.get(asset, "0"))

        if current_price <= 0:
            raise ValueError(f"Invalid price for {asset}: {current_price}")

        # Get decimals for proper rounding
        _, sz_decimals = await self.get_leverage_and_decimals(asset)

        # Calculate minimum size needed with a buffer
        min_size = (min_value_usd * 1.05) / current_price  # 5% buffer
        rounded_size = round(min_size, sz_decimals)

        # Verify the value meets minimum
        estimated_value = rounded_size * current_price
        if estimated_value < min_value_usd:
            # Increase size until we meet minimum
            increment = 1 / (10**sz_decimals)  # Smallest possible increment
            while estimated_value < min_value_usd:
                rounded_size += increment
                estimated_value = rounded_size * current_price
            rounded_size = round(rounded_size, sz_decimals)

        logger.info(
            f"Calculated min order size for {asset}: {rounded_size} (price: ${current_price}, value: ${estimated_value:.2f})"
        )

        return {
            "asset": asset,
            "current_price": current_price,
            "min_size": rounded_size,
            "estimated_value": estimated_value,
        }

    async def get_candle_data(
        self, asset: str, interval: str, start_time: int, end_time: int
    ) -> Dict[str, Any]:
        """Get historical candle data."""
        return self.info.candles_snapshot(asset, interval, start_time, end_time)

    async def get_user_fills_by_time(
        self,
        start_time: int,
        end_time: Optional[int] = None,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get user fills by time range."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.user_fills_by_time(user_address, start_time, end_time)

    async def get_all_mids_detailed(self) -> Dict[str, Any]:
        """Get detailed market data for all assets."""
        return self.info.meta_and_asset_ctxs()

    async def get_funding_rates(
        self,
        asset: Optional[str] = None,
        include_history: bool = False,
        start_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get funding rates."""
        result: dict = {"current_funding": {}, "historical_funding": {}}

        # Get current funding from meta and contexts
        meta_and_contexts = self.info.meta_and_asset_ctxs()
        if len(meta_and_contexts) >= 2:
            universe = meta_and_contexts[0].get("universe", [])
            asset_contexts = meta_and_contexts[1]

            for i, ctx in enumerate(asset_contexts):
                if i < len(universe) and isinstance(ctx, dict):
                    asset_name = universe[i].get("name", "")
                    if not asset or asset_name == asset:
                        result["current_funding"][asset_name] = ctx

        # Get historical funding if requested
        if include_history and asset and start_time:
            try:
                historical = self.info.funding_history(asset, start_time)
                result["historical_funding"][asset] = historical
            except Exception as e:
                logger.warning(f"Could not get historical funding for {asset}: {e}")

        return result

    async def simulate_order(
        self, asset: str, is_buy: bool, size: float, price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Simulate an order."""
        all_mids = self.info.all_mids()
        current_price = float(all_mids.get(asset, "0"))

        if current_price <= 0:
            raise ValueError(f"Could not get valid price for {asset}")

        final_price = price or current_price
        order_value = size * final_price
        price_impact = abs(final_price - current_price) / current_price * 100

        return {
            "asset": asset,
            "side": "BUY" if is_buy else "SELL",
            "size": size,
            "price": final_price,
            "current_market_price": current_price,
            "order_value_usd": order_value,
            "price_impact_percent": price_impact,
            "validations": {
                "min_order_value": order_value >= 10.0,
                "price_reasonable": price_impact <= 5.0,
                "size_valid": size > 0,
            },
        }

    # Order Operations
    async def place_order(
        self,
        asset: str,
        is_buy: bool,
        size: float,
        order_type: str = "market",
        price: Optional[float] = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place an order on Hyperliquid with optional TP/SL."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        response: Dict[str, Any] = {
            "main_order": [],
            "stop_loss": [],
            "take_profit": [],
        }

        try:

            # 1. Calculate price for market orders or validate limit price
            if order_type == "market":
                px = self._slippage_price(asset, is_buy, 0.05)  # 5% slippage
                # Round market order price to tick size too
                px = await self.round_to_tick_size(asset, px)
                time_in_force = "IOC"  # Force IOC for market orders
            elif order_type in ["limit", "trigger"]:
                if price is None:
                    raise ValueError(f"Price is required for {order_type} orders")
                # Round price to correct tick size
                px = await self.round_to_tick_size(asset, price)
                logger.info(f"Rounded {order_type} price to tick size: ${px}")
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            # 2. Validate minimum order value ($10 minimum)
            estimated_value = size * px
            if estimated_value < 10.0:
                logger.warning(
                    f"Order value ${estimated_value:.2f} below $10 minimum. Consider using calculate_min_order_size()"
                )

            # Convert order type to Hyperliquid format
            tif_map = {"GTC": "Gtc", "IOC": "Ioc", "ALO": "Alo"}
            order_type_map = {
                "limit": {"limit": {"tif": tif_map.get(time_in_force, "Gtc")}},
                "market": {
                    "limit": {"tif": "Ioc"}
                },  # Market orders use IOC limit orders
                "trigger": {
                    "trigger": {
                        "triggerPx": px,
                        "tif": tif_map.get(time_in_force, "Gtc"),
                    }
                },
            }

            if order_type not in order_type_map:
                raise ValueError(f"Unsupported order type: {order_type}")

            # 3. Place main order
            logger.info(
                f"Placing order with final parameters: asset={asset}, is_buy={is_buy}, sz={size}, px={px}, order_type={order_type_map[order_type]}"
            )
            main_order_result = self.exchange.order(
                asset, is_buy, size, px, order_type_map[order_type], reduce_only, None
            )

            if not await self._check_order(main_order_result):
                raise ValueError(f"Failed to place main order: {main_order_result}")

            # Extract order ID from response
            main_oid = self._extract_order_id(main_order_result)
            if main_oid:
                response["main_order"] = [main_oid]

            # 4. Place stop loss if specified
            if stop_loss is not None:
                # Round stop loss to tick size
                stop_loss_rounded = await self.round_to_tick_size(asset, stop_loss)
                sl_result = self.exchange.order(
                    asset,
                    not is_buy,  # Opposite direction
                    size,
                    stop_loss_rounded,
                    {
                        "trigger": {
                            "triggerPx": stop_loss_rounded,
                            "isMarket": True,
                            "tpsl": "sl",
                        }
                    },
                    reduce_only=True,
                )

                if await self._check_order(sl_result):
                    sl_oid = self._extract_order_id(sl_result)
                    if sl_oid:
                        response["stop_loss"] = [sl_oid]
                else:
                    logger.warning(f"Failed to place stop loss: {sl_result}")

            # 5. Place take profit if specified
            if take_profit is not None:
                # Round take profit to tick size
                take_profit_rounded = await self.round_to_tick_size(asset, take_profit)
                tp_result = self.exchange.order(
                    asset,
                    not is_buy,  # Opposite direction
                    size,
                    take_profit_rounded,
                    {
                        "trigger": {
                            "triggerPx": take_profit_rounded,
                            "isMarket": True,
                            "tpsl": "tp",
                        }
                    },
                    reduce_only=True,
                )

                if await self._check_order(tp_result):
                    tp_oid = self._extract_order_id(tp_result)
                    if tp_oid:
                        response["take_profit"] = [tp_oid]
                else:
                    logger.warning(f"Failed to place take profit: {tp_result}")

            logger.info(f"Order placed successfully: {response}")
            return response

        except Exception as e:
            # Cancel any successfully placed orders if there was an error
            orders_to_cancel = []
            for order_type_key, oids in response.items():
                for oid in oids:
                    if isinstance(oid, int):
                        orders_to_cancel.append({"coin": asset, "oid": oid})

            if orders_to_cancel:
                try:
                    self.exchange.bulk_cancel(orders_to_cancel)
                    logger.info(
                        f"Cancelled {len(orders_to_cancel)} orders due to error"
                    )
                except Exception as cancel_error:
                    logger.error(f"Failed to cancel orders after error: {cancel_error}")

            logger.error(f"Failed to place order: {e}")
            raise

    async def cancel_order(self, asset: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        return self.exchange.cancel(asset, order_id)

    async def get_open_orders(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get open orders."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.open_orders(user_address)

    async def get_order_status(
        self, order_id: int, user: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get order status."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.query_order_by_oid(user_address, order_id)

    async def modify_order(
        self,
        asset: str,
        order_id: int,
        new_price: Optional[float] = None,
        new_size: Optional[float] = None,
        new_time_in_force: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify an order."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        # Get current order info
        user_address = self.user_address or self.wallet_address
        if not user_address:
            raise ValueError("No user address available")

        current_order = self.info.query_order_by_oid(user_address, order_id)
        if current_order.get("status") == "unknownOid":
            raise ValueError(f"Order {order_id} not found")

        # Use current values as defaults
        order_data = current_order.get("order", {}).get("order", {})
        final_is_buy = order_data.get("side") == "B"
        final_size = (
            new_size if new_size is not None else float(order_data.get("origSz", "0"))
        )
        final_price = (
            new_price
            if new_price is not None
            else float(order_data.get("limitPx", "0"))
        )

        # Build order type
        if new_time_in_force:
            tif_map = {"GTC": "Gtc", "IOC": "Ioc", "ALO": "Alo"}
            order_type = {"limit": {"tif": tif_map.get(new_time_in_force, "Gtc")}}
        else:
            order_type = {"limit": {"tif": "Gtc"}}

        return self.exchange.modify_order(
            oid=order_id,
            name=asset,
            is_buy=final_is_buy,
            sz=final_size,
            limit_px=final_price,
            order_type=order_type,
            reduce_only=False,
        )

    async def bulk_cancel_orders(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cancel multiple orders."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        formatted_orders = [
            {"coin": order["asset"], "oid": int(order["order_id"])} for order in orders
        ]
        return self.exchange.bulk_cancel(formatted_orders)

    async def cancel_all_orders(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all open orders."""
        if not self.is_trading_enabled():
            raise RuntimeError("Trading not enabled")

        user_address = self.user_address or self.wallet_address
        if not user_address:
            raise ValueError("No user address available")

        open_orders = self.info.open_orders(user_address)

        if asset:
            orders_to_cancel = [
                {"coin": order["coin"], "oid": order["oid"]}
                for order in open_orders
                if order.get("coin") == asset
            ]
        else:
            orders_to_cancel = [
                {"coin": order["coin"], "oid": order["oid"]} for order in open_orders
            ]

        if not orders_to_cancel:
            return {"status": "ok", "response": {"data": {"statuses": []}}}

        return self.exchange.bulk_cancel(orders_to_cancel)

    async def get_user_fills(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get user fills."""
        user_address = user or self.user_address
        if not user_address:
            raise ValueError("No user address available")

        return self.info.user_fills(user_address)

    async def get_historical_orders(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get historical orders (via fills)."""
        return await self.get_user_fills(user)

    async def get_l2_orderbook(
        self, asset: str, significant_figures: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get L2 orderbook."""
        return self.info.l2_snapshot(asset)
