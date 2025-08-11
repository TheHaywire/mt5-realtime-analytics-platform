#!/usr/bin/env python3
"""
MT5 Service - Real-time MetaTrader 5 data connection and streaming
Handles live tick data ingestion, bar aggregation, and market data
"""

import asyncio
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import pytz
from collections import defaultdict

from core.config import settings
from models.database import SessionLocal
from models.schemas import TickData, BarData

logger = logging.getLogger(__name__)

@dataclass
class MarketTick:
    """Market tick data structure"""
    symbol: str
    time: datetime
    bid: float
    ask: float
    volume: int
    spread: float

@dataclass 
class OHLCV:
    """OHLCV bar data structure"""
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime

class BarAggregator:
    """Real-time bar aggregation from tick data"""
    
    def __init__(self):
        self.current_bars = {}  # symbol -> current bar data
        self.bar_callbacks = []
        
    def add_tick(self, tick: MarketTick):
        """Add tick to current bar aggregation"""
        symbol = tick.symbol
        minute_key = tick.time.replace(second=0, microsecond=0)
        
        if symbol not in self.current_bars:
            self.current_bars[symbol] = {}
            
        if minute_key not in self.current_bars[symbol]:
            # Start new bar
            mid_price = (tick.bid + tick.ask) / 2
            self.current_bars[symbol][minute_key] = {
                'open': mid_price,
                'high': mid_price,
                'low': mid_price,
                'close': mid_price,
                'volume': tick.volume,
                'tick_count': 1,
                'timestamp': minute_key
            }
        else:
            # Update existing bar
            bar = self.current_bars[symbol][minute_key]
            mid_price = (tick.bid + tick.ask) / 2
            
            bar['high'] = max(bar['high'], mid_price)
            bar['low'] = min(bar['low'], mid_price)
            bar['close'] = mid_price
            bar['volume'] += tick.volume
            bar['tick_count'] += 1
            
        # Check if bar is complete (next minute started)
        current_minute = datetime.now().replace(second=0, microsecond=0)
        if minute_key < current_minute:
            self._emit_completed_bar(symbol, minute_key)
            
    def _emit_completed_bar(self, symbol: str, minute_key: datetime):
        """Emit completed bar to callbacks"""
        if symbol in self.current_bars and minute_key in self.current_bars[symbol]:
            bar_data = self.current_bars[symbol][minute_key]
            
            ohlcv = OHLCV(
                symbol=symbol,
                timeframe="M1",
                open=bar_data['open'],
                high=bar_data['high'],
                low=bar_data['low'],
                close=bar_data['close'],
                volume=bar_data['volume'],
                timestamp=bar_data['timestamp']
            )
            
            # Call all registered callbacks
            for callback in self.bar_callbacks:
                asyncio.create_task(callback(ohlcv))
                
            # Clean up completed bar
            del self.current_bars[symbol][minute_key]

class MT5Service:
    """MetaTrader 5 service for real-time data"""
    
    def __init__(self):
        self.connected = False
        self.streaming = False
        self.symbols = settings.MT5_SYMBOLS.split(",")
        self.bar_aggregator = BarAggregator()
        self.tick_callbacks = []
        self.bar_callbacks = []
        
        # IST timezone for display
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        
    async def connect(self) -> bool:
        """Connect to MetaTrader 5"""
        try:
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return False
                
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return False
                
            logger.info(f"Connected to MT5 account: {account_info.login}")
            logger.info(f"Server: {account_info.server}")
            logger.info(f"Balance: ${account_info.balance:.2f}")
            
            self.connected = True
            
            # Register bar callback for database storage
            self.bar_aggregator.bar_callbacks.append(self._store_bar_in_db)
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
            
    async def disconnect(self):
        """Disconnect from MetaTrader 5"""
        self.streaming = False
        self.connected = False
        mt5.shutdown()
        logger.info("Disconnected from MT5")
        
    def is_connected(self) -> bool:
        """Check if MT5 is connected"""
        return self.connected and mt5.terminal_info() is not None
        
    async def start_data_stream(self):
        """Start real-time tick data streaming"""
        if not self.connected:
            logger.error("MT5 not connected - cannot start streaming")
            return
            
        self.streaming = True
        logger.info(f"Starting tick data stream for symbols: {self.symbols}")
        
        while self.streaming:
            try:
                for symbol in self.symbols:
                    # Get latest ticks
                    ticks = mt5.copy_ticks_from(
                        symbol, 
                        datetime.now() - timedelta(seconds=1), 
                        100,
                        mt5.COPY_TICKS_ALL
                    )
                    
                    if ticks is not None and len(ticks) > 0:
                        for tick_data in ticks:
                            # Convert to our tick format
                            tick = MarketTick(
                                symbol=symbol,
                                time=datetime.fromtimestamp(tick_data.time),
                                bid=tick_data.bid,
                                ask=tick_data.ask,
                                volume=getattr(tick_data, 'volume', 1),
                                spread=(tick_data.ask - tick_data.bid)
                            )
                            
                            # Process tick
                            await self._process_tick(tick)
                            
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.1)  # 100ms
                
            except Exception as e:
                logger.error(f"Error in data stream: {e}")
                await asyncio.sleep(1)
                
    async def _process_tick(self, tick: MarketTick):
        """Process incoming tick data"""
        # Add to bar aggregator
        self.bar_aggregator.add_tick(tick)
        
        # Call tick callbacks
        for callback in self.tick_callbacks:
            await callback(tick)
            
    async def _store_bar_in_db(self, bar: OHLCV):
        """Store completed bar in database"""
        try:
            db = SessionLocal()
            
            # Convert to database model
            bar_data = BarData(
                symbol=bar.symbol,
                timeframe=bar.timeframe,
                open_price=bar.open,
                high_price=bar.high,
                low_price=bar.low,
                close_price=bar.close,
                volume=bar.volume,
                timestamp=bar.timestamp,
                created_at=datetime.utcnow()
            )
            
            db.add(bar_data)
            db.commit()
            
            logger.debug(f"Stored bar: {bar.symbol} {bar.timestamp}")
            
        except Exception as e:
            logger.error(f"Error storing bar in DB: {e}")
        finally:
            db.close()
            
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current market price"""
        if not self.is_connected():
            # Return mock data for demo
            return {
                "bid": 2045.50,
                "ask": 2045.65,
                "spread": 0.15,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                raise ValueError(f"No tick data for symbol {symbol}")
                
            return {
                "bid": tick.bid,
                "ask": tick.ask,
                "spread": tick.ask - tick.bid,
                "timestamp": datetime.fromtimestamp(tick.time).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            raise
            
    async def get_bars(self, symbol: str, timeframe: str, count: int) -> List[Dict]:
        """Get historical OHLCV bars"""
        if not self.is_connected():
            # Return mock data for demo
            return self._generate_mock_bars(symbol, count)
            
        try:
            # Map timeframe string to MT5 constant
            tf_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_M1)
            
            # Get rates
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None:
                logger.warning(f"No rates data for {symbol} {timeframe}")
                return []
                
            # Convert to our format
            bars = []
            for rate in rates:
                # Convert to IST for display
                utc_time = datetime.fromtimestamp(rate['time'], tz=pytz.UTC)
                ist_time = utc_time.astimezone(self.ist_tz)
                
                bars.append({
                    "timestamp": utc_time.isoformat(),
                    "timestamp_ist": ist_time.isoformat(),
                    "open": rate['open'],
                    "high": rate['high'],
                    "low": rate['low'],
                    "close": rate['close'],
                    "volume": rate['tick_volume'],
                    "spread": rate.get('spread', 0)
                })
                
            return bars
            
        except Exception as e:
            logger.error(f"Error getting bars: {e}")
            return []
            
    def _generate_mock_bars(self, symbol: str, count: int) -> List[Dict]:
        """Generate mock OHLCV data for demo mode"""
        bars = []
        base_price = 2045.0
        
        for i in range(count):
            # Simulate price movement
            price_change = np.random.normal(0, 0.5)  # Small random changes
            base_price += price_change
            
            # Generate OHLC with some randomness
            open_price = base_price
            close_price = base_price + np.random.normal(0, 0.3)
            high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.2))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.2))
            
            timestamp = datetime.utcnow() - timedelta(minutes=count-i)
            ist_time = timestamp.replace(tzinfo=pytz.UTC).astimezone(self.ist_tz)
            
            bars.append({
                "timestamp": timestamp.isoformat(),
                "timestamp_ist": ist_time.isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": np.random.randint(50, 200),
                "spread": round(np.random.uniform(0.1, 0.3), 2)
            })
            
        return bars
        
    async def get_account_info(self) -> Dict[str, Any]:
        """Get MT5 account information"""
        if not self.is_connected():
            return {
                "login": "DEMO",
                "server": "Demo Server",
                "balance": 10000.0,
                "equity": 10000.0,
                "margin": 0.0,
                "free_margin": 10000.0,
                "currency": "USD"
            }
            
        try:
            account = mt5.account_info()
            if account is None:
                raise ValueError("Could not get account info")
                
            return {
                "login": account.login,
                "server": account.server, 
                "balance": account.balance,
                "equity": account.equity,
                "margin": account.margin,
                "free_margin": account.margin_free,
                "currency": account.currency
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
            
    def add_tick_callback(self, callback):
        """Add callback for tick data"""
        self.tick_callbacks.append(callback)
        
    def add_bar_callback(self, callback):
        """Add callback for bar data"""
        self.bar_callbacks.append(callback)
        
    async def get_server_time(self) -> Dict[str, str]:
        """Get server time and IST equivalent"""
        if self.is_connected():
            # Get MT5 server time
            terminal_info = mt5.terminal_info()
            server_time = datetime.fromtimestamp(terminal_info.time)
        else:
            server_time = datetime.utcnow()
            
        # Convert to IST
        server_time_utc = server_time.replace(tzinfo=pytz.UTC)
        ist_time = server_time_utc.astimezone(self.ist_tz)
        
        return {
            "server_time": server_time.isoformat(),
            "server_time_ist": ist_time.isoformat(),
            "timezone": "Asia/Kolkata"
        }