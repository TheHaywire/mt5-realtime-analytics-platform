#!/usr/bin/env python3
"""
Statistical Edge Detection Engine
Analyzes live MT5 data to identify profitable time-based patterns and statistical edges
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from dataclasses import dataclass
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class EdgePattern:
    """Statistical edge pattern with performance metrics"""
    name: str
    type: str  # 'time_of_day', 'day_of_week', 'session', 'volatility'
    period: str  # e.g., '03:17', 'friday', 'asian_session'
    direction: str  # 'long', 'short', 'neutral'
    
    # Performance metrics
    win_rate: float
    avg_winner: float
    avg_loser: float
    profit_factor: float
    total_trades: int
    
    # Statistical significance
    confidence_level: float
    p_value: float
    z_score: float
    
    # Risk metrics
    max_drawdown: float
    sharpe_ratio: float
    
    # Current status
    is_active: bool
    strength: float  # 0-100 pattern strength score
    last_signal: Optional[datetime]

class StatisticalEngine:
    """Real-time statistical analysis engine for trading edge detection"""
    
    def __init__(self):
        self.is_running = False
        self.price_data = []  # Rolling price history
        self.patterns = {}  # Discovered patterns
        self.performance_history = defaultdict(list)  # Pattern performance over time
        self.current_edges = {}  # Currently active edges
        
        # Analysis parameters
        self.min_trades_for_significance = 25
        self.confidence_threshold = 0.95
        self.rolling_window_days = 30
        self.analysis_interval_seconds = 60  # Analyze every minute
        
    async def start(self):
        """Start the statistical analysis engine"""
        self.is_running = True
        logger.info("Starting Statistical Edge Detection Engine...")
        
        # Start analysis loop
        asyncio.create_task(self._analysis_loop())
        
    async def stop(self):
        """Stop the statistical analysis"""
        self.is_running = False
        logger.info("Stopped Statistical Engine")
    
    async def _analysis_loop(self):
        """Main statistical analysis loop"""
        while self.is_running:
            try:
                await self._run_full_analysis()
                await asyncio.sleep(self.analysis_interval_seconds)
            except Exception as e:
                logger.error(f"Statistical analysis error: {e}")
                await asyncio.sleep(30)
    
    async def add_price_data(self, timestamp: datetime, symbol: str, bid: float, ask: float, volume: float = 0):
        """Add new price tick for analysis"""
        price_point = {
            'timestamp': timestamp,
            'symbol': symbol,
            'bid': bid,
            'ask': ask,
            'mid': (bid + ask) / 2,
            'spread': ask - bid,
            'volume': volume,
            'hour': timestamp.hour,
            'minute': timestamp.minute,
            'weekday': timestamp.weekday(),
            'day_name': timestamp.strftime('%A').lower()
        }
        
        self.price_data.append(price_point)
        
        # Keep only recent data (rolling window)
        cutoff_time = timestamp - timedelta(days=self.rolling_window_days)
        self.price_data = [p for p in self.price_data if p['timestamp'] > cutoff_time]
    
    async def _run_full_analysis(self):
        """Run comprehensive statistical analysis"""
        if len(self.price_data) < 100:  # Need minimum data
            return
            
        logger.info(f"Running statistical analysis on {len(self.price_data)} data points...")
        
        # Analyze different pattern types
        await self._analyze_time_of_day_patterns()
        await self._analyze_day_of_week_patterns() 
        await self._analyze_session_patterns()
        await self._analyze_volatility_patterns()
        await self._analyze_momentum_patterns()
        
        # Update pattern strengths and rankings
        await self._update_pattern_rankings()
        
        logger.info(f"Analysis complete. Found {len(self.patterns)} patterns")
    
    async def _analyze_time_of_day_patterns(self):
        """Analyze profitable times of day"""
        df = pd.DataFrame(self.price_data)
        if len(df) < 50:
            return
        
        # Create price returns for each hour
        df['return'] = df['mid'].pct_change()
        df = df.dropna()
        
        # Group by hour and analyze returns
        hourly_stats = df.groupby('hour')['return'].agg([
            'count', 'mean', 'std', 'min', 'max',
            lambda x: (x > 0).mean(),  # Win rate
            lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0,  # Avg winner
            lambda x: x[x < 0].mean() if len(x[x < 0]) > 0 else 0   # Avg loser
        ]).round(6)
        
        hourly_stats.columns = ['count', 'avg_return', 'volatility', 'min_return', 'max_return', 'win_rate', 'avg_winner', 'avg_loser']
        
        # Find statistically significant hours
        for hour in range(24):
            if hour not in hourly_stats.index:
                continue
                
            stats_row = hourly_stats.loc[hour]
            
            if stats_row['count'] >= self.min_trades_for_significance:
                # Perform statistical tests
                hour_returns = df[df['hour'] == hour]['return'].dropna()
                
                if len(hour_returns) > 10:
                    # Test if returns are significantly different from zero
                    t_stat, p_value = stats.ttest_1samp(hour_returns, 0)
                    
                    if p_value < (1 - self.confidence_threshold):
                        direction = 'long' if stats_row['avg_return'] > 0 else 'short'
                        
                        # Calculate additional metrics
                        profit_factor = abs(stats_row['avg_winner'] * stats_row['win_rate'] / 
                                          (stats_row['avg_loser'] * (1 - stats_row['win_rate']))) if stats_row['avg_loser'] != 0 else 0
                        
                        sharpe_ratio = stats_row['avg_return'] / stats_row['volatility'] if stats_row['volatility'] > 0 else 0
                        
                        pattern = EdgePattern(
                            name=f"{hour:02d}:00 Hour Edge",
                            type="time_of_day",
                            period=f"{hour:02d}:00",
                            direction=direction,
                            win_rate=stats_row['win_rate'] * 100,
                            avg_winner=stats_row['avg_winner'] * 100,
                            avg_loser=stats_row['avg_loser'] * 100,
                            profit_factor=profit_factor,
                            total_trades=int(stats_row['count']),
                            confidence_level=self.confidence_threshold * 100,
                            p_value=p_value,
                            z_score=abs(t_stat),
                            max_drawdown=0,  # TODO: Calculate proper drawdown
                            sharpe_ratio=sharpe_ratio,
                            is_active=True,
                            strength=min(100, abs(t_stat) * 10),  # Strength based on statistical significance
                            last_signal=datetime.now()
                        )
                        
                        pattern_key = f"time_of_day_{hour:02d}"
                        self.patterns[pattern_key] = pattern
                        
                        logger.info(f"Found time edge: {hour:02d}:00 - Win Rate: {stats_row['win_rate']:.1%}, P-value: {p_value:.4f}")
    
    async def _analyze_day_of_week_patterns(self):
        """Analyze day-of-week patterns (Monday weakness, Friday strength, etc.)"""
        df = pd.DataFrame(self.price_data)
        if len(df) < 50:
            return
        
        df['return'] = df['mid'].pct_change()
        df = df.dropna()
        
        # Group by day of week
        daily_stats = df.groupby('day_name')['return'].agg([
            'count', 'mean', 'std',
            lambda x: (x > 0).mean(),  # Win rate
            lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0,
            lambda x: x[x < 0].mean() if len(x[x < 0]) > 0 else 0
        ]).round(6)
        
        daily_stats.columns = ['count', 'avg_return', 'volatility', 'win_rate', 'avg_winner', 'avg_loser']
        
        # Analyze each day
        for day_name in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            if day_name not in daily_stats.index:
                continue
                
            stats_row = daily_stats.loc[day_name]
            
            if stats_row['count'] >= self.min_trades_for_significance:
                day_returns = df[df['day_name'] == day_name]['return'].dropna()
                
                if len(day_returns) > 10:
                    t_stat, p_value = stats.ttest_1samp(day_returns, 0)
                    
                    if p_value < (1 - self.confidence_threshold):
                        direction = 'long' if stats_row['avg_return'] > 0 else 'short'
                        
                        profit_factor = abs(stats_row['avg_winner'] * stats_row['win_rate'] / 
                                          (stats_row['avg_loser'] * (1 - stats_row['win_rate']))) if stats_row['avg_loser'] != 0 else 0
                        
                        pattern = EdgePattern(
                            name=f"{day_name.title()} {direction.title()} Bias",
                            type="day_of_week",
                            period=day_name,
                            direction=direction,
                            win_rate=stats_row['win_rate'] * 100,
                            avg_winner=stats_row['avg_winner'] * 100,
                            avg_loser=stats_row['avg_loser'] * 100,
                            profit_factor=profit_factor,
                            total_trades=int(stats_row['count']),
                            confidence_level=self.confidence_threshold * 100,
                            p_value=p_value,
                            z_score=abs(t_stat),
                            max_drawdown=0,
                            sharpe_ratio=stats_row['avg_return'] / stats_row['volatility'] if stats_row['volatility'] > 0 else 0,
                            is_active=True,
                            strength=min(100, abs(t_stat) * 15),
                            last_signal=datetime.now()
                        )
                        
                        pattern_key = f"day_of_week_{day_name}"
                        self.patterns[pattern_key] = pattern
                        
                        logger.info(f"Found day pattern: {day_name.title()} {direction} - Win Rate: {stats_row['win_rate']:.1%}")
    
    async def _analyze_session_patterns(self):
        """Analyze trading session patterns (Asian, European, US)"""
        df = pd.DataFrame(self.price_data)
        if len(df) < 50:
            return
        
        df['return'] = df['mid'].pct_change()
        df = df.dropna()
        
        # Define trading sessions (UTC hours)
        def get_session(hour):
            if 0 <= hour < 8:
                return 'asian'
            elif 8 <= hour < 16:
                return 'european'
            else:
                return 'us'
        
        df['session'] = df['hour'].apply(get_session)
        
        # Analyze each session
        for session in ['asian', 'european', 'us']:
            session_data = df[df['session'] == session]
            
            if len(session_data) >= self.min_trades_for_significance:
                returns = session_data['return'].dropna()
                
                if len(returns) > 10:
                    win_rate = (returns > 0).mean()
                    avg_winner = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
                    avg_loser = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
                    
                    t_stat, p_value = stats.ttest_1samp(returns, 0)
                    
                    if p_value < (1 - self.confidence_threshold):
                        direction = 'long' if returns.mean() > 0 else 'short'
                        
                        pattern = EdgePattern(
                            name=f"{session.title()} Session {direction.title()}",
                            type="session",
                            period=session,
                            direction=direction,
                            win_rate=win_rate * 100,
                            avg_winner=avg_winner * 100,
                            avg_loser=avg_loser * 100,
                            profit_factor=abs(avg_winner * win_rate / (avg_loser * (1 - win_rate))) if avg_loser != 0 else 0,
                            total_trades=len(returns),
                            confidence_level=self.confidence_threshold * 100,
                            p_value=p_value,
                            z_score=abs(t_stat),
                            max_drawdown=0,
                            sharpe_ratio=returns.mean() / returns.std() if returns.std() > 0 else 0,
                            is_active=True,
                            strength=min(100, abs(t_stat) * 12),
                            last_signal=datetime.now()
                        )
                        
                        self.patterns[f"session_{session}"] = pattern
    
    async def _analyze_volatility_patterns(self):
        """Analyze high/low volatility period patterns"""
        df = pd.DataFrame(self.price_data)
        if len(df) < 100:
            return
            
        df['return'] = df['mid'].pct_change()
        df['volatility'] = df['return'].rolling(window=10).std()
        df = df.dropna()
        
        # Define high/low volatility periods
        volatility_threshold = df['volatility'].quantile(0.7)
        df['vol_regime'] = df['volatility'].apply(lambda x: 'high' if x > volatility_threshold else 'low')
        
        # Analyze performance in different volatility regimes
        for regime in ['high', 'low']:
            regime_data = df[df['vol_regime'] == regime]
            
            if len(regime_data) >= self.min_trades_for_significance:
                returns = regime_data['return'].dropna()
                
                if len(returns) > 10:
                    win_rate = (returns > 0).mean()
                    t_stat, p_value = stats.ttest_1samp(returns, 0)
                    
                    if p_value < (1 - self.confidence_threshold) and abs(returns.mean()) > 0.0001:  # Minimum significance threshold
                        direction = 'long' if returns.mean() > 0 else 'short'
                        
                        pattern = EdgePattern(
                            name=f"{regime.title()} Volatility {direction.title()}",
                            type="volatility",
                            period=f"{regime}_vol",
                            direction=direction,
                            win_rate=win_rate * 100,
                            avg_winner=returns[returns > 0].mean() * 100 if len(returns[returns > 0]) > 0 else 0,
                            avg_loser=returns[returns < 0].mean() * 100 if len(returns[returns < 0]) > 0 else 0,
                            profit_factor=0,  # Calculate separately
                            total_trades=len(returns),
                            confidence_level=self.confidence_threshold * 100,
                            p_value=p_value,
                            z_score=abs(t_stat),
                            max_drawdown=0,
                            sharpe_ratio=returns.mean() / returns.std() if returns.std() > 0 else 0,
                            is_active=True,
                            strength=min(100, abs(t_stat) * 8),
                            last_signal=datetime.now()
                        )
                        
                        self.patterns[f"volatility_{regime}"] = pattern
    
    async def _analyze_momentum_patterns(self):
        """Analyze momentum and mean reversion patterns"""
        df = pd.DataFrame(self.price_data)
        if len(df) < 100:
            return
            
        df['return'] = df['mid'].pct_change()
        df['momentum'] = df['return'].rolling(window=5).mean()  # 5-period momentum
        df = df.dropna()
        
        # Analyze momentum persistence
        df['next_return'] = df['return'].shift(-1)
        correlation = df['momentum'].corr(df['next_return'])
        
        if abs(correlation) > 0.1:  # Minimum correlation threshold
            momentum_direction = 'trend_following' if correlation > 0 else 'mean_reverting'
            
            # Test statistical significance of momentum effect
            valid_data = df[['momentum', 'next_return']].dropna()
            
            if len(valid_data) > 50:
                # Create momentum buckets
                df['momentum_bucket'] = pd.qcut(df['momentum'], q=3, labels=['low', 'medium', 'high'])
                
                # Analyze performance of high momentum periods
                high_momentum_returns = df[df['momentum_bucket'] == 'high']['next_return'].dropna()
                low_momentum_returns = df[df['momentum_bucket'] == 'low']['next_return'].dropna()
                
                if len(high_momentum_returns) > 20 and len(low_momentum_returns) > 20:
                    # Test if high momentum periods have different returns
                    t_stat, p_value = stats.ttest_ind(high_momentum_returns, low_momentum_returns)
                    
                    if p_value < 0.05:  # Significant difference
                        better_performance = 'high' if high_momentum_returns.mean() > low_momentum_returns.mean() else 'low'
                        direction = 'long' if high_momentum_returns.mean() > 0 else 'short'
                        
                        pattern = EdgePattern(
                            name=f"Momentum {momentum_direction.replace('_', ' ').title()}",
                            type="momentum", 
                            period="momentum_based",
                            direction=direction,
                            win_rate=(high_momentum_returns > 0).mean() * 100,
                            avg_winner=high_momentum_returns[high_momentum_returns > 0].mean() * 100 if len(high_momentum_returns[high_momentum_returns > 0]) > 0 else 0,
                            avg_loser=high_momentum_returns[high_momentum_returns < 0].mean() * 100 if len(high_momentum_returns[high_momentum_returns < 0]) > 0 else 0,
                            profit_factor=0,
                            total_trades=len(high_momentum_returns),
                            confidence_level=95,
                            p_value=p_value,
                            z_score=abs(t_stat),
                            max_drawdown=0,
                            sharpe_ratio=high_momentum_returns.mean() / high_momentum_returns.std() if high_momentum_returns.std() > 0 else 0,
                            is_active=True,
                            strength=min(100, abs(correlation) * 100),
                            last_signal=datetime.now()
                        )
                        
                        self.patterns["momentum_pattern"] = pattern
    
    async def _update_pattern_rankings(self):
        """Update pattern strength rankings and current active edges"""
        if not self.patterns:
            return
        
        # Sort patterns by strength and statistical significance  
        ranked_patterns = sorted(
            self.patterns.items(),
            key=lambda x: (x[1].strength * x[1].z_score),
            reverse=True
        )
        
        # Update current active edges (top performing patterns)
        self.current_edges = {}
        for i, (pattern_key, pattern) in enumerate(ranked_patterns[:10]):  # Top 10 patterns
            if pattern.is_active and pattern.strength > 20:  # Minimum strength threshold
                self.current_edges[pattern_key] = pattern
                
                # Log top patterns
                if i < 5:
                    logger.info(f"Top Pattern #{i+1}: {pattern.name} - Strength: {pattern.strength:.1f}, Win Rate: {pattern.win_rate:.1f}%")
    
    async def get_current_edges(self) -> Dict[str, Dict[str, Any]]:
        """Get current active trading edges"""
        edges_data = {}
        
        for pattern_key, pattern in self.current_edges.items():
            edges_data[pattern_key] = {
                'name': pattern.name,
                'type': pattern.type,
                'period': pattern.period,
                'direction': pattern.direction,
                'win_rate': pattern.win_rate,
                'profit_factor': pattern.profit_factor,
                'strength': pattern.strength,
                'confidence': pattern.confidence_level,
                'total_trades': pattern.total_trades,
                'is_active': pattern.is_active,
                'sharpe_ratio': pattern.sharpe_ratio,
                'avg_winner': pattern.avg_winner,
                'avg_loser': pattern.avg_loser
            }
        
        return edges_data
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        return {
            'total_patterns': len(self.patterns),
            'active_edges': len(self.current_edges),
            'data_points': len(self.price_data),
            'analysis_window_days': self.rolling_window_days,
            'last_analysis': datetime.now().isoformat(),
            'top_edges': await self.get_current_edges()
        }

# Global statistical engine instance
statistical_engine = StatisticalEngine()

async def get_statistical_engine() -> StatisticalEngine:
    """Get the global statistical engine instance"""
    return statistical_engine