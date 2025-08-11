#!/usr/bin/env python3
"""
REAL MT5 Service for Live Data Connection
Connects to live MT5 account and streams real tick/bar data
NO SYNTHETIC DATA - PURELY BUSINESS REAL TRADING DATA
"""

import MetaTrader5 as mt5
import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import os
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class MT5ServiceReal:
    """Real MT5 service for live trading data - NO MOCKS"""
    
    def __init__(self):
        self.connected = False
        self.streaming = False
        self.symbols = ["XAUUSD", "GOLD", "EURUSD", "GBPUSD"]  # Real trading symbols
        self.account_info = None
        self.live_rates = {}
        
        # Real MT5 credentials
        self.login = int(os.getenv('MT5_LIVE_LOGIN', '165835373'))
        self.password = os.getenv('MT5_LIVE_PASSWORD', 'Manan@123!!')
        self.server = os.getenv('MT5_LIVE_SERVER', 'XMGlobal-MT5 2')
        
        logger.info(f"Initializing REAL MT5 service for account {self.login} on {self.server}")
    
    async def connect(self) -> bool:
        """Connect to REAL MT5 terminal"""
        try:
            # Initialize MT5 connection
            if not mt5.initialize():
                logger.error("Failed to initialize MT5 terminal")
                return False
            
            # Connect to LIVE account
            authorized = mt5.login(self.login, password=self.password, server=self.server)
            if not authorized:
                logger.error(f"Failed to login to LIVE MT5 account {self.login}")
                return False
            
            # Get account information
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return False
            
            self.account_info = account_info._asdict()
            self.connected = True
            
            logger.info(f"SUCCESSFULLY CONNECTED TO LIVE MT5!")
            logger.info(f"Account: {account_info.login}")
            logger.info(f"Balance: ${account_info.balance:,.2f}")
            logger.info(f"Equity: ${account_info.equity:,.2f}")
            logger.info(f"Server: {account_info.server}")
            logger.info(f"Currency: {account_info.currency}")
            logger.info(f"Leverage: 1:{account_info.leverage}")
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    async def get_live_tick_data(self, symbol: str, count: int = 10) -> List[Dict]:
        """Get real live tick data from MT5"""
        if not self.connected:
            return []
        
        try:
            # Get last N ticks
            ticks = mt5.copy_ticks_from(symbol, datetime.now(), count, mt5.COPY_TICKS_ALL)
            
            if ticks is None or len(ticks) == 0:
                return []
            
            tick_data = []
            for tick in ticks:
                tick_data.append({
                    'symbol': symbol,
                    'time': datetime.fromtimestamp(tick.time, tz=timezone.utc),
                    'bid': float(tick.bid),
                    'ask': float(tick.ask),
                    'last': float(tick.last),
                    'volume': int(tick.volume),
                    'spread': float(tick.ask - tick.bid),
                    'flags': int(tick.flags)
                })
            
            return tick_data
            
        except Exception as e:
            logger.error(f"Error getting tick data for {symbol}: {e}")
            return []
    
    async def get_live_rates(self, symbols: List[str] = None) -> Dict[str, Dict]:
        """Get current live rates for symbols"""
        if not self.connected:
            return {}
        
        if symbols is None:
            symbols = self.symbols
        
        rates = {}
        for symbol in symbols:
            try:
                symbol_info = mt5.symbol_info_tick(symbol)
                if symbol_info is not None:
                    rates[symbol] = {
                        'time': datetime.fromtimestamp(symbol_info.time, tz=timezone.utc),
                        'bid': float(symbol_info.bid),
                        'ask': float(symbol_info.ask),
                        'last': float(symbol_info.last),
                        'volume': int(symbol_info.volume),
                        'spread': float(symbol_info.ask - symbol_info.bid),
                        'spread_points': int(symbol_info.ask - symbol_info.bid) * 10000
                    }
            except Exception as e:
                logger.error(f"Error getting rates for {symbol}: {e}")
        
        return rates
    
    async def get_historical_bars(self, symbol: str, timeframe: str = "M1", count: int = 1000) -> pd.DataFrame:
        """Get real historical bar data"""
        if not self.connected:
            return pd.DataFrame()
        
        try:
            # Map timeframe
            tf_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_M1)
            
            # Get bars
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                logger.warning(f"No historical data available for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Rename columns
            df.rename(columns={
                'open': 'open_price',
                'high': 'high_price', 
                'low': 'low_price',
                'close': 'close_price',
                'tick_volume': 'volume'
            }, inplace=True)
            
            logger.info(f"Retrieved {len(df)} bars for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def analyze_time_patterns(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Analyze real time-based patterns from live data"""
        if not self.connected:
            return {}
        
        try:
            # Get 30 days of M1 data
            df = await self.get_historical_bars(symbol, "M1", count=43200)  # 30 days * 24 hours * 60 minutes
            
            if df.empty:
                return {}
            
            # Calculate returns
            df['returns'] = df['close_price'].pct_change()
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.day_name()
            df['minute'] = df.index.minute
            
            # Time-based analysis
            patterns = {}
            
            # Hour-by-hour analysis
            hourly_stats = df.groupby('hour').agg({
                'returns': ['count', 'mean', 'std', lambda x: (x > 0).sum() / len(x)]
            }).round(4)
            
            patterns['hourly'] = {}
            for hour in range(24):
                if hour in hourly_stats.index:
                    stats = hourly_stats.loc[hour]
                    patterns['hourly'][f"{hour:02d}:00"] = {
                        'sample_size': int(stats[('returns', 'count')]),
                        'avg_return': float(stats[('returns', 'mean')] * 100),
                        'win_rate': float(stats[('returns', '<lambda>')] * 100),
                        'volatility': float(stats[('returns', 'std')] * 100),
                        'significance': 'high' if stats[('returns', 'count')] > 100 else 'low'
                    }
            
            # Day of week analysis
            daily_stats = df.groupby('day_of_week').agg({
                'returns': ['count', 'mean', 'std', lambda x: (x > 0).sum() / len(x)]
            }).round(4)
            
            patterns['daily'] = {}
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                if day in daily_stats.index:
                    stats = daily_stats.loc[day]
                    patterns['daily'][day] = {
                        'sample_size': int(stats[('returns', 'count')]),
                        'avg_return': float(stats[('returns', 'mean')] * 100),
                        'win_rate': float(stats[('returns', '<lambda>')] * 100),
                        'volatility': float(stats[('returns', 'std')] * 100)
                    }
            
            # Find best edges
            best_hours = []
            for hour, data in patterns['hourly'].items():
                if data['sample_size'] > 50 and data['win_rate'] > 55:
                    best_hours.append({
                        'time': hour,
                        'win_rate': data['win_rate'],
                        'avg_return': data['avg_return'],
                        'sample_size': data['sample_size']
                    })
            
            patterns['best_edges'] = sorted(best_hours, key=lambda x: x['win_rate'], reverse=True)[:5]
            patterns['analysis_period'] = {
                'from': df.index.min().isoformat(),
                'to': df.index.max().isoformat(),
                'total_bars': len(df)
            }
            
            logger.info(f"Analyzed {len(df)} real data points for {symbol}")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for {symbol}: {e}")
            return {}
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get real market status"""
        if not self.connected:
            return {'status': 'disconnected', 'message': 'Not connected to MT5'}
        
        try:
            # Check if market is open by getting current tick
            current_tick = mt5.symbol_info_tick("XAUUSD")
            
            if current_tick is None:
                return {'status': 'closed', 'message': 'Market is closed'}
            
            # Get server time
            server_time = datetime.fromtimestamp(current_tick.time, tz=timezone.utc)
            current_time = datetime.now(timezone.utc)
            
            # Check if data is fresh (within last 5 minutes)
            time_diff = (current_time - server_time).total_seconds()
            
            if time_diff > 300:  # 5 minutes
                status = 'closed'
                message = f'Market closed - Last tick: {server_time}'
            else:
                status = 'open'
                message = f'Market open - Live data flowing'
            
            return {
                'status': status,
                'message': message,
                'server_time': server_time.isoformat(),
                'local_time': current_time.isoformat(),
                'account_balance': self.account_info['balance'] if self.account_info else 0,
                'account_equity': self.account_info['equity'] if self.account_info else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def start_live_streaming(self):
        """Start streaming live data"""
        if not self.connected:
            logger.error("Cannot start streaming - not connected to MT5")
            return
        
        self.streaming = True
        logger.info("Started REAL MT5 data streaming")
        
        while self.streaming:
            try:
                # Update live rates
                self.live_rates = await self.get_live_rates()
                
                # Feed data to statistical and strategy engines
                current_time = datetime.now()
                for symbol, rate in self.live_rates.items():
                    try:
                        # Import here to avoid circular imports
                        from services.statistical_engine import get_statistical_engine
                        from services.strategy_engine import get_strategy_engine
                        from services.pattern_recognition import get_pattern_engine
                        
                        # Feed data to engines
                        statistical_engine = await get_statistical_engine()
                        await statistical_engine.add_price_data(
                            timestamp=current_time,
                            symbol=symbol,
                            bid=rate['bid'],
                            ask=rate['ask'],
                            volume=rate.get('volume', 0)
                        )
                        
                        strategy_engine = await get_strategy_engine()
                        await strategy_engine.add_price_data(
                            timestamp=current_time,
                            symbol=symbol,
                            bid=rate['bid'],
                            ask=rate['ask']
                        )
                        
                        # Feed data to pattern recognition engine
                        pattern_engine = await get_pattern_engine()
                        await pattern_engine.add_price_data(
                            timestamp=current_time,
                            symbol=symbol,
                            bid=rate['bid'],
                            ask=rate['ask'],
                            volume=rate.get('volume', 0)
                        )
                        
                    except Exception as engine_error:
                        logger.warning(f"Engine feeding error: {engine_error}")
                
                # Log current prices
                for symbol, rate in self.live_rates.items():
                    logger.info(f"{symbol}: Bid={rate['bid']:.5f}, Ask={rate['ask']:.5f}, Spread={rate['spread']:.5f}")
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                await asyncio.sleep(5)
    
    async def stop_streaming(self):
        """Stop streaming"""
        self.streaming = False
        logger.info("Stopped MT5 data streaming")
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    async def get_live_analytics_data(self) -> Dict[str, Any]:
        """Get live analytics data for the dashboard"""
        if not self.connected:
            return {}
        
        try:
            # Get current rates
            rates = await self.get_live_rates()
            
            # Get real patterns for GOLD
            patterns = await self.analyze_time_patterns("XAUUSD")
            
            # Market status
            market_status = await self.get_market_status()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'market_status': market_status,
                'live_rates': rates,
                'patterns': patterns,
                'account_info': self.account_info,
                'connection_status': 'live',
                'data_source': 'MT5_LIVE_REAL'
            }
            
        except Exception as e:
            logger.error(f"Error getting live analytics: {e}")
            return {}

# Global instance
mt5_service_real = MT5ServiceReal()

async def get_mt5_service():
    """Get the real MT5 service instance"""
    if not mt5_service_real.connected:
        await mt5_service_real.connect()
    return mt5_service_real