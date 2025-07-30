"""Test suite for Hyperliquid MCP Server tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hyperliquid_mcp.models import (
    AssetFilterRequest,
    BulkCancelRequest,
    CalculateMinOrderSizeRequest,
    CancelOrderRequest,
    CandleInterval,
    GetCandleDataRequest,
    GetFundingRatesRequest,
    GetL2OrderbookRequest,
    GetMarketDataRequest,
    GetUserFillsRequest,
    ModifyOrderRequest,
    OrderStatusRequest,
    OrderType,
    PlaceOrderRequest,
    SimulateOrderRequest,
    SubAccountTransferRequest,
    TimeInForce,
    TransferRequest,
    UpdateLeverageRequest,
    UsdTransferRequest,
    UserAddressRequest,
    WithdrawRequest,
)
from hyperliquid_mcp.server import get_client, mcp

# Valid Ethereum address for testing
TEST_ADDRESS = "0x1234567890123456789012345678901234567890"


@pytest.fixture
def mock_client():
    """Create a mock Hyperliquid client."""
    with patch("hyperliquid_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        yield mock_client


class TestAccountTools:
    """Test account-related MCP tools."""

    @pytest.mark.asyncio
    async def test_get_positions(self, mock_client):
        """Test get_positions tool."""
        mock_client.get_positions.return_value = {"positions": [], "marginSummary": {}}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_positions"].fn
        result = await tool_func(request)

        mock_client.get_positions.assert_called_once_with(TEST_ADDRESS)
        assert "positions" in result

    @pytest.mark.asyncio
    async def test_get_positions_error(self, mock_client):
        """Test get_positions tool error handling."""
        mock_client.get_positions.side_effect = Exception("API Error")

        request = UserAddressRequest()
        tool_func = mcp._tool_manager._tools["get_positions"].fn
        result = await tool_func(request)

        assert "error" in result
        assert result["error"] == "API Error"

    @pytest.mark.asyncio
    async def test_get_account_info(self, mock_client):
        """Test get_account_info tool."""
        mock_client.get_account_info.return_value = {
            "marginSummary": {"accountValue": "1000"}
        }

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_account_info"].fn
        result = await tool_func(request)

        mock_client.get_account_info.assert_called_once_with(TEST_ADDRESS)
        assert "marginSummary" in result

    @pytest.mark.asyncio
    async def test_update_leverage(self, mock_client):
        """Test update_leverage tool."""
        mock_client.update_leverage.return_value = {"status": "ok"}

        request = UpdateLeverageRequest(asset="ETH", leverage=10, is_isolated=True)
        tool_func = mcp._tool_manager._tools["update_leverage"].fn
        result = await tool_func(request)

        mock_client.update_leverage.assert_called_once_with("ETH", 10, True)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_transfer_between_spot_and_perp(self, mock_client):
        """Test transfer_between_spot_and_perp tool."""
        mock_client.transfer_between_spot_and_perp.return_value = {"status": "ok"}

        request = TransferRequest(amount=100.0, to_perp=True)
        tool_func = mcp._tool_manager._tools["transfer_between_spot_and_perp"].fn
        result = await tool_func(request)

        mock_client.transfer_between_spot_and_perp.assert_called_once_with(100.0, True)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_usd_transfer(self, mock_client):
        """Test usd_transfer tool."""
        mock_client.usd_transfer.return_value = {"status": "ok"}

        request = UsdTransferRequest(destination=TEST_ADDRESS, amount=50.0)
        tool_func = mcp._tool_manager._tools["usd_transfer"].fn
        result = await tool_func(request)

        mock_client.usd_transfer.assert_called_once_with(TEST_ADDRESS, 50.0)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_withdraw(self, mock_client):
        """Test withdraw tool."""
        mock_client.withdraw.return_value = {"status": "ok"}

        request = WithdrawRequest(destination=TEST_ADDRESS, amount=50.0)
        tool_func = mcp._tool_manager._tools["withdraw"].fn
        result = await tool_func(request)

        mock_client.withdraw.assert_called_once_with(TEST_ADDRESS, 50.0)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_get_spot_user_state(self, mock_client):
        """Test get_spot_user_state tool."""
        mock_client.get_spot_user_state.return_value = {"balances": []}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_spot_user_state"].fn
        result = await tool_func(request)

        mock_client.get_spot_user_state.assert_called_once_with(TEST_ADDRESS)
        assert "balances" in result

    @pytest.mark.asyncio
    async def test_sub_account_transfer(self, mock_client):
        """Test sub_account_transfer tool."""
        mock_client.sub_account_transfer.return_value = {"status": "ok"}

        request = SubAccountTransferRequest(
            sub_account=TEST_ADDRESS, amount=100.0, is_deposit=True
        )
        tool_func = mcp._tool_manager._tools["sub_account_transfer"].fn
        result = await tool_func(request)

        mock_client.sub_account_transfer.assert_called_once_with(
            TEST_ADDRESS, 100.0, True
        )
        assert "status" in result

    @pytest.mark.asyncio
    async def test_get_user_portfolio(self, mock_client):
        """Test get_user_portfolio tool."""
        mock_client.get_user_portfolio.return_value = {"portfolio": {}}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_user_portfolio"].fn
        result = await tool_func(request)

        mock_client.get_user_portfolio.assert_called_once_with(TEST_ADDRESS)
        assert "portfolio" in result

    @pytest.mark.asyncio
    async def test_get_user_fees(self, mock_client):
        """Test get_user_fees tool."""
        mock_client.get_user_fees.return_value = {"fees": {}}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_user_fees"].fn
        result = await tool_func(request)

        mock_client.get_user_fees.assert_called_once_with(TEST_ADDRESS)
        assert "fees" in result


class TestMarketDataTools:
    """Test market data related MCP tools."""

    @pytest.mark.asyncio
    async def test_get_market_data(self, mock_client):
        """Test get_market_data tool."""
        mock_client.get_market_data.return_value = {"symbol": "ETH", "price": "2000"}

        request = GetMarketDataRequest(asset="ETH")
        tool_func = mcp._tool_manager._tools["get_market_data"].fn
        result = await tool_func(request)

        mock_client.get_market_data.assert_called_once_with("ETH")
        assert "symbol" in result

    @pytest.mark.asyncio
    async def test_calculate_min_order_size(self, mock_client):
        """Test calculate_min_order_size tool."""
        mock_client.calculate_min_order_size.return_value = {"min_size": "0.1"}

        request = CalculateMinOrderSizeRequest(asset="ETH", min_value_usd=10.0)
        tool_func = mcp._tool_manager._tools["calculate_min_order_size"].fn
        result = await tool_func(request)

        mock_client.calculate_min_order_size.assert_called_once_with("ETH", 10.0)
        assert "min_size" in result

    @pytest.mark.asyncio
    async def test_get_candle_data(self, mock_client):
        """Test get_candle_data tool."""
        mock_client.get_candle_data.return_value = {"candles": []}

        request = GetCandleDataRequest(
            asset="ETH",
            interval=CandleInterval.ONE_HOUR,
            start_time=1640995200000,
            end_time=1641081600000,
        )
        tool_func = mcp._tool_manager._tools["get_candle_data"].fn
        result = await tool_func(request)

        mock_client.get_candle_data.assert_called_once_with(
            "ETH", "1h", 1640995200000, 1641081600000
        )
        assert "candles" in result

    @pytest.mark.asyncio
    async def test_get_user_fills_by_time(self, mock_client):
        """Test get_user_fills_by_time tool."""
        mock_client.get_user_fills_by_time.return_value = {"fills": []}

        request = GetUserFillsRequest(
            start_time=1640995200000, end_time=1641081600000, user=TEST_ADDRESS
        )
        tool_func = mcp._tool_manager._tools["get_user_fills_by_time"].fn
        result = await tool_func(request)

        mock_client.get_user_fills_by_time.assert_called_once_with(
            1640995200000, 1641081600000, TEST_ADDRESS
        )
        assert "fills" in result

    @pytest.mark.asyncio
    async def test_get_all_mids_detailed(self, mock_client):
        """Test get_all_mids_detailed tool."""
        mock_client.get_all_mids_detailed.return_value = {"mids": {}}

        tool_func = mcp._tool_manager._tools["get_all_mids_detailed"].fn
        result = await tool_func()

        mock_client.get_all_mids_detailed.assert_called_once()
        assert "mids" in result

    @pytest.mark.asyncio
    async def test_get_funding_rates(self, mock_client):
        """Test get_funding_rates tool."""
        mock_client.get_funding_rates.return_value = {"funding_rates": []}

        request = GetFundingRatesRequest(
            asset="ETH", include_history=True, start_time=1640995200000
        )
        tool_func = mcp._tool_manager._tools["get_funding_rates"].fn
        result = await tool_func(request)

        mock_client.get_funding_rates.assert_called_once_with(
            "ETH", True, 1640995200000
        )
        assert "funding_rates" in result

    @pytest.mark.asyncio
    async def test_simulate_order(self, mock_client):
        """Test simulate_order tool."""
        mock_client.simulate_order.return_value = {"simulation": {}}

        request = SimulateOrderRequest(asset="ETH", is_buy=True, size=1.0, price=2000.0)
        tool_func = mcp._tool_manager._tools["simulate_order"].fn
        result = await tool_func(request)

        mock_client.simulate_order.assert_called_once_with("ETH", True, 1.0, 2000.0)
        assert "simulation" in result

    @pytest.mark.asyncio
    async def test_get_l2_orderbook(self, mock_client):
        """Test get_l2_orderbook tool."""
        mock_client.get_l2_orderbook.return_value = {"levels": []}

        request = GetL2OrderbookRequest(asset="ETH", significant_figures=3)
        tool_func = mcp._tool_manager._tools["get_l2_orderbook"].fn
        result = await tool_func(request)

        mock_client.get_l2_orderbook.assert_called_once_with("ETH", 3)
        assert "levels" in result


class TestOrderManagementTools:
    """Test order management related MCP tools."""

    @pytest.mark.asyncio
    async def test_place_order(self, mock_client):
        """Test place_order tool."""
        mock_client.place_order.return_value = {"status": "ok", "orderId": "123"}

        request = PlaceOrderRequest(
            asset="ETH",
            is_buy=True,
            size=1.0,
            order_type=OrderType.LIMIT,
            price=2000.0,
            time_in_force=TimeInForce.GTC,
            reduce_only=False,
        )
        tool_func = mcp._tool_manager._tools["place_order"].fn
        result = await tool_func(request)

        mock_client.place_order.assert_called_once_with(
            "ETH", True, 1.0, "limit", 2000.0, "GTC", False, None, None
        )
        assert "status" in result

    @pytest.mark.asyncio
    async def test_cancel_order(self, mock_client):
        """Test cancel_order tool."""
        mock_client.cancel_order.return_value = {"status": "ok"}

        request = CancelOrderRequest(asset="ETH", order_id=123)
        tool_func = mcp._tool_manager._tools["cancel_order"].fn
        result = await tool_func(request)

        mock_client.cancel_order.assert_called_once_with("ETH", 123)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_get_open_orders(self, mock_client):
        """Test get_open_orders tool."""
        mock_client.get_open_orders.return_value = {"orders": []}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_open_orders"].fn
        result = await tool_func(request)

        mock_client.get_open_orders.assert_called_once_with(TEST_ADDRESS)
        assert "orders" in result

    @pytest.mark.asyncio
    async def test_get_order_status(self, mock_client):
        """Test get_order_status tool."""
        mock_client.get_order_status.return_value = {"status": "filled"}

        request = OrderStatusRequest(order_id=123, user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_order_status"].fn
        result = await tool_func(request)

        mock_client.get_order_status.assert_called_once_with(123, TEST_ADDRESS)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_modify_order(self, mock_client):
        """Test modify_order tool."""
        mock_client.modify_order.return_value = {"status": "ok"}

        request = ModifyOrderRequest(
            asset="ETH",
            order_id=123,
            new_price=2100.0,
            new_size=1.5,
            new_time_in_force=TimeInForce.IOC,
        )
        tool_func = mcp._tool_manager._tools["modify_order"].fn
        result = await tool_func(request)

        mock_client.modify_order.assert_called_once_with("ETH", 123, 2100.0, 1.5, "IOC")
        assert "status" in result

    @pytest.mark.asyncio
    async def test_bulk_cancel_orders(self, mock_client):
        """Test bulk_cancel_orders tool."""
        mock_client.bulk_cancel_orders.return_value = {"status": "ok"}

        orders = [{"asset": "ETH", "order_id": 123}, {"asset": "BTC", "order_id": 456}]
        request = BulkCancelRequest(orders=orders)
        tool_func = mcp._tool_manager._tools["bulk_cancel_orders"].fn
        result = await tool_func(request)

        mock_client.bulk_cancel_orders.assert_called_once_with(orders)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_cancel_all_orders(self, mock_client):
        """Test cancel_all_orders tool."""
        mock_client.cancel_all_orders.return_value = {"status": "ok"}

        request = AssetFilterRequest(asset="ETH")
        tool_func = mcp._tool_manager._tools["cancel_all_orders"].fn
        result = await tool_func(request)

        mock_client.cancel_all_orders.assert_called_once_with("ETH")
        assert "status" in result

    @pytest.mark.asyncio
    async def test_get_user_fills(self, mock_client):
        """Test get_user_fills tool."""
        mock_client.get_user_fills.return_value = {"fills": []}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_user_fills"].fn
        result = await tool_func(request)

        mock_client.get_user_fills.assert_called_once_with(TEST_ADDRESS)
        assert "fills" in result

    @pytest.mark.asyncio
    async def test_get_historical_orders(self, mock_client):
        """Test get_historical_orders tool."""
        mock_client.get_historical_orders.return_value = {"orders": []}

        request = UserAddressRequest(user=TEST_ADDRESS)
        tool_func = mcp._tool_manager._tools["get_historical_orders"].fn
        result = await tool_func(request)

        mock_client.get_historical_orders.assert_called_once_with(TEST_ADDRESS)
        assert "orders" in result


class TestClientSingleton:
    """Test client singleton behavior."""

    def test_get_client_singleton(self):
        """Test that get_client returns the same instance."""
        with patch("hyperliquid_mcp.server.HyperliquidClient") as mock_client_class:
            mock_instance = MagicMock()
            mock_client_class.return_value = mock_instance

            # Reset the global client
            import hyperliquid_mcp.server

            hyperliquid_mcp.server.client = None

            client1 = get_client()
            client2 = get_client()

            assert client1 is client2
            mock_client_class.assert_called_once()
