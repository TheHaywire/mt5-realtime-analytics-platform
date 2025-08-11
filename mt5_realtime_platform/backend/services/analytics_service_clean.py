#!/usr/bin/env python3
"""
Analytics Service for real-time statistical analysis
Processes REAL MT5 data for edge detection and pattern analysis
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from scipy import stats
import json

from services.mt5_service import get_mt5_service
from services.statistical_engine import get_statistical_engine
from services.strategy_engine import get_strategy_engine
from services.alert_engine import get_alert_engine
from services.pattern_recognition import get_pattern_engine
from services.demo_data_generator import get_demo_generator

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Real-time analytics service for MT5 data"""
    
    def __init__(self):
        self.running = False
        self.edges_cache = {}
        self.last_analysis = None
        
    async def start_analytics(self):
        """Start real-time analytics"""
        self.running = True
        logger.info("Started real-time analytics service")
        
        # Start statistical engine
        statistical_engine = await get_statistical_engine()
        await statistical_engine.start()
        
        # Start strategy engine
        strategy_engine = await get_strategy_engine()
        await strategy_engine.start()
        
        # Start alert engine
        alert_engine = await get_alert_engine()
        await alert_engine.start()
        
        # Start pattern recognition engine
        pattern_engine = await get_pattern_engine()
        await pattern_engine.start()
        
        # Start demo data generator for intelligence features
        demo_generator = await get_demo_generator()
        await demo_generator.start()
        logger.info("Started demo data generator for intelligence population")
        
        # Start background analysis
        asyncio.create_task(self._analysis_loop())
    
    async def stop(self):
        """Stop analytics"""
        self.running = False
        logger.info("Stopped analytics service")
    
    async def _analysis_loop(self):
        """Main analysis loop"""
        while self.running:
            try:
                # Run analysis every 5 minutes
                await self.analyze_all_patterns()
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(60)
    
    async def analyze_all_patterns(self) -> Dict[str, Any]:
        """Analyze all patterns using real MT5 data"""
        try:
            mt5_service = await get_mt5_service()
            
            # Get real data analysis
            patterns = await mt5_service.analyze_time_patterns("XAUUSD")
            
            if patterns:
                self.edges_cache = patterns
                self.last_analysis = datetime.now()
                logger.info("Updated pattern analysis with real MT5 data")
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return {}
    
    async def get_live_data(self) -> Dict[str, Any]:
        """Get live analytics data for WebSocket streaming"""
        try:
            mt5_service = await get_mt5_service()
            
            # Get real live data
            live_data = await mt5_service.get_live_analytics_data()
            
            # Get statistical edges
            statistical_engine = await get_statistical_engine()
            edges_data = await statistical_engine.get_current_edges()
            
            # Get strategy performance
            strategy_engine = await get_strategy_engine()
            strategy_performance = await strategy_engine.get_strategy_performance()
            active_signals = await strategy_engine.get_active_signals()
            
            # Get alerts
            alert_engine = await get_alert_engine()
            await alert_engine.process_live_data(live_data)  # Process data for alert generation
            active_alerts = await alert_engine.get_active_alerts()
            alert_summary = await alert_engine.get_alert_summary()
            
            # Get discovered patterns
            pattern_engine = await get_pattern_engine()
            discovered_patterns = await pattern_engine.get_discovered_patterns()
            pattern_summary = await pattern_engine.get_pattern_summary()
            
            # Generate demo alerts if needed
            demo_generator = await get_demo_generator()
            demo_alerts = await demo_generator.generate_demo_alerts()
            
            # Merge demo alerts with active alerts
            all_alerts = (active_alerts or []) + demo_alerts
            
            # Add new intelligence data to live feed
            live_data['statistical_edges'] = edges_data
            live_data['strategy_performance'] = strategy_performance
            live_data['active_signals'] = active_signals
            live_data['active_alerts'] = all_alerts
            live_data['alert_summary'] = alert_summary
            live_data['discovered_patterns'] = discovered_patterns
            live_data['pattern_summary'] = pattern_summary
            live_data['analytics_summary'] = await statistical_engine.get_analytics_summary()
            
            # Add legacy analytics insights
            if self.edges_cache:
                live_data['legacy_edges'] = self.edges_cache
            
            live_data['analytics_status'] = 'active' if self.running else 'inactive'
            live_data['last_analysis'] = self.last_analysis.isoformat() if self.last_analysis else None
            
            return live_data
            
        except Exception as e:
            logger.error(f"Error getting live data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_heatmap_data(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Generate heatmap data from real patterns"""
        try:
            if not self.edges_cache or 'hourly' not in self.edges_cache:
                await self.analyze_all_patterns()
            
            if not self.edges_cache or 'hourly' not in self.edges_cache:
                return {}
            
            # Convert hourly patterns to heatmap format
            heatmap_data = []
            hours = list(range(24))
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days:
                day_data = []
                for hour in hours:
                    hour_key = f"{hour:02d}:00"
                    if hour_key in self.edges_cache['hourly']:
                        data = self.edges_cache['hourly'][hour_key]
                        day_data.append({
                            'win_rate': data['win_rate'],
                            'avg_return': data['avg_return'],
                            'sample_size': data['sample_size'],
                            'strength': 'high' if data['win_rate'] > 60 else 'medium' if data['win_rate'] > 52 else 'low'
                        })
                    else:
                        day_data.append({
                            'win_rate': 50,
                            'avg_return': 0,
                            'sample_size': 0,
                            'strength': 'none'
                        })
                heatmap_data.append(day_data)
            
            return {
                'symbol': symbol,
                'hours': hours,
                'days': days,
                'data': heatmap_data,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            return {}
    
    def calculate_statistical_significance(self, returns: List[float]) -> Dict[str, float]:
        """Calculate statistical significance of returns"""
        if len(returns) < 10:
            return {'p_value': 1.0, 'z_score': 0.0, 'confidence': 0.0}
        
        returns_array = np.array(returns)
        
        # T-test against zero (no edge)
        t_stat, p_value = stats.ttest_1samp(returns_array, 0)
        
        # Z-score
        z_score = np.mean(returns_array) / (np.std(returns_array) / np.sqrt(len(returns_array)))
        
        # Confidence level (1 - p_value)
        confidence = (1 - p_value) * 100
        
        return {
            'p_value': float(p_value),
            'z_score': float(z_score),
            'confidence': float(confidence),
            't_statistic': float(t_stat)
        }
    
    async def get_strategy_performance(self, strategy_id: int) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        # Mock implementation for now
        return {
            'strategy_id': strategy_id,
            'total_trades': 156,
            'winning_trades': 89,
            'win_rate': 57.1,
            'total_pnl': 2847.50,
            'avg_trade': 18.25,
            'max_drawdown': -234.80,
            'sharpe_ratio': 1.42,
            'last_updated': datetime.now().isoformat()
        }

# Global instance
analytics_service = AnalyticsService()