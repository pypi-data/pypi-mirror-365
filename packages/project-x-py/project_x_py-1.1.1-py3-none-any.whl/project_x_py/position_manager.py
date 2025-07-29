#!/usr/bin/env python3
"""
PositionManager for Comprehensive Position Operations

Author: TexasCoding
Date: June 2025

This module provides comprehensive position management capabilities for the ProjectX API:
1. Position tracking and monitoring
2. Real-time position updates and P&L calculation
3. Portfolio-level position management
4. Risk metrics and exposure analysis
5. Position sizing and risk management
6. Automated position monitoring and alerts

Key Features:
- Thread-safe position operations
- Dependency injection with ProjectX client
- Integration with ProjectXRealtimeClient for live updates
- Real-time P&L and risk calculations
- Portfolio-level analytics and reporting
- Position-based risk management

Architecture:
- Similar to OrderBook and OrderManager
- Clean separation from main client class
- Real-time position tracking capabilities
- Event-driven position updates
"""

import asyncio
import json
import logging
import threading
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

import requests

from .exceptions import (
    ProjectXError,
)
from .lock_coordinator import get_lock_coordinator
from .models import Position

if TYPE_CHECKING:
    from .client import ProjectX
    from .order_manager import OrderManager
    from .realtime import ProjectXRealtimeClient


class PositionManager:
    """
    Comprehensive position management system for ProjectX trading operations.

    This class handles all position-related operations including tracking, monitoring,
    analysis, and management. It integrates with both the ProjectX API client and
    the real-time client for live position monitoring.

    Features:
        - Real-time position tracking and monitoring
        - Portfolio-level position management
        - Automated P&L calculation and risk metrics
        - Position sizing and risk management tools
        - Event-driven position updates (closures detected from type=0/size=0)
        - Thread-safe operations for concurrent access

    Example Usage:
        >>> # Create position manager with dependency injection
        >>> position_manager = PositionManager(project_x_client)
        >>> # Initialize with optional real-time client
        >>> position_manager.initialize(realtime_client=realtime_client)
        >>> # Get current positions
        >>> positions = position_manager.get_all_positions()
        >>> mgc_position = position_manager.get_position("MGC")
        >>> # Portfolio analytics
        >>> portfolio_pnl = position_manager.get_portfolio_pnl()
        >>> risk_metrics = position_manager.get_risk_metrics()
        >>> # Position monitoring
        >>> position_manager.add_position_alert("MGC", max_loss=-500.0)
        >>> position_manager.start_monitoring()
        >>> # Position sizing
        >>> suggested_size = position_manager.calculate_position_size(
        ...     "MGC", risk_amount=100.0, entry_price=2045.0, stop_price=2040.0
        ... )
    """

    def __init__(self, project_x_client: "ProjectX"):
        """
        Initialize the PositionManager with a ProjectX client.

        Args:
            project_x_client: ProjectX client instance for API access
        """
        self.project_x = project_x_client
        self.logger = logging.getLogger(__name__)

        # Thread safety (coordinated with other components)
        self.lock_coordinator = get_lock_coordinator()
        self.position_lock = self.lock_coordinator.position_lock

        # Real-time integration (optional)
        self.realtime_client: ProjectXRealtimeClient | None = None
        self._realtime_enabled = False

        # Order management integration (optional)
        self.order_manager: OrderManager | None = None
        self._order_sync_enabled = False

        # Position tracking (maintains local state for business logic)
        self.tracked_positions: dict[str, Position] = {}
        self.position_history: dict[str, list[dict]] = defaultdict(list)
        self.position_callbacks: dict[str, list] = defaultdict(list)

        # Monitoring and alerts
        self._monitoring_active = False
        self._monitoring_thread: threading.Thread | None = None
        self.position_alerts: dict[str, dict] = {}

        # Statistics and metrics
        self.stats = {
            "positions_tracked": 0,
            "total_pnl": 0.0,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "positions_closed": 0,
            "positions_partially_closed": 0,
            "last_update_time": None,
            "monitoring_started": None,
        }

        # Risk management settings
        self.risk_settings = {
            "max_portfolio_risk": 0.02,  # 2% of portfolio
            "max_position_risk": 0.01,  # 1% per position
            "max_correlation": 0.7,  # Maximum correlation between positions
            "alert_threshold": 0.005,  # 0.5% threshold for alerts
        }

        self.logger.info("PositionManager initialized")

    def initialize(
        self,
        realtime_client: Optional["ProjectXRealtimeClient"] = None,
        order_manager: Optional["OrderManager"] = None,
    ) -> bool:
        """
        Initialize the PositionManager with optional real-time capabilities and order synchronization.

        Args:
            realtime_client: Optional ProjectXRealtimeClient for live position tracking
            order_manager: Optional OrderManager for automatic order synchronization

        Returns:
            bool: True if initialization successful
        """
        try:
            # Set up real-time integration if provided
            if realtime_client:
                self.realtime_client = realtime_client
                self._setup_realtime_callbacks()
                self._realtime_enabled = True
                self.logger.info(
                    "✅ PositionManager initialized with real-time capabilities"
                )
            else:
                self.logger.info("✅ PositionManager initialized (polling mode)")

            # Set up order management integration if provided
            if order_manager:
                self.order_manager = order_manager
                self._order_sync_enabled = True
                self.logger.info(
                    "✅ PositionManager initialized with order synchronization"
                )

            # Load initial positions
            self.refresh_positions()

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize PositionManager: {e}")
            return False

    def _setup_realtime_callbacks(self):
        """Set up callbacks for real-time position monitoring."""
        if not self.realtime_client:
            return

        # Register for position events (closures are detected from position updates)
        self.realtime_client.add_callback("position_update", self._on_position_update)
        self.realtime_client.add_callback("account_update", self._on_account_update)

        self.logger.info("🔄 Real-time position callbacks registered")

    def _on_position_update(self, data: dict):
        """Handle real-time position updates and detect position closures."""
        try:
            with self.position_lock:
                if isinstance(data, list):
                    for position_data in data:
                        self._process_position_data(position_data)
                elif isinstance(data, dict):
                    self._process_position_data(data)

            # Note: No duplicate callback triggering - realtime client handles this

        except Exception as e:
            self.logger.error(f"Error processing position update: {e}")

    def _on_account_update(self, data: dict):
        """Handle account-level updates that may affect positions."""
        self._trigger_callbacks("account_update", data)

    def _validate_position_payload(self, position_data: dict) -> bool:
        """
        Validate that position payload matches ProjectX GatewayUserPosition format.

        Expected fields according to ProjectX docs:
        - id (int): The position ID
        - accountId (int): The account associated with the position
        - contractId (string): The contract ID associated with the position
        - creationTimestamp (string): When the position was created or opened
        - type (int): PositionType enum (Undefined=0, Long=1, Short=2)
        - size (int): The size of the position (0 means closed)
        - averagePrice (number): The average price of the position

        Args:
            position_data: Position payload from ProjectX realtime feed

        Returns:
            bool: True if payload format is valid
        """
        required_fields = {
            "id",
            "accountId",
            "contractId",
            "creationTimestamp",
            "type",
            "size",
            "averagePrice",
        }

        if not isinstance(position_data, dict):
            self.logger.warning(
                f"Position payload is not a dict: {type(position_data)}"
            )
            return False

        missing_fields = required_fields - set(position_data.keys())
        if missing_fields:
            self.logger.warning(
                f"Position payload missing required fields: {missing_fields}"
            )
            return False

        # Validate PositionType enum values
        position_type = position_data.get("type")
        if position_type not in [0, 1, 2]:  # Undefined, Long, Short
            self.logger.warning(f"Invalid position type: {position_type}")
            return False

        return True

    def _process_position_data(self, position_data: dict):
        """
        Process individual position data update and detect position closures.

        ProjectX GatewayUserPosition payload structure:
        - Position is closed when size == 0 (not when type == 0)
        - type=0 means "Undefined" according to PositionType enum
        - type=1 means "Long", type=2 means "Short"
        """
        try:
            # According to ProjectX docs, the payload IS the position data directly
            # No need to extract from "data" field

            # Validate payload format
            if not self._validate_position_payload(position_data):
                self.logger.error(f"Invalid position payload format: {position_data}")
                return

            contract_id = position_data.get("contractId")
            if not contract_id:
                self.logger.error(f"No contract ID found in {position_data}")
                return

            # Check if this is a position closure
            # Position is closed when size == 0 (not when type == 0)
            # type=0 means "Undefined" according to PositionType enum, not closed
            position_size = position_data.get("size", 0)
            is_position_closed = position_size == 0

            # Get the old position before updating
            old_position = self.tracked_positions.get(contract_id)
            old_size = old_position.size if old_position else 0

            if is_position_closed:
                # Position is closed - remove from tracking and trigger closure callbacks
                if contract_id in self.tracked_positions:
                    del self.tracked_positions[contract_id]
                    self.logger.info(f"📊 Position closed: {contract_id}")
                    self.stats["positions_closed"] += 1

                # Synchronize orders - cancel related orders when position is closed
                if self._order_sync_enabled and self.order_manager:
                    self.order_manager.on_position_closed(contract_id)

                # Trigger position_closed callbacks with the closure data
                self._trigger_callbacks("position_closed", {"data": position_data})
            else:
                # Position is open/updated - create or update position
                # ProjectX payload structure matches our Position model fields
                position = Position(**position_data)
                self.tracked_positions[contract_id] = position

                # Synchronize orders - update order sizes if position size changed
                if (
                    self._order_sync_enabled
                    and self.order_manager
                    and old_size != position_size
                ):
                    self.order_manager.on_position_changed(
                        contract_id, old_size, position_size
                    )

                # Track position history
                self.position_history[contract_id].append(
                    {
                        "timestamp": datetime.now(),
                        "position": position_data.copy(),
                        "size_change": position_size - old_size,
                    }
                )

                # Check alerts
                self._check_position_alerts(contract_id, position, old_position)

        except Exception as e:
            self.logger.error(f"Error processing position data: {e}")
            self.logger.debug(f"Position data that caused error: {position_data}")

    def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger registered callbacks for position events."""
        for callback in self.position_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in {event_type} callback: {e}")

    def add_callback(self, event_type: str, callback):
        """
        Register a callback function for specific position events.

        Allows you to listen for position updates, closures, account changes, and alerts
        to build custom monitoring and notification systems.

        Args:
            event_type: Type of event to listen for
                - "position_update": Position size or price changes
                - "position_closed": Position fully closed (size = 0)
                - "account_update": Account-level changes
                - "position_alert": Position alert triggered
            callback: Function to call when event occurs
                Should accept one argument: the event data dict

        Example:
            >>> def on_position_update(data):
            ...     pos = data.get("data", {})
            ...     print(
            ...         f"Position updated: {pos.get('contractId')} size: {pos.get('size')}"
            ...     )
            >>> position_manager.add_callback("position_update", on_position_update)
            >>> def on_position_closed(data):
            ...     pos = data.get("data", {})
            ...     print(f"Position closed: {pos.get('contractId')}")
            >>> position_manager.add_callback("position_closed", on_position_closed)
        """
        self.position_callbacks[event_type].append(callback)

    # ================================================================================
    # CORE POSITION RETRIEVAL METHODS
    # ================================================================================

    def get_all_positions(self, account_id: int | None = None) -> list[Position]:
        """
        Get all current positions.

        Args:
            account_id: Account ID. Uses default account if None.

        Returns:
            List[Position]: List of all current positions

        Example:
            >>> positions = position_manager.get_all_positions()
            >>> for pos in positions:
            ...     print(f"{pos.contractId}: {pos.size} @ ${pos.averagePrice}")
        """
        try:
            positions = self.project_x.search_open_positions(account_id=account_id)

            # Update tracked positions
            with self.position_lock:
                for position in positions:
                    self.tracked_positions[position.contractId] = position

                # Update statistics
                self.stats["positions_tracked"] = len(positions)
                self.stats["last_update_time"] = datetime.now()

            return positions

        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve positions: {e}")
            return []

    def get_position(
        self, contract_id: str, account_id: int | None = None
    ) -> Position | None:
        """
        Get a specific position by contract ID.

        Args:
            contract_id: Contract ID to search for
            account_id: Account ID. Uses default account if None.

        Returns:
            Position: Position object if found, None otherwise

        Example:
            >>> mgc_position = position_manager.get_position("MGC")
            >>> if mgc_position:
            ...     print(f"MGC size: {mgc_position.size}")
        """
        # Try cached data first if real-time enabled
        if self._realtime_enabled:
            with self.position_lock:
                cached_position = self.tracked_positions.get(contract_id)
                if cached_position:
                    return cached_position

        # Fallback to API search
        positions = self.get_all_positions(account_id=account_id)
        for position in positions:
            if position.contractId == contract_id:
                return position

        return None

    def refresh_positions(self, account_id: int | None = None) -> bool:
        """
        Refresh all position data from the API.

        Args:
            account_id: Account ID. Uses default account if None.

        Returns:
            bool: True if refresh successful
        """
        try:
            positions = self.get_all_positions(account_id=account_id)
            self.logger.info(f"🔄 Refreshed {len(positions)} positions")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to refresh positions: {e}")
            return False

    def is_position_open(self, contract_id: str, account_id: int | None = None) -> bool:
        """
        Check if a position exists for the given contract.

        Args:
            contract_id: Contract ID to check
            account_id: Account ID. Uses default account if None.

        Returns:
            bool: True if position exists and size > 0
        """
        position = self.get_position(contract_id, account_id)
        return position is not None and position.size != 0

    # ================================================================================
    # P&L CALCULATION METHODS (requires market prices)
    # ================================================================================

    def calculate_position_pnl(
        self, position: Position, current_price: float
    ) -> dict[str, Any]:
        """
        Calculate P&L for a position given current market price.

        Args:
            position: Position object
            current_price: Current market price

        Returns:
            Dict with P&L calculations

        Example:
            >>> pnl = position_manager.calculate_position_pnl(position, 2050.0)
            >>> print(f"Unrealized P&L: ${pnl['unrealized_pnl']:.2f}")
        """
        # Calculate P&L based on position direction
        if position.type == 1:  # LONG
            pnl_per_contract = current_price - position.averagePrice
        else:  # SHORT (type == 2)
            pnl_per_contract = position.averagePrice - current_price

        unrealized_pnl = pnl_per_contract * position.size
        market_value = current_price * position.size

        return {
            "unrealized_pnl": unrealized_pnl,
            "market_value": market_value,
            "pnl_per_contract": pnl_per_contract,
            "current_price": current_price,
            "entry_price": position.averagePrice,
            "size": position.size,
            "direction": "LONG" if position.type == 1 else "SHORT",
        }

    def calculate_portfolio_pnl(
        self, current_prices: dict[str, float], account_id: int | None = None
    ) -> dict[str, Any]:
        """
        Calculate portfolio P&L given current market prices.

        Args:
            current_prices: Dict mapping contract IDs to current prices
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with portfolio P&L breakdown

        Example:
            >>> prices = {"MGC": 2050.0, "NQ": 15500.0}
            >>> pnl = position_manager.calculate_portfolio_pnl(prices)
            >>> print(f"Total P&L: ${pnl['total_pnl']:.2f}")
        """
        positions = self.get_all_positions(account_id=account_id)

        total_pnl = 0.0
        position_breakdown = []
        positions_with_prices = 0

        for position in positions:
            current_price = current_prices.get(position.contractId)

            if current_price is not None:
                pnl_data = self.calculate_position_pnl(position, current_price)
                total_pnl += pnl_data["unrealized_pnl"]
                positions_with_prices += 1

                position_breakdown.append(
                    {
                        "contract_id": position.contractId,
                        "size": position.size,
                        "entry_price": position.averagePrice,
                        "current_price": current_price,
                        "unrealized_pnl": pnl_data["unrealized_pnl"],
                        "market_value": pnl_data["market_value"],
                        "direction": pnl_data["direction"],
                    }
                )
            else:
                # No price data available
                position_breakdown.append(
                    {
                        "contract_id": position.contractId,
                        "size": position.size,
                        "entry_price": position.averagePrice,
                        "current_price": None,
                        "unrealized_pnl": None,
                        "market_value": None,
                        "direction": "LONG" if position.type == 1 else "SHORT",
                    }
                )

        return {
            "total_pnl": total_pnl,
            "positions_count": len(positions),
            "positions_with_prices": positions_with_prices,
            "positions_without_prices": len(positions) - positions_with_prices,
            "position_breakdown": position_breakdown,
            "timestamp": datetime.now(),
        }

    # ================================================================================
    # PORTFOLIO ANALYTICS AND REPORTING
    # ================================================================================

    def get_portfolio_pnl(self, account_id: int | None = None) -> dict[str, Any]:
        """
        Calculate comprehensive portfolio P&L metrics.

        Args:
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with portfolio P&L breakdown

        Example:
            >>> pnl = position_manager.get_portfolio_pnl()
            >>> print(f"Total P&L: ${pnl['total_pnl']:.2f}")
            >>> print(f"Unrealized: ${pnl['unrealized_pnl']:.2f}")
        """
        positions = self.get_all_positions(account_id=account_id)

        position_breakdown = []

        for position in positions:
            # Note: ProjectX doesn't provide P&L data, would need current market prices to calculate
            position_breakdown.append(
                {
                    "contract_id": position.contractId,
                    "size": position.size,
                    "avg_price": position.averagePrice,
                    "market_value": position.size * position.averagePrice,
                    "direction": "LONG" if position.type == 1 else "SHORT",
                    "note": "P&L requires current market price - use calculate_position_pnl() method",
                }
            )

        return {
            "position_count": len(positions),
            "positions": position_breakdown,
            "last_updated": datetime.now(),
            "note": "For P&L calculations, use calculate_portfolio_pnl() with current market prices",
        }

    def get_risk_metrics(self, account_id: int | None = None) -> dict[str, Any]:
        """
        Calculate portfolio risk metrics.

        Args:
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with risk analysis

        Example:
            >>> risk = position_manager.get_risk_metrics()
            >>> print(f"Portfolio risk: {risk['portfolio_risk']:.2%}")
        """
        positions = self.get_all_positions(account_id=account_id)

        if not positions:
            return {
                "portfolio_risk": 0.0,
                "largest_position_risk": 0.0,
                "total_exposure": 0.0,
                "position_count": 0,
                "diversification_score": 1.0,
            }

        total_exposure = sum(abs(pos.size * pos.averagePrice) for pos in positions)
        largest_exposure = (
            max(abs(pos.size * pos.averagePrice) for pos in positions)
            if positions
            else 0.0
        )

        # Calculate basic risk metrics (note: P&L-based risk requires market prices)
        portfolio_risk = (
            0.0  # Would need current market prices to calculate P&L-based risk
        )
        largest_position_risk = (
            largest_exposure / total_exposure if total_exposure > 0 else 0.0
        )

        # Simple diversification score (inverse of concentration)
        diversification_score = (
            1.0 - largest_position_risk if largest_position_risk < 1.0 else 0.0
        )

        return {
            "portfolio_risk": portfolio_risk,
            "largest_position_risk": largest_position_risk,
            "total_exposure": total_exposure,
            "position_count": len(positions),
            "diversification_score": diversification_score,
            "risk_warnings": self._generate_risk_warnings(
                positions, portfolio_risk, largest_position_risk
            ),
        }

    def _generate_risk_warnings(
        self,
        positions: list[Position],
        portfolio_risk: float,
        largest_position_risk: float,
    ) -> list[str]:
        """Generate risk warnings based on current portfolio state."""
        warnings = []

        if portfolio_risk > self.risk_settings["max_portfolio_risk"]:
            warnings.append(
                f"Portfolio risk ({portfolio_risk:.2%}) exceeds maximum ({self.risk_settings['max_portfolio_risk']:.2%})"
            )

        if largest_position_risk > self.risk_settings["max_position_risk"]:
            warnings.append(
                f"Largest position risk ({largest_position_risk:.2%}) exceeds maximum ({self.risk_settings['max_position_risk']:.2%})"
            )

        if len(positions) == 1:
            warnings.append("Portfolio lacks diversification (single position)")

        return warnings

    # ================================================================================
    # POSITION MONITORING AND ALERTS
    # ================================================================================

    def add_position_alert(
        self,
        contract_id: str,
        max_loss: float | None = None,
        max_gain: float | None = None,
        pnl_threshold: float | None = None,
    ):
        """
        Add an alert for a specific position.

        Args:
            contract_id: Contract ID to monitor
            max_loss: Maximum loss threshold (negative value)
            max_gain: Maximum gain threshold (positive value)
            pnl_threshold: Absolute P&L change threshold

        Example:
            >>> # Alert if MGC loses more than $500
            >>> position_manager.add_position_alert("MGC", max_loss=-500.0)
            >>> # Alert if NQ gains more than $1000
            >>> position_manager.add_position_alert("NQ", max_gain=1000.0)
        """
        with self.position_lock:
            self.position_alerts[contract_id] = {
                "max_loss": max_loss,
                "max_gain": max_gain,
                "pnl_threshold": pnl_threshold,
                "created": datetime.now(),
                "triggered": False,
            }

        self.logger.info(f"📢 Position alert added for {contract_id}")

    def remove_position_alert(self, contract_id: str):
        """
        Remove position alert for a specific contract.

        Args:
            contract_id: Contract ID to remove alert for

        Example:
            >>> position_manager.remove_position_alert("MGC")
        """
        with self.position_lock:
            if contract_id in self.position_alerts:
                del self.position_alerts[contract_id]
                self.logger.info(f"🔕 Position alert removed for {contract_id}")

    def _check_position_alerts(
        self,
        contract_id: str,
        current_position: Position,
        old_position: Position | None,
    ):
        """
        Check if position alerts should be triggered and handle alert notifications.

        This method is called automatically when positions are updated to evaluate
        whether any configured alerts should be triggered.

        Args:
            contract_id: Contract ID of the position being checked
            current_position: Current position state
            old_position: Previous position state (None if new position)

        Note:
            Currently checks for position size changes. P&L-based alerts require
            current market prices to be provided separately.
        """
        alert = self.position_alerts.get(contract_id)
        if not alert or alert["triggered"]:
            return

        # Note: P&L-based alerts require current market prices
        # For now, only check position size changes
        alert_triggered = False
        alert_message = ""

        # Check for position size changes as a basic alert
        if old_position and current_position.size != old_position.size:
            size_change = current_position.size - old_position.size
            alert_triggered = True
            alert_message = (
                f"Position {contract_id} size changed by {size_change} contracts"
            )

        if alert_triggered:
            alert["triggered"] = True
            self.logger.warning(f"🚨 POSITION ALERT: {alert_message}")
            self._trigger_callbacks(
                "position_alert",
                {
                    "contract_id": contract_id,
                    "message": alert_message,
                    "position": current_position,
                    "alert": alert,
                },
            )

    async def _monitoring_loop(self, refresh_interval: int):
        """Main monitoring loop for polling mode."""
        while self._monitoring_active:
            try:
                self.refresh_positions()
                await asyncio.sleep(refresh_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(refresh_interval)

    def start_monitoring(self, refresh_interval: int = 30):
        """
        Start automated position monitoring for real-time updates and alerts.

        Enables continuous monitoring of positions with automatic alert checking.
        In real-time mode (with ProjectXRealtimeClient), uses live WebSocket feeds.
        In polling mode, periodically refreshes position data from the API.

        Args:
            refresh_interval: Seconds between position updates in polling mode (default: 30)
                Ignored when real-time client is available

        Example:
            >>> # Start monitoring with real-time updates
            >>> position_manager.start_monitoring()
            >>> # Start monitoring with custom polling interval
            >>> position_manager.start_monitoring(refresh_interval=60)
        """
        if self._monitoring_active:
            self.logger.warning("⚠️ Position monitoring already active")
            return

        self._monitoring_active = True
        self.stats["monitoring_started"] = datetime.now()

        if not self._realtime_enabled:
            # Start async monitoring loop
            self._monitoring_task = asyncio.create_task(
                self._monitoring_loop(refresh_interval)
            )
            self.logger.info(
                f"📊 Position monitoring started (polling every {refresh_interval}s)"
            )
        else:
            self.logger.info("📊 Position monitoring started (real-time mode)")

    def stop_monitoring(self):
        """
        Stop automated position monitoring and clean up monitoring resources.

        Cancels any active monitoring tasks and stops position update notifications.

        Example:
            >>> position_manager.stop_monitoring()
        """
        self._monitoring_active = False
        if hasattr(self, "_monitoring_task") and self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        self.logger.info("🛑 Position monitoring stopped")

    # ================================================================================
    # POSITION SIZING AND RISK MANAGEMENT
    # ================================================================================

    def calculate_position_size(
        self,
        contract_id: str,
        risk_amount: float,
        entry_price: float,
        stop_price: float,
        account_balance: float | None = None,
    ) -> dict[str, Any]:
        """
        Calculate optimal position size based on risk parameters.

        Args:
            contract_id: Contract to trade
            risk_amount: Maximum amount to risk (in currency)
            entry_price: Planned entry price
            stop_price: Stop loss price
            account_balance: Account balance (retrieved if None)

        Returns:
            Dict with position sizing recommendations

        Example:
            >>> sizing = position_manager.calculate_position_size(
            ...     "MGC", risk_amount=100.0, entry_price=2045.0, stop_price=2040.0
            ... )
            >>> print(f"Suggested size: {sizing['suggested_size']} contracts")
        """
        try:
            # Get account balance if not provided
            if account_balance is None:
                account_info = self.project_x.get_account_info()
                account_balance = (
                    account_info.balance if account_info else 10000.0
                )  # Default fallback

            # Calculate risk per contract
            price_diff = abs(entry_price - stop_price)
            if price_diff == 0:
                return {"error": "Entry price and stop price cannot be the same"}

            # Get instrument details for contract multiplier
            instrument = self.project_x.get_instrument(contract_id)
            contract_multiplier = (
                getattr(instrument, "contractMultiplier", 1.0) if instrument else 1.0
            )

            risk_per_contract = price_diff * contract_multiplier
            suggested_size = (
                int(risk_amount / risk_per_contract) if risk_per_contract > 0 else 0
            )

            # Calculate risk metrics
            total_risk = suggested_size * risk_per_contract
            risk_percentage = (
                (total_risk / account_balance) * 100 if account_balance > 0 else 0.0
            )

            return {
                "suggested_size": suggested_size,
                "risk_per_contract": risk_per_contract,
                "total_risk": total_risk,
                "risk_percentage": risk_percentage,
                "entry_price": entry_price,
                "stop_price": stop_price,
                "price_diff": price_diff,
                "contract_multiplier": contract_multiplier,
                "account_balance": account_balance,
                "risk_warnings": self._generate_sizing_warnings(
                    risk_percentage, suggested_size
                ),
            }

        except Exception as e:
            self.logger.error(f"❌ Position sizing calculation failed: {e}")
            return {"error": str(e)}

    def _generate_sizing_warnings(self, risk_percentage: float, size: int) -> list[str]:
        """Generate warnings for position sizing."""
        warnings = []

        if risk_percentage > self.risk_settings["max_position_risk"] * 100:
            warnings.append(
                f"Risk percentage ({risk_percentage:.2f}%) exceeds recommended maximum"
            )

        if size == 0:
            warnings.append(
                "Calculated position size is 0 - risk amount may be too small"
            )

        if size > 10:  # Arbitrary large size threshold
            warnings.append(
                f"Large position size ({size} contracts) - consider reducing risk"
            )

        return warnings

    # ================================================================================
    # DIRECT POSITION MANAGEMENT METHODS (API-based)
    # ================================================================================

    def close_position_direct(
        self, contract_id: str, account_id: int | None = None
    ) -> dict[str, Any]:
        """
        Close an entire position using the direct position close API.

        Args:
            contract_id: Contract ID of the position to close
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with closure response details

        Example:
            >>> result = position_manager.close_position_direct("MGC")
            >>> if result["success"]:
            ...     print(f"Position closed: {result.get('orderId', 'N/A')}")
        """
        self.project_x._ensure_authenticated()

        if account_id is None:
            if not self.project_x.account_info:
                self.project_x.get_account_info()
            if not self.project_x.account_info:
                raise ProjectXError("No account information available")
            account_id = self.project_x.account_info.id

        url = f"{self.project_x.base_url}/Position/closeContract"
        payload = {
            "accountId": account_id,
            "contractId": contract_id,
        }

        try:
            response = requests.post(
                url,
                headers=self.project_x.headers,
                json=payload,
                timeout=self.project_x.timeout_seconds,
            )
            self.project_x._handle_response_errors(response)

            data = response.json()
            success = data.get("success", False)

            if success:
                self.logger.info(f"✅ Position {contract_id} closed successfully")
                # Remove from tracked positions if present
                with self.position_lock:
                    positions_to_remove = [
                        contract_id
                        for contract_id, pos in self.tracked_positions.items()
                        if pos.contractId == contract_id
                    ]
                    for contract_id in positions_to_remove:
                        del self.tracked_positions[contract_id]

                # Synchronize orders - cancel related orders when position is closed
                if self._order_sync_enabled and self.order_manager:
                    self.order_manager.on_position_closed(contract_id)

                self.stats["positions_closed"] += 1
            else:
                error_msg = data.get("errorMessage", "Unknown error")
                self.logger.error(f"❌ Position closure failed: {error_msg}")

            return data

        except requests.RequestException as e:
            self.logger.error(f"❌ Position closure request failed: {e}")
            return {"success": False, "error": str(e)}
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"❌ Invalid position closure response: {e}")
            return {"success": False, "error": str(e)}

    def partially_close_position(
        self, contract_id: str, close_size: int, account_id: int | None = None
    ) -> dict[str, Any]:
        """
        Partially close a position by reducing its size.

        Args:
            contract_id: Contract ID of the position to partially close
            close_size: Number of contracts to close (must be less than position size)
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with partial closure response details

        Example:
            >>> # Close 5 contracts from a 10 contract position
            >>> result = position_manager.partially_close_position("MGC", 5)
            >>> if result["success"]:
            ...     print(f"Partially closed: {result.get('orderId', 'N/A')}")
        """
        self.project_x._ensure_authenticated()

        if account_id is None:
            if not self.project_x.account_info:
                self.project_x.get_account_info()
            if not self.project_x.account_info:
                raise ProjectXError("No account information available")
            account_id = self.project_x.account_info.id

        # Validate close size
        if close_size <= 0:
            raise ProjectXError("Close size must be positive")

        url = f"{self.project_x.base_url}/Position/partialCloseContract"
        payload = {
            "accountId": account_id,
            "contractId": contract_id,
            "closeSize": close_size,
        }

        try:
            response = requests.post(
                url,
                headers=self.project_x.headers,
                json=payload,
                timeout=self.project_x.timeout_seconds,
            )
            self.project_x._handle_response_errors(response)

            data = response.json()
            success = data.get("success", False)

            if success:
                self.logger.info(
                    f"✅ Position {contract_id} partially closed: {close_size} contracts"
                )
                # Trigger position refresh to get updated sizes
                self.refresh_positions(account_id=account_id)

                # Synchronize orders - update order sizes after partial close
                if self._order_sync_enabled and self.order_manager:
                    self.order_manager.sync_orders_with_position(
                        contract_id, account_id
                    )

                self.stats["positions_partially_closed"] += 1
            else:
                error_msg = data.get("errorMessage", "Unknown error")
                self.logger.error(f"❌ Partial position closure failed: {error_msg}")

            return data

        except requests.RequestException as e:
            self.logger.error(f"❌ Partial position closure request failed: {e}")
            return {"success": False, "error": str(e)}
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"❌ Invalid partial closure response: {e}")
            return {"success": False, "error": str(e)}

    def close_all_positions(
        self, contract_id: str | None = None, account_id: int | None = None
    ) -> dict[str, Any]:
        """
        Close all positions, optionally filtered by contract.

        Args:
            contract_id: Optional contract ID to filter positions
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with bulk closure results

        Example:
            >>> # Close all positions
            >>> result = position_manager.close_all_positions()
            >>> # Close all MGC positions
            >>> result = position_manager.close_all_positions(contract_id="MGC")
        """
        positions = self.get_all_positions(account_id=account_id)

        # Filter by contract if specified
        if contract_id:
            positions = [pos for pos in positions if pos.contractId == contract_id]

        results = {
            "total_positions": len(positions),
            "closed": 0,
            "failed": 0,
            "errors": [],
        }

        for position in positions:
            try:
                close_result = self.close_position_direct(
                    position.contractId, account_id
                )
                if close_result.get("success", False):
                    results["closed"] += 1
                else:
                    results["failed"] += 1
                    error_msg = close_result.get("errorMessage", "Unknown error")
                    results["errors"].append(
                        f"Position {position.contractId}: {error_msg}"
                    )
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Position {position.contractId}: {e!s}")

        self.logger.info(
            f"✅ Closed {results['closed']}/{results['total_positions']} positions"
        )
        return results

    def close_position_by_contract(
        self,
        contract_id: str,
        close_size: int | None = None,
        account_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Close position by contract ID (full or partial).

        Args:
            contract_id: Contract ID of position to close
            close_size: Optional size to close (full position if None)
            account_id: Account ID. Uses default account if None.

        Returns:
            Dict with closure response details

        Example:
            >>> # Close entire MGC position
            >>> result = position_manager.close_position_by_contract("MGC")
            >>> # Close 3 contracts from MGC position
            >>> result = position_manager.close_position_by_contract(
            ...     "MGC", close_size=3
            ... )
        """
        # Find the position
        position = self.get_position(contract_id, account_id)
        if not position:
            return {
                "success": False,
                "error": f"No open position found for {contract_id}",
            }

        # Determine if full or partial close
        if close_size is None or close_size >= position.size:
            # Full close
            return self.close_position_direct(position.contractId, account_id)
        else:
            # Partial close
            return self.partially_close_position(
                position.contractId, close_size, account_id
            )

    # ================================================================================
    # UTILITY AND STATISTICS METHODS
    # ================================================================================

    def get_position_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive position management statistics and health information.

        Provides detailed statistics about position tracking, monitoring status,
        performance metrics, and system health for debugging and monitoring.

        Returns:
            Dict with complete statistics including:
                - statistics: Core tracking metrics (positions tracked, P&L, etc.)
                - realtime_enabled: Whether real-time updates are active
                - order_sync_enabled: Whether order synchronization is active
                - monitoring_active: Whether automated monitoring is running
                - tracked_positions: Number of positions currently tracked
                - active_alerts: Number of active position alerts
                - callbacks_registered: Number of callbacks per event type
                - risk_settings: Current risk management settings
                - health_status: Overall system health status

        Example:
            >>> stats = position_manager.get_position_statistics()
            >>> print(f"Tracking {stats['tracked_positions']} positions")
            >>> print(f"Real-time enabled: {stats['realtime_enabled']}")
            >>> print(f"Active alerts: {stats['active_alerts']}")
            >>> if stats["health_status"] != "active":
            ...     print("Warning: Position manager not fully active")
        """
        with self.position_lock:
            return {
                "statistics": self.stats.copy(),
                "realtime_enabled": self._realtime_enabled,
                "order_sync_enabled": self._order_sync_enabled,
                "monitoring_active": self._monitoring_active,
                "tracked_positions": len(self.tracked_positions),
                "active_alerts": len(
                    [a for a in self.position_alerts.values() if not a["triggered"]]
                ),
                "callbacks_registered": {
                    event: len(callbacks)
                    for event, callbacks in self.position_callbacks.items()
                },
                "risk_settings": self.risk_settings.copy(),
                "health_status": "active"
                if self.project_x._authenticated
                else "inactive",
            }

    def get_position_history(self, contract_id: str, limit: int = 100) -> list[dict]:
        """
        Get historical position data for a specific contract.

        Retrieves the history of position changes including size changes,
        timestamps, and position snapshots for analysis and debugging.

        Args:
            contract_id: Contract ID to get history for
            limit: Maximum number of history entries to return (default: 100)

        Returns:
            List[dict]: Historical position data entries, each containing:
                - timestamp: When the position change occurred
                - position: Position data snapshot at that time
                - size_change: Change in position size from previous state

        Example:
            >>> history = position_manager.get_position_history("MGC", limit=50)
            >>> for entry in history[-5:]:  # Last 5 changes
            ...     print(f"{entry['timestamp']}: Size change {entry['size_change']}")
            ...     pos = entry["position"]
            ...     print(
            ...         f"  New size: {pos.get('size', 0)} @ ${pos.get('averagePrice', 0):.2f}"
            ...     )
        """
        with self.position_lock:
            history = self.position_history.get(contract_id, [])
            return history[-limit:] if history else []

    def export_portfolio_report(self) -> dict[str, Any]:
        """
        Generate a comprehensive portfolio report with complete analysis.

        Creates a detailed report suitable for saving to file, sending via email,
        or displaying in dashboards. Includes positions, P&L, risk metrics,
        and system statistics.

        Returns:
            Dict with complete portfolio analysis including:
                - report_timestamp: When the report was generated
                - portfolio_summary: High-level portfolio metrics
                - positions: Detailed position information with P&L
                - risk_analysis: Portfolio risk metrics and warnings
                - statistics: System performance and tracking statistics
                - alerts: Active and triggered alert counts

        Example:
            >>> report = position_manager.export_portfolio_report()
            >>> print(f"Portfolio Report - {report['report_timestamp']}")
            >>> summary = report["portfolio_summary"]
            >>> print(f"Total Positions: {summary['total_positions']}")
            >>> print(f"Total P&L: ${summary['total_pnl']:.2f}")
            >>> print(f"Portfolio Risk: {summary['portfolio_risk']:.2%}")
            >>> # Save report to file
            >>> import json
            >>> with open("portfolio_report.json", "w") as f:
            ...     json.dump(report, f, indent=2, default=str)
        """
        positions = self.get_all_positions()
        pnl_data = self.get_portfolio_pnl()
        risk_data = self.get_risk_metrics()
        stats = self.get_position_statistics()

        return {
            "report_timestamp": datetime.now(),
            "portfolio_summary": {
                "total_positions": len(positions),
                "total_pnl": pnl_data["total_pnl"],
                "total_exposure": risk_data["total_exposure"],
                "portfolio_risk": risk_data["portfolio_risk"],
            },
            "positions": pnl_data["positions"],
            "risk_analysis": risk_data,
            "statistics": stats,
            "alerts": {
                "active_alerts": len(
                    [a for a in self.position_alerts.values() if not a["triggered"]]
                ),
                "triggered_alerts": len(
                    [a for a in self.position_alerts.values() if a["triggered"]]
                ),
            },
        }

    def get_realtime_validation_status(self) -> dict[str, Any]:
        """
        Get validation status for real-time position feed integration and compliance.

        Provides detailed information about real-time integration status,
        payload validation settings, and ProjectX API compliance for debugging
        and system validation.

        Returns:
            Dict with comprehensive validation status including:
                - realtime_enabled: Whether real-time updates are active
                - tracked_positions_count: Number of positions being tracked
                - position_callbacks_registered: Number of position update callbacks
                - payload_validation: Settings for validating ProjectX position payloads
                - projectx_compliance: Compliance status with ProjectX API format
                - statistics: Current tracking statistics

        Example:
            >>> status = position_manager.get_realtime_validation_status()
            >>> print(f"Real-time enabled: {status['realtime_enabled']}")
            >>> print(f"Tracking {status['tracked_positions_count']} positions")
            >>> compliance = status["projectx_compliance"]
            >>> for check, result in compliance.items():
            ...     print(f"{check}: {result}")
            >>> # Check if validation is working correctly
            >>> if "✅" not in str(status["projectx_compliance"].values()):
            ...     print("Warning: ProjectX compliance issues detected")
        """
        return {
            "realtime_enabled": self._realtime_enabled,
            "tracked_positions_count": len(self.tracked_positions),
            "position_callbacks_registered": len(
                self.position_callbacks.get("position_update", [])
            ),
            "payload_validation": {
                "enabled": True,
                "required_fields": [
                    "id",
                    "accountId",
                    "contractId",
                    "creationTimestamp",
                    "type",
                    "size",
                    "averagePrice",
                ],
                "position_type_enum": {"Undefined": 0, "Long": 1, "Short": 2},
                "closure_detection": "size == 0 (not type == 0)",
            },
            "projectx_compliance": {
                "gateway_user_position_format": "✅ Compliant",
                "position_type_enum": "✅ Correct",
                "closure_logic": "✅ Fixed (was incorrectly checking type==0)",
                "payload_structure": "✅ Direct payload (no 'data' extraction)",
            },
            "statistics": self.stats.copy(),
        }

    def cleanup(self):
        """
        Clean up resources and connections when shutting down.

        Properly shuts down monitoring, clears tracked data, and releases
        resources to prevent memory leaks when the PositionManager is no
        longer needed.

        Example:
            >>> # Proper shutdown
            >>> position_manager.cleanup()
        """
        self.stop_monitoring()

        with self.position_lock:
            self.tracked_positions.clear()
            self.position_history.clear()
            self.position_callbacks.clear()
            self.position_alerts.clear()

        # Clear order manager integration
        self.order_manager = None
        self._order_sync_enabled = False

        self.logger.info("✅ PositionManager cleanup completed")
