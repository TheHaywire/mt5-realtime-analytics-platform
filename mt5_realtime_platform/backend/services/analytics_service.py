#!/usr/bin/env python3
"""
Analytics Service - Real-time statistical edge computation and analysis
Continuously computes time-of-day and day-of-week patterns over rolling windows
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from collections import defaultdict, deque
import json
from scipy import stats
import pytz

from models.database import SessionLocal
from models.schemas import BarData, StrategyConfig
from core.config import settings

logger = logging.getLogger(__name__)

class StatisticalCalculator:
    """Core statistical calculations for edge detection"""
    
    @staticmethod
    def calculate_win_rate(returns: List[float]) -> Dict[str, float]:
        """Calculate win rate with confidence intervals"""
        if len(returns) < 10:
            return {"win_rate": 0.5, "confidence": 0.0, "sample_size": len(returns)}
            
        wins = sum(1 for r in returns if r > 0)
        win_rate = wins / len(returns)
        
        # Calculate confidence interval using Wilson score
        n = len(returns)
        z = 1.96  # 95% confidence
        
        p_hat = win_rate
        denominator = 1 + z**2 / n
        center = (p_hat + z**2 / (2*n)) / denominator
        width = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4*n**2)) / denominator
        
        ci_lower = max(0, center - width)
        ci_upper = min(1, center + width)
        
        # Statistical significance test (against 50% null hypothesis)
        z_score = (win_rate - 0.5) / np.sqrt(0.5 * 0.5 / n)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return {
            "win_rate": win_rate,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "confidence": 1 - p_value,
            "sample_size": n,
            "z_score": z_score,
            "p_value": p_value
        }
        
    @staticmethod
    def calculate_volatility_metrics(returns: List[float]) -> Dict[str, float]:
        """Calculate volatility and risk metrics"""
        if len(returns) < 10:
            return {"volatility": 0.0, "sharpe": 0.0, "max_drawdown": 0.0}
            
        returns_array = np.array(returns)
        
        # Volatility (annualized)
        volatility = np.std(returns_array) * np.sqrt(252 * 24 * 60)  # Minute data
        
        # Sharpe ratio (assuming 2% risk-free rate)
        excess_returns = returns_array - (0.02 / (252 * 24 * 60))
        sharpe = np.mean(excess_returns) / np.std(returns_array) if np.std(returns_array) > 0 else 0
        
        # Maximum drawdown
        cumulative = np.cumsum(returns_array)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_drawdown = np.min(drawdown)
        
        return {
            "volatility": volatility,
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
            "avg_return": np.mean(returns_array),
            "return_std": np.std(returns_array)
        }

class RollingWindowAnalyzer:
    """Analyzes patterns over rolling time windows"""
    
    def __init__(self, window_hours: int = 168):  # 1 week default
        self.window_hours = window_hours
        self.data_buffer = deque(maxlen=window_hours * 60)  # Minute data
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        
    def add_bar(self, bar_data: Dict[str, Any]):
        """Add new bar to rolling window"""
        # Convert timestamp to IST for analysis
        timestamp = pd.to_datetime(bar_data['timestamp'])
        ist_timestamp = timestamp.tz_convert(self.ist_tz)
        
        self.data_buffer.append({
            'timestamp': timestamp,
            'timestamp_ist': ist_timestamp,
            'open': bar_data['open'],
            'high': bar_data['high'], 
            'low': bar_data['low'],
            'close': bar_data['close'],
            'volume': bar_data['volume'],
            'return': bar_data.get('return', 0.0)
        })
        
    def get_time_of_day_patterns(self) -> Dict[str, Any]:
        """Analyze patterns by time of day (IST)"""
        if len(self.data_buffer) < 100:
            return {}
            
        df = pd.DataFrame(list(self.data_buffer))
        df['hour'] = df['timestamp_ist'].dt.hour
        df['minute'] = df['timestamp_ist'].dt.minute
        df['time_key'] = df['hour'].astype(str).str.zfill(2) + ':' + df['minute'].astype(str).str.zfill(2)
        
        patterns = {}
        
        # Group by time intervals
        time_groups = df.groupby('time_key')
        
        for time_key, group in time_groups:
            if len(group) >= 10:  # Minimum sample size
                returns = group['return'].values
                
                win_rate_stats = StatisticalCalculator.calculate_win_rate(returns)
                volatility_stats = StatisticalCalculator.calculate_volatility_metrics(returns)
                
                patterns[time_key] = {
                    'time': time_key,
                    'sample_size': len(returns),
                    'win_rate': win_rate_stats['win_rate'],
                    'confidence': win_rate_stats['confidence'],
                    'avg_return': volatility_stats['avg_return'],
                    'volatility': volatility_stats['volatility'],
                    'sharpe': volatility_stats['sharpe'],
                    'is_significant': win_rate_stats['confidence'] > 0.95,
                    'edge_strength': abs(win_rate_stats['win_rate'] - 0.5) * win_rate_stats['confidence']
                }
                
        return patterns
        
    def get_day_of_week_patterns(self) -> Dict[str, Any]:
        """Analyze patterns by day of week (IST)"""
        if len(self.data_buffer) < 100:
            return {}
            
        df = pd.DataFrame(list(self.data_buffer))
        df['weekday'] = df['timestamp_ist'].dt.day_name()
        
        patterns = {}
        
        for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            day_data = df[df['weekday'] == weekday]
            
            if len(day_data) >= 10:
                returns = day_data['return'].values
                
                win_rate_stats = StatisticalCalculator.calculate_win_rate(returns)
                volatility_stats = StatisticalCalculator.calculate_volatility_metrics(returns)
                
                patterns[weekday] = {
                    'day': weekday,
                    'sample_size': len(returns),
                    'win_rate': win_rate_stats['win_rate'],
                    'confidence': win_rate_stats['confidence'],
                    'avg_return': volatility_stats['avg_return'],
                    'volatility': volatility_stats['volatility'],
                    'is_significant': win_rate_stats['confidence'] > 0.95,
                    'edge_strength': abs(win_rate_stats['win_rate'] - 0.5) * win_rate_stats['confidence']
                }
                
        return patterns
        
    def get_volatility_surface(self) -> Dict[str, Any]:
        """Generate 3D volatility surface data"""
        if len(self.data_buffer) < 100:
            return {}
            
        df = pd.DataFrame(list(self.data_buffer))
        df['hour'] = df['timestamp_ist'].dt.hour
        df['weekday'] = df['timestamp_ist'].dt.weekday  # 0=Monday
        
        # Calculate volatility by hour and day
        volatility_matrix = []
        hours = list(range(24))
        weekdays = list(range(5))  # Monday to Friday
        
        for hour in hours:
            hour_row = []
            for weekday in weekdays:
                subset = df[(df['hour'] == hour) & (df['weekday'] == weekday)]
                
                if len(subset) >= 5:
                    volatility = np.std(subset['return']) * 100  # Convert to percentage
                else:
                    volatility = 0
                    
                hour_row.append(volatility)
            volatility_matrix.append(hour_row)
            
        return {
            'hours': hours,
            'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'volatility_matrix': volatility_matrix,
            'max_volatility': np.max(volatility_matrix) if volatility_matrix else 0
        }

class StrategyMonitor:
    """Monitor predefined trading strategies in real-time"""
    
    def __init__(self):
        self.strategies = {
            'am_edge_0317': {
                'name': '03:17 AM Edge',
                'entry_time': '01:00',
                'exit_time': '03:17',
                'direction': 'long',
                'returns': deque(maxlen=1000),
                'active_trades': {}
            },
            'friday_long': {
                'name': 'Friday Gold Rush',
                'day_filter': 'Friday',
                'direction': 'long',
                'returns': deque(maxlen=1000),
                'session': 'full_day'
            },
            'wednesday_short': {
                'name': 'Wednesday Fade',
                'day_filter': 'Wednesday', 
                'direction': 'short',
                'returns': deque(maxlen=1000),
                'entry_time': '09:00',
                'exit_time': '17:00'
            }
        }
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        
    def update_strategy_performance(self, bar_data: Dict[str, Any]):
        """Update strategy performance with new bar"""
        timestamp = pd.to_datetime(bar_data['timestamp'])
        ist_time = timestamp.tz_convert(self.ist_tz)
        
        current_return = bar_data.get('return', 0.0)
        
        # Update each strategy
        for strategy_id, strategy in self.strategies.items():
            if self._should_trade_strategy(strategy, ist_time):
                strategy['returns'].append(current_return)
                
    def _should_trade_strategy(self, strategy: Dict, ist_time: pd.Timestamp) -> bool:
        """Check if strategy should be trading at this time"""
        # Day filter
        if 'day_filter' in strategy:
            if ist_time.day_name() != strategy['day_filter']:
                return False
                
        # Time filter
        if 'entry_time' in strategy and 'exit_time' in strategy:
            entry_time = pd.to_datetime(strategy['entry_time']).time()
            exit_time = pd.to_datetime(strategy['exit_time']).time()
            current_time = ist_time.time()
            
            if not (entry_time <= current_time <= exit_time):
                return False
                
        return True
        
    def get_strategy_performance(self) -> Dict[str, Dict]:
        """Get current performance metrics for all strategies"""
        performance = {}
        
        for strategy_id, strategy in self.strategies.items():
            returns = list(strategy['returns'])
            
            if len(returns) >= 10:
                win_rate_stats = StatisticalCalculator.calculate_win_rate(returns)
                volatility_stats = StatisticalCalculator.calculate_volatility_metrics(returns)
                
                performance[strategy_id] = {
                    'name': strategy['name'],
                    'sample_size': len(returns),
                    'win_rate': win_rate_stats['win_rate'],
                    'confidence': win_rate_stats['confidence'],
                    'avg_return': volatility_stats['avg_return'],
                    'sharpe': volatility_stats['sharpe'],
                    'max_drawdown': volatility_stats['max_drawdown'],
                    'total_return': sum(returns),
                    'is_significant': win_rate_stats['confidence'] > 0.95,
                    'last_updated': datetime.utcnow().isoformat()
                }
            else:
                performance[strategy_id] = {
                    'name': strategy['name'],
                    'sample_size': len(returns),
                    'status': 'insufficient_data'
                }
                
        return performance

class AnalyticsService:
    """Main analytics service coordinating all analysis"""
    
    def __init__(self):
        self.running = False
        self.rolling_analyzer = RollingWindowAnalyzer()
        self.strategy_monitor = StrategyMonitor()
        self.live_data_cache = {}
        self.current_edges = {}
        
    async def start_analytics_engine(self):
        """Start the analytics processing engine"""
        self.running = True
        logger.info("Starting analytics engine...")
        
        # Start background tasks
        asyncio.create_task(self._process_historical_data())
        asyncio.create_task(self._continuous_analysis_loop())
        
    async def stop(self):
        """Stop analytics engine"""
        self.running = False
        logger.info("Analytics engine stopped")
        
    def is_running(self) -> bool:
        """Check if analytics engine is running"""
        return self.running
        
    async def _process_historical_data(self):
        """Load and process recent historical data on startup"""
        try:
            db = SessionLocal()
            
            # Get recent bars (last 7 days)
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            recent_bars = db.query(BarData).filter(
                BarData.timestamp >= cutoff_time
            ).order_by(BarData.timestamp).all()
            
            logger.info(f"Loading {len(recent_bars)} historical bars for analysis")
            
            for bar in recent_bars:
                # Calculate return
                bar_dict = {
                    'timestamp': bar.timestamp,
                    'open': bar.open_price,
                    'high': bar.high_price,
                    'low': bar.low_price,
                    'close': bar.close_price,
                    'volume': bar.volume,
                    'return': 0.0  # Will be calculated
                }
                
                # Add to analyzers
                self.rolling_analyzer.add_bar(bar_dict)
                self.strategy_monitor.update_strategy_performance(bar_dict)
                
            db.close()
            
        except Exception as e:
            logger.error(f"Error processing historical data: {e}")
            
    async def _continuous_analysis_loop(self):
        """Continuously update analysis with new data"""
        while self.running:
            try:
                # Update current edges
                self.current_edges = {
                    'time_patterns': self.rolling_analyzer.get_time_of_day_patterns(),
                    'day_patterns': self.rolling_analyzer.get_day_of_week_patterns(),
                    'strategies': self.strategy_monitor.get_strategy_performance(),
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                # Update live data cache
                self.live_data_cache = await self._generate_live_data()
                
                # Wait before next analysis
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(5)
                
    async def _generate_live_data(self) -> Dict[str, Any]:
        """Generate comprehensive live data for dashboard"""
        try:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'market_status': 'active',  # Could check actual market hours
                'total_patterns': len(self.current_edges.get('time_patterns', {})),
                'significant_edges': sum(
                    1 for pattern in self.current_edges.get('time_patterns', {}).values() 
                    if pattern.get('is_significant', False)
                ),
                'best_edge': self._find_best_edge(),
                'volatility_level': self._calculate_current_volatility(),
                'active_strategies': len([
                    s for s in self.current_edges.get('strategies', {}).values()
                    if s.get('sample_size', 0) >= 10
                ])
            }
        except Exception as e:
            logger.error(f"Error generating live data: {e}")
            return {}
            
    def _find_best_edge(self) -> Dict[str, Any]:
        """Find the strongest current edge"""
        best_edge = None
        max_strength = 0
        
        for time_key, pattern in self.current_edges.get('time_patterns', {}).items():
            strength = pattern.get('edge_strength', 0)
            if strength > max_strength:
                max_strength = strength
                best_edge = {
                    'time': time_key,
                    'win_rate': pattern['win_rate'],
                    'confidence': pattern['confidence'],
                    'strength': strength
                }
                
        return best_edge or {}
        
    def _calculate_current_volatility(self) -> float:
        """Calculate current market volatility level"""
        if len(self.rolling_analyzer.data_buffer) < 50:
            return 0.0
            
        recent_returns = [bar['return'] for bar in list(self.rolling_analyzer.data_buffer)[-50:]]
        return np.std(recent_returns) * 100  # Convert to percentage
        
    # Public API methods
    async def get_live_data(self) -> Dict[str, Any]:
        """Get current live analytics data"""
        return self.live_data_cache
        
    async def get_current_edges(self) -> Dict[str, Any]:
        """Get current statistical edges"""
        return self.current_edges
        
    async def calculate_edges(self, symbol: str, timeframe: str, lookback_hours: int) -> Dict[str, Any]:
        """Calculate edges for specific parameters"""
        # This would typically query database and recalculate
        # For now, return current cached edges
        return self.current_edges
        
    async def generate_heatmap_data(self, symbol: str, days_back: int) -> Dict[str, Any]:
        """Generate win rate heatmap data"""
        time_patterns = self.current_edges.get('time_patterns', {})
        
        # Create 24x7 matrix (hours x days)
        heatmap_data = []
        
        for hour in range(24):
            hour_data = []
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                time_key = f"{hour:02d}:00"
                
                if time_key in time_patterns:
                    pattern = time_patterns[time_key]
                    win_rate = pattern['win_rate'] * 100  # Convert to percentage
                    confidence = pattern['confidence']
                    
                    # Color intensity based on confidence
                    intensity = confidence if pattern.get('is_significant', False) else 0.1
                    
                    hour_data.append({
                        'win_rate': win_rate,
                        'confidence': confidence,
                        'intensity': intensity,
                        'sample_size': pattern['sample_size']
                    })
                else:
                    hour_data.append({
                        'win_rate': 50,
                        'confidence': 0,
                        'intensity': 0,
                        'sample_size': 0
                    })
            heatmap_data.append(hour_data)
            
        return {
            'symbol': symbol,
            'hours': list(range(24)),
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': heatmap_data,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    async def calculate_volatility_surface(self, symbol: str, days_back: int) -> Dict[str, Any]:
        """Get 3D volatility surface data"""
        surface_data = self.rolling_analyzer.get_volatility_surface()
        surface_data['symbol'] = symbol
        surface_data['generated_at'] = datetime.utcnow().isoformat()
        return surface_data
        
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        return {
            'total_bars_processed': len(self.rolling_analyzer.data_buffer),
            'active_patterns': len(self.current_edges.get('time_patterns', {})),
            'significant_edges': len([
                p for p in self.current_edges.get('time_patterns', {}).values()
                if p.get('is_significant', False)
            ]),
            'strategies_monitored': len(self.strategy_monitor.strategies),
            'uptime_hours': 24,  # This would be calculated from startup time
            'last_analysis': self.current_edges.get('last_updated', ''),
            'system_status': 'healthy'
        }