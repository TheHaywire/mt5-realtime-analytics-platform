#!/usr/bin/env python3
"""
Demo Data Generator for Testing Intelligence Features
Generates realistic trading data to demonstrate platform capabilities
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)

class DemoDataGenerator:
    """Generates realistic demo data for testing intelligence features"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """Start demo data generation"""
        self.is_running = True
        logger.info("Starting Demo Data Generator for Intelligence Testing...")
        
        # Start demo data injection loop
        asyncio.create_task(self._demo_loop())
    
    async def stop(self):
        """Stop demo data generation"""
        self.is_running = False
        logger.info("Stopped Demo Data Generator")
    
    async def _demo_loop(self):
        """Generate demo intelligence data periodically"""
        while self.is_running:
            try:
                await self._inject_demo_strategies()
                await self._inject_demo_edges()
                await self._inject_demo_signals() 
                await self._inject_demo_patterns()
                await asyncio.sleep(10)  # Update every 10 seconds for demo
                
            except Exception as e:
                logger.error(f"Demo data generation error: {e}")
                await asyncio.sleep(30)
    
    async def _inject_demo_strategies(self):
        """Inject demo strategy performance data"""
        from services.strategy_engine import get_strategy_engine
        
        try:
            strategy_engine = await get_strategy_engine()
            
            # Simulate strategy performance updates
            demo_performances = {
                'turtle_breakout': {
                    'total_signals': 15,
                    'winning_signals': 11,
                    'win_rate': 73.3,
                    'performance_score': 87,
                    'current_streak': 3
                },
                'rsi2_mean_reversion': {
                    'total_signals': 12,
                    'winning_signals': 8,
                    'win_rate': 66.7,
                    'performance_score': 79,
                    'current_streak': 2
                },
                '0317_edge': {
                    'total_signals': 8,
                    'winning_signals': 6,
                    'win_rate': 75.0,
                    'performance_score': 82,
                    'current_streak': 1
                },
                'friday_rush': {
                    'total_signals': 6,
                    'winning_signals': 4,
                    'win_rate': 66.7,
                    'performance_score': 74,
                    'current_streak': -1
                },
                'wednesday_fade': {
                    'total_signals': 5,
                    'winning_signals': 3,
                    'win_rate': 60.0,
                    'performance_score': 68,
                    'current_streak': 1
                }
            }
            
            # Update strategy performances
            for strategy_id, strategy in strategy_engine.strategies.items():
                if strategy_id in demo_performances:
                    perf_data = demo_performances[strategy_id]
                    perf = strategy['performance']
                    
                    perf.total_signals = perf_data['total_signals']
                    perf.winning_signals = perf_data['winning_signals']
                    perf.win_rate = perf_data['win_rate']
                    perf.performance_score = perf_data['performance_score']
                    perf.current_streak = perf_data['current_streak']
                    
            logger.info("Injected demo strategy performance data")
            
        except Exception as e:
            logger.error(f"Demo strategy injection error: {e}")
    
    async def _inject_demo_edges(self):
        """Inject demo statistical edges"""
        from services.statistical_engine import get_statistical_engine
        
        try:
            statistical_engine = await get_statistical_engine()
            
            # Create some demo edges
            demo_edges = {
                'time_of_day_03': {
                    'name': '03:00 Hour Edge',
                    'type': 'time_of_day',
                    'period': '03:00',
                    'direction': 'long',
                    'win_rate': 68.5,
                    'strength': 76.2,
                    'confidence_level': 95.0,
                    'p_value': 0.023,
                    'total_trades': 28,
                    'is_active': True
                },
                'time_of_day_15': {
                    'name': '15:00 Hour Edge',
                    'type': 'time_of_day', 
                    'period': '15:00',
                    'direction': 'short',
                    'win_rate': 71.2,
                    'strength': 82.1,
                    'confidence_level': 95.0,
                    'p_value': 0.015,
                    'total_trades': 33,
                    'is_active': True
                },
                'day_of_week_friday': {
                    'name': 'Friday Long Bias',
                    'type': 'day_of_week',
                    'period': 'friday',
                    'direction': 'long',
                    'win_rate': 64.7,
                    'strength': 69.3,
                    'confidence_level': 90.0,
                    'p_value': 0.041,
                    'total_trades': 17,
                    'is_active': True
                },
                'session_london_ny': {
                    'name': 'London/NY Overlap Edge',
                    'type': 'session',
                    'period': 'london_ny_overlap',
                    'direction': 'long',
                    'win_rate': 72.8,
                    'strength': 85.4,
                    'confidence_level': 99.0,
                    'p_value': 0.003,
                    'total_trades': 46,
                    'is_active': True
                }
            }
            
            # Add demo edges to the engine
            for edge_key, edge_data in demo_edges.items():
                statistical_engine.current_edges[edge_key] = edge_data
                
            logger.info(f"Injected {len(demo_edges)} demo statistical edges")
            
        except Exception as e:
            logger.error(f"Demo edges injection error: {e}")
    
    async def _inject_demo_signals(self):
        """Inject demo trading signals"""
        from services.strategy_engine import get_strategy_engine
        
        try:
            strategy_engine = await get_strategy_engine()
            
            # Clear old signals and add fresh ones
            strategy_engine.active_signals = []
            
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Generate signals based on current conditions
            demo_signals = []
            
            # Time-based signal during London/NY overlap
            if 13 <= current_hour <= 16:
                demo_signals.append({
                    'strategy': 'London/NY Overlap Strategy',
                    'timestamp': current_time.isoformat(),
                    'signal_type': 'BUY',
                    'symbol': 'GOLD',
                    'price': 3359.12,
                    'confidence': 84.2,
                    'risk_level': 'MEDIUM',
                    'stop_loss': 3354.50,
                    'take_profit': 3368.00,
                    'reasoning': 'Major session overlap with high volume and statistical edge active'
                })
            
            # Turtle breakout signal
            if random.random() < 0.7:  # 70% chance to show signal
                demo_signals.append({
                    'strategy': 'Turtle Breakout System',
                    'timestamp': current_time.isoformat(),
                    'signal_type': 'BUY',
                    'symbol': 'GOLD',
                    'price': 3359.00,
                    'confidence': 78.6,
                    'risk_level': 'MEDIUM',
                    'stop_loss': 3352.20,
                    'take_profit': 3372.40,
                    'reasoning': '20-day breakout confirmed with volume, trending market conditions'
                })
            
            # RSI oversold signal
            if random.random() < 0.5:  # 50% chance
                demo_signals.append({
                    'strategy': 'RSI-2 Mean Reversion',
                    'timestamp': current_time.isoformat(),
                    'signal_type': 'BUY',
                    'symbol': 'GOLD',
                    'price': 3359.00,
                    'confidence': 72.1,
                    'risk_level': 'LOW',
                    'stop_loss': 3354.80,
                    'take_profit': 3364.60,
                    'reasoning': 'RSI(2) oversold at 8.4, price above 200-day SMA, bullish mean reversion setup'
                })
            
            # Friday pattern signal (if it's Friday)
            if current_time.weekday() == 4:  # Friday
                demo_signals.append({
                    'strategy': 'Friday Gold Rush',
                    'timestamp': current_time.isoformat(),
                    'signal_type': 'BUY',
                    'symbol': 'GOLD',
                    'price': 3359.00,
                    'confidence': 69.8,
                    'risk_level': 'MEDIUM',
                    'stop_loss': 3353.50,
                    'take_profit': 3368.70,
                    'reasoning': 'Friday long bias pattern, historically strong end-of-week performance'
                })
            
            strategy_engine.active_signals = demo_signals
            logger.info(f"Injected {len(demo_signals)} demo trading signals")
            
        except Exception as e:
            logger.error(f"Demo signals injection error: {e}")
    
    async def _inject_demo_patterns(self):
        """Inject demo discovered patterns"""
        from services.pattern_recognition import get_pattern_engine
        
        try:
            pattern_engine = await get_pattern_engine()
            
            # Create demo discovered patterns
            demo_patterns = [
                {
                    'id': 'pattern_001',
                    'name': 'Morning Gap Reversal',
                    'type': 'technical',
                    'description': 'Price gaps down at market open then reverses within first hour',
                    'win_rate': 73.2,
                    'avg_return': 0.0045,
                    'total_occurrences': 23,
                    'statistical_significance': 94.7,
                    'p_value': 0.025,
                    'validation_score': 87.3,
                    'is_validated': True,
                    'discovered_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'conditions': {'gap_down': '>0.2%', 'reversal_time': '<60min'}
                },
                {
                    'id': 'pattern_002',
                    'name': 'High Volatility Continuation',
                    'type': 'statistical',
                    'description': 'After periods of high volatility, trend continues in same direction',
                    'win_rate': 66.1,
                    'avg_return': 0.0038,
                    'total_occurrences': 31,
                    'statistical_significance': 89.2,
                    'p_value': 0.031,
                    'validation_score': 82.6,
                    'is_validated': True,
                    'discovered_at': (datetime.now() - timedelta(hours=4)).isoformat(),
                    'conditions': {'volatility': '>80th percentile', 'timeframe': '15min'}
                },
                {
                    'id': 'pattern_003',
                    'name': 'Support Bounce Pattern',
                    'type': 'technical',
                    'description': 'Price bounces off psychological support levels with volume confirmation',
                    'win_rate': 69.8,
                    'avg_return': 0.0041,
                    'total_occurrences': 18,
                    'statistical_significance': 86.4,
                    'p_value': 0.038,
                    'validation_score': 79.1,
                    'is_validated': True,
                    'discovered_at': (datetime.now() - timedelta(hours=6)).isoformat(),
                    'conditions': {'support_level': 'psychological', 'volume_spike': '>150%'}
                },
                {
                    'id': 'pattern_004',
                    'name': 'Spread Compression Signal',
                    'type': 'behavioral',
                    'description': 'Tight spreads followed by directional price movement',
                    'win_rate': 61.5,
                    'avg_return': 0.0032,
                    'total_occurrences': 14,
                    'statistical_significance': 78.3,
                    'p_value': 0.047,
                    'validation_score': 71.8,
                    'is_validated': False,
                    'discovered_at': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'conditions': {'spread': '<25th percentile', 'duration': '>10min'}
                }
            ]
            
            # Clear existing and add demo patterns
            pattern_engine.discovered_patterns = {}
            for pattern_data in demo_patterns:
                pattern_engine.discovered_patterns[pattern_data['id']] = pattern_data
                
            logger.info(f"Injected {len(demo_patterns)} demo discovered patterns")
            
        except Exception as e:
            logger.error(f"Demo patterns injection error: {e}")
    
    async def generate_demo_alerts(self) -> List[Dict[str, Any]]:
        """Generate demo alerts for testing"""
        current_time = datetime.now()
        
        demo_alerts = [
            {
                'id': f'alert_{current_time.strftime("%H%M%S")}_001',
                'timestamp': current_time.isoformat(),
                'type': 'strategy_signal',
                'priority': 3,  # HIGH
                'title': '🎯 High-Confidence BUY Signal',
                'message': 'Turtle Breakout System generated BUY signal with 84.2% confidence during London/NY overlap',
                'symbol': 'GOLD',
                'price': 3359.12,
                'confidence': 84.2,
                'action': 'BUY',
                'reasoning': 'Major session overlap with confirmed breakout pattern and volume surge',
                'risk_level': 'MEDIUM',
                'stop_loss': 3354.50,
                'take_profit': 3368.00,
                'expires_at': (current_time + timedelta(hours=2)).isoformat(),
                'metadata': {'strategy': 'Turtle Breakout', 'session': 'london_ny_overlap'}
            },
            {
                'id': f'alert_{current_time.strftime("%H%M%S")}_002',
                'timestamp': (current_time - timedelta(minutes=5)).isoformat(),
                'type': 'statistical_edge',
                'priority': 2,  # MEDIUM
                'title': '⚡ Statistical Edge Active',
                'message': 'London/NY Overlap Edge showing 85.4% strength with 72.8% historical win rate',
                'symbol': 'GOLD',
                'price': 3359.00,
                'confidence': 85.4,
                'action': 'MONITOR',
                'reasoning': 'Prime trading window with 46 historical samples confirming edge',
                'risk_level': 'MEDIUM',
                'stop_loss': None,
                'take_profit': None,
                'expires_at': (current_time + timedelta(hours=1)).isoformat(),
                'metadata': {'edge_type': 'session', 'samples': 46}
            },
            {
                'id': f'alert_{current_time.strftime("%H%M%S")}_003',
                'timestamp': (current_time - timedelta(minutes=12)).isoformat(),
                'type': 'market_opportunity',
                'priority': 2,  # MEDIUM
                'title': '🚀 Prime Trading Window',
                'message': 'Major session overlap detected with 3 active statistical edges and elevated opportunity score',
                'symbol': 'GOLD',
                'price': 3359.00,
                'confidence': 78.5,
                'action': 'MONITOR',
                'reasoning': 'High-volume session with multiple confirmed patterns active',
                'risk_level': 'MEDIUM',
                'stop_loss': None,
                'take_profit': None,
                'expires_at': (current_time + timedelta(minutes=45)).isoformat(),
                'metadata': {'active_edges': 3, 'session': 'major_overlap'}
            }
        ]
        
        return demo_alerts

# Global demo data generator
demo_generator = DemoDataGenerator()

async def get_demo_generator() -> DemoDataGenerator:
    """Get the global demo generator instance"""
    return demo_generator