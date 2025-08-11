#!/usr/bin/env python3
"""
Smart Alert Engine for High-Confidence Trading Setups
Generates real-time alerts based on statistical edges and strategy signals
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertType(Enum):
    STRATEGY_SIGNAL = "strategy_signal"
    STATISTICAL_EDGE = "statistical_edge"
    RISK_WARNING = "risk_warning"
    MARKET_OPPORTUNITY = "market_opportunity"
    PERFORMANCE_UPDATE = "performance_update"

class AlertPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TradingAlert:
    """Trading alert with full context"""
    id: str
    timestamp: datetime
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    symbol: str
    price: float
    confidence: float
    action: str  # BUY, SELL, HOLD, CLOSE
    reasoning: str
    risk_level: str  # LOW, MEDIUM, HIGH
    expected_move: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    expires_at: Optional[datetime]
    is_active: bool = True
    metadata: Dict[str, Any] = None

class SmartAlertEngine:
    """Intelligent alert system for trading opportunities and risks"""
    
    def __init__(self):
        self.is_running = False
        self.active_alerts = {}
        self.alert_history = []
        self.alert_rules = {}
        self.last_prices = {}
        self.performance_tracker = {}
        
        # Alert configuration
        self.max_alerts_per_hour = 10
        self.min_confidence_threshold = 70.0
        self.alert_cooldown_minutes = 15
        
        # Initialize alert rules
        self._initialize_alert_rules()
    
    def _initialize_alert_rules(self):
        """Initialize smart alert rules based on trading intelligence"""
        
        # Rule 1: High-confidence strategy signals
        self.alert_rules['high_confidence_signal'] = {
            'condition': lambda data: self._check_high_confidence_signals(data),
            'priority': AlertPriority.HIGH,
            'cooldown_minutes': 30,
            'max_per_day': 5
        }
        
        # Rule 2: Statistical edge activation
        self.alert_rules['statistical_edge'] = {
            'condition': lambda data: self._check_statistical_edges(data),
            'priority': AlertPriority.MEDIUM,
            'cooldown_minutes': 45,
            'max_per_day': 8
        }
        
        # Rule 3: Risk warnings
        self.alert_rules['risk_warning'] = {
            'condition': lambda data: self._check_risk_conditions(data),
            'priority': AlertPriority.CRITICAL,
            'cooldown_minutes': 10,
            'max_per_day': 20
        }
        
        # Rule 4: Market opportunity windows
        self.alert_rules['market_opportunity'] = {
            'condition': lambda data: self._check_market_opportunities(data),
            'priority': AlertPriority.MEDIUM,
            'cooldown_minutes': 60,
            'max_per_day': 6
        }
        
        # Rule 5: Performance milestones
        self.alert_rules['performance_milestone'] = {
            'condition': lambda data: self._check_performance_milestones(data),
            'priority': AlertPriority.LOW,
            'cooldown_minutes': 120,
            'max_per_day': 3
        }
    
    async def start(self):
        """Start the alert engine"""
        self.is_running = True
        logger.info("Starting Smart Alert Engine...")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Stop the alert engine"""
        self.is_running = False
        logger.info("Stopped Smart Alert Engine")
    
    async def _monitoring_loop(self):
        """Main alert monitoring loop"""
        while self.is_running:
            try:
                # Check all alert rules
                await self._process_alert_rules()
                
                # Clean up expired alerts
                await self._cleanup_expired_alerts()
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _process_alert_rules(self):
        """Process all alert rules - placeholder implementation"""
        try:
            # Simple implementation - just track that we're processing
            logger.debug("Processing alert rules...")
        except Exception as e:
            logger.error(f"Process alert rules error: {e}")
    
    async def _cleanup_expired_alerts(self):
        """Remove expired alerts"""
        current_time = datetime.now()
        expired_ids = []
        
        for alert_id, alert in list(self.active_alerts.items()):
            if hasattr(alert, 'expires_at') and alert.expires_at and current_time > alert.expires_at:
                expired_ids.append(alert_id)
        
        for alert_id in expired_ids:
            del self.active_alerts[alert_id]
    
    async def process_live_data(self, data: Dict[str, Any]):
        """Process live data for alert generation"""
        try:
            # Update price tracking
            if data.get('live_rates'):
                for symbol, rate_data in data['live_rates'].items():
                    self.last_prices[symbol] = {
                        'price': rate_data.get('bid', 0),
                        'timestamp': datetime.now(),
                        'spread': rate_data.get('spread', 0)
                    }
            
            # Check each alert rule
            for rule_name, rule_config in self.alert_rules.items():
                try:
                    if rule_config['condition'](data):
                        await self._generate_alert_from_rule(rule_name, rule_config, data)
                except Exception as e:
                    logger.error(f"Error checking rule {rule_name}: {e}")
            
        except Exception as e:
            logger.error(f"Error processing live data for alerts: {e}")
    
    def _check_high_confidence_signals(self, data: Dict[str, Any]) -> bool:
        """Check for high-confidence strategy signals"""
        if not data.get('active_signals'):
            return False
        
        # Look for signals with confidence >= 80%
        for signal in data['active_signals']:
            if signal.get('confidence', 0) >= 80:
                return True
        
        return False
    
    def _check_statistical_edges(self, data: Dict[str, Any]) -> bool:
        """Check for strong statistical edges"""
        if not data.get('statistical_edges'):
            return False
        
        # Look for edges with strength >= 70 and win rate >= 65%
        for edge_key, edge in data['statistical_edges'].items():
            if (edge.get('strength', 0) >= 70 and 
                edge.get('win_rate', 0) >= 65 and 
                edge.get('is_active', False)):
                return True
        
        return False
    
    def _check_risk_conditions(self, data: Dict[str, Any]) -> bool:
        """Check for risk warning conditions"""
        if not data.get('live_rates'):
            return False
        
        # Check for high volatility (large spreads)
        for symbol, rate_data in data['live_rates'].items():
            spread = rate_data.get('spread', 0)
            
            # Alert if GOLD spread > 0.8 (high volatility)
            if symbol in ['GOLD', 'XAUUSD'] and spread > 0.8:
                return True
            
            # Alert if major pair spread unusually high
            if symbol in ['EURUSD', 'GBPUSD'] and spread > 0.0003:
                return True
        
        return False
    
    def _check_market_opportunities(self, data: Dict[str, Any]) -> bool:
        """Check for market opportunity windows"""
        current_hour = datetime.now().hour
        
        # Check for prime trading hours (London/NY overlap)
        if 13 <= current_hour <= 16:  # 1PM-4PM GMT (major session overlap)
            # Check if we have active statistical edges during this time
            if data.get('statistical_edges'):
                active_edges = sum(1 for edge in data['statistical_edges'].values() 
                                 if edge.get('is_active', False))
                if active_edges >= 2:
                    return True
        
        return False
    
    def _check_performance_milestones(self, data: Dict[str, Any]) -> bool:
        """Check for performance milestone achievements"""
        if not data.get('strategy_performance'):
            return False
        
        # Check for strategies hitting win rate milestones
        for strategy_id, performance in data['strategy_performance'].items():
            win_rate = performance.get('win_rate', 0)
            total_signals = performance.get('total_signals', 0)
            
            # Alert on significant milestones
            if total_signals >= 10 and win_rate >= 75:  # Excellent performance
                return True
            elif total_signals >= 5 and win_rate <= 30:  # Poor performance warning
                return True
        
        return False
    
    async def _generate_alert_from_rule(self, rule_name: str, rule_config: dict, data: Dict[str, Any]):
        """Generate an alert based on a triggered rule"""
        
        # Check cooldown
        if not self._can_send_alert(rule_name):
            return
        
        # Generate specific alert based on rule type
        alert = None
        
        if rule_name == 'high_confidence_signal':
            alert = await self._create_signal_alert(data)
        elif rule_name == 'statistical_edge':
            alert = await self._create_edge_alert(data)
        elif rule_name == 'risk_warning':
            alert = await self._create_risk_alert(data)
        elif rule_name == 'market_opportunity':
            alert = await self._create_opportunity_alert(data)
        elif rule_name == 'performance_milestone':
            alert = await self._create_performance_alert(data)
        
        if alert:
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
            logger.info(f"Generated {rule_name} alert: {alert.title}")
    
    async def _create_signal_alert(self, data: Dict[str, Any]) -> Optional[TradingAlert]:
        """Create alert for high-confidence strategy signal"""
        if not data.get('active_signals'):
            return None
        
        # Find the highest confidence signal
        best_signal = max(data['active_signals'], 
                         key=lambda s: s.get('confidence', 0))
        
        if best_signal.get('confidence', 0) < 80:
            return None
        
        alert_id = f"signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TradingAlert(
            id=alert_id,
            timestamp=datetime.now(),
            type=AlertType.STRATEGY_SIGNAL,
            priority=AlertPriority.HIGH,
            title=f"🎯 High-Confidence {best_signal.get('signal_type', 'SIGNAL')}",
            message=f"{best_signal.get('strategy', 'Strategy')} generated {best_signal.get('signal_type')} signal with {best_signal.get('confidence', 0):.1f}% confidence",
            symbol=best_signal.get('symbol', 'GOLD'),
            price=best_signal.get('price', 0),
            confidence=best_signal.get('confidence', 0),
            action=best_signal.get('signal_type', 'HOLD'),
            reasoning=best_signal.get('reasoning', 'High probability setup detected'),
            risk_level=best_signal.get('risk_level', 'MEDIUM'),
            expected_move=None,
            stop_loss=best_signal.get('stop_loss'),
            take_profit=best_signal.get('take_profit'),
            expires_at=datetime.now() + timedelta(hours=2),
            metadata={'strategy': best_signal.get('strategy'), 'original_signal': best_signal}
        )
    
    async def _create_edge_alert(self, data: Dict[str, Any]) -> Optional[TradingAlert]:
        """Create alert for strong statistical edge"""
        if not data.get('statistical_edges'):
            return None
        
        # Find strongest active edge
        best_edge = None
        best_strength = 0
        
        for edge_key, edge in data['statistical_edges'].items():
            if (edge.get('is_active', False) and 
                edge.get('strength', 0) > best_strength and
                edge.get('win_rate', 0) >= 65):
                best_edge = edge
                best_strength = edge.get('strength', 0)
        
        if not best_edge:
            return None
        
        alert_id = f"edge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TradingAlert(
            id=alert_id,
            timestamp=datetime.now(),
            type=AlertType.STATISTICAL_EDGE,
            priority=AlertPriority.MEDIUM,
            title=f"⚡ Statistical Edge Active",
            message=f"{best_edge.get('name', 'Pattern')} showing {best_edge.get('strength', 0):.0f}% strength with {best_edge.get('win_rate', 0):.1f}% win rate",
            symbol='GOLD',
            price=self.last_prices.get('GOLD', {}).get('price', 0),
            confidence=best_edge.get('strength', 0),
            action=best_edge.get('direction', 'HOLD').upper(),
            reasoning=f"Historical pattern with {best_edge.get('total_trades', 0)} samples",
            risk_level='MEDIUM',
            expected_move=None,
            stop_loss=None,
            take_profit=None,
            expires_at=datetime.now() + timedelta(hours=1),
            metadata={'edge_type': best_edge.get('type'), 'period': best_edge.get('period')}
        )
    
    async def _create_risk_alert(self, data: Dict[str, Any]) -> Optional[TradingAlert]:
        """Create risk warning alert"""
        if not data.get('live_rates'):
            return None
        
        risk_symbols = []
        for symbol, rate_data in data['live_rates'].items():
            spread = rate_data.get('spread', 0)
            
            if symbol in ['GOLD', 'XAUUSD'] and spread > 0.8:
                risk_symbols.append(f"{symbol} (spread: {spread:.2f})")
            elif symbol in ['EURUSD', 'GBPUSD'] and spread > 0.0003:
                risk_symbols.append(f"{symbol} (spread: {spread*10000:.1f} pips)")
        
        if not risk_symbols:
            return None
        
        alert_id = f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TradingAlert(
            id=alert_id,
            timestamp=datetime.now(),
            type=AlertType.RISK_WARNING,
            priority=AlertPriority.CRITICAL,
            title="⚠️ High Volatility Warning",
            message=f"Elevated spreads detected: {', '.join(risk_symbols)}. Consider reducing position sizes.",
            symbol='MULTIPLE',
            price=0,
            confidence=90.0,
            action='REDUCE_RISK',
            reasoning="Abnormally high spreads indicate increased market volatility and risk",
            risk_level='HIGH',
            expected_move=None,
            stop_loss=None,
            take_profit=None,
            expires_at=datetime.now() + timedelta(minutes=30),
            metadata={'risk_symbols': risk_symbols}
        )
    
    async def _create_opportunity_alert(self, data: Dict[str, Any]) -> Optional[TradingAlert]:
        """Create market opportunity alert"""
        current_hour = datetime.now().hour
        
        if not (13 <= current_hour <= 16):  # Prime trading hours
            return None
        
        active_edges = 0
        if data.get('statistical_edges'):
            active_edges = sum(1 for edge in data['statistical_edges'].values() 
                             if edge.get('is_active', False))
        
        if active_edges < 2:
            return None
        
        alert_id = f"opportunity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TradingAlert(
            id=alert_id,
            timestamp=datetime.now(),
            type=AlertType.MARKET_OPPORTUNITY,
            priority=AlertPriority.MEDIUM,
            title="🚀 Prime Trading Window",
            message=f"London/NY session overlap with {active_edges} active statistical edges detected",
            symbol='GOLD',
            price=self.last_prices.get('GOLD', {}).get('price', 0),
            confidence=75.0,
            action='MONITOR',
            reasoning="High-volume session with multiple confirmed patterns active",
            risk_level='MEDIUM',
            expected_move=None,
            stop_loss=None,
            take_profit=None,
            expires_at=datetime.now() + timedelta(hours=1),
            metadata={'session': 'london_ny_overlap', 'active_edges': active_edges}
        )
    
    async def _create_performance_alert(self, data: Dict[str, Any]) -> Optional[TradingAlert]:
        """Create performance milestone alert"""
        if not data.get('strategy_performance'):
            return None
        
        milestone_strategy = None
        milestone_type = None
        
        for strategy_id, performance in data['strategy_performance'].items():
            win_rate = performance.get('win_rate', 0)
            total_signals = performance.get('total_signals', 0)
            
            if total_signals >= 10 and win_rate >= 75:
                milestone_strategy = performance
                milestone_type = 'excellent'
                break
            elif total_signals >= 5 and win_rate <= 30:
                milestone_strategy = performance
                milestone_type = 'poor'
                break
        
        if not milestone_strategy:
            return None
        
        alert_id = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if milestone_type == 'excellent':
            return TradingAlert(
                id=alert_id,
                timestamp=datetime.now(),
                type=AlertType.PERFORMANCE_UPDATE,
                priority=AlertPriority.LOW,
                title="🏆 Strategy Milestone",
                message=f"{milestone_strategy.get('name', 'Strategy')} achieved {milestone_strategy.get('win_rate', 0):.1f}% win rate over {milestone_strategy.get('total_signals', 0)} signals",
                symbol='MULTIPLE',
                price=0,
                confidence=100.0,
                action='CONTINUE',
                reasoning="Excellent strategy performance milestone reached",
                risk_level='LOW',
                expected_move=None,
                stop_loss=None,
                take_profit=None,
                expires_at=datetime.now() + timedelta(hours=24),
                metadata={'milestone_type': 'excellent', 'strategy': milestone_strategy}
            )
        else:  # poor performance
            return TradingAlert(
                id=alert_id,
                timestamp=datetime.now(),
                type=AlertType.PERFORMANCE_UPDATE,
                priority=AlertPriority.MEDIUM,
                title="⚠️ Strategy Review Needed",
                message=f"{milestone_strategy.get('name', 'Strategy')} showing {milestone_strategy.get('win_rate', 0):.1f}% win rate - consider review",
                symbol='MULTIPLE',
                price=0,
                confidence=80.0,
                action='REVIEW',
                reasoning="Poor strategy performance requires attention",
                risk_level='MEDIUM',
                expected_move=None,
                stop_loss=None,
                take_profit=None,
                expires_at=datetime.now() + timedelta(hours=8),
                metadata={'milestone_type': 'poor', 'strategy': milestone_strategy}
            )
    
    def _can_send_alert(self, rule_name: str) -> bool:
        """Check if we can send an alert for this rule (cooldown logic)"""
        # Implementation would check cooldown periods, daily limits, etc.
        # For now, simplified version
        return True
    
    async def _cleanup_expired_alerts(self):
        """Remove expired alerts"""
        current_time = datetime.now()
        expired_alerts = []
        
        for alert_id, alert in self.active_alerts.items():
            if alert.expires_at and alert.expires_at < current_time:
                expired_alerts.append(alert_id)
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
            logger.info(f"Cleaned up expired alert: {alert_id}")
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        alerts = []
        for alert in self.active_alerts.values():
            alerts.append({
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.type.value,
                'priority': alert.priority.value,
                'title': alert.title,
                'message': alert.message,
                'symbol': alert.symbol,
                'price': alert.price,
                'confidence': alert.confidence,
                'action': alert.action,
                'reasoning': alert.reasoning,
                'risk_level': alert.risk_level,
                'stop_loss': alert.stop_loss,
                'take_profit': alert.take_profit,
                'expires_at': alert.expires_at.isoformat() if alert.expires_at else None,
                'metadata': alert.metadata
            })
        
        # Sort by priority and timestamp
        alerts.sort(key=lambda x: (x['priority'], x['timestamp']), reverse=True)
        return alerts
    
    async def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary"""
        return {
            'active_alerts': len(self.active_alerts),
            'alerts_today': len([a for a in self.alert_history 
                               if a.timestamp.date() == datetime.now().date()]),
            'high_priority_alerts': len([a for a in self.active_alerts.values() 
                                       if a.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]]),
            'alert_rules_active': len(self.alert_rules),
            'last_alert': max([a.timestamp for a in self.active_alerts.values()]).isoformat() if self.active_alerts else None
        }

# Global alert engine instance
alert_engine = SmartAlertEngine()

async def get_alert_engine() -> SmartAlertEngine:
    """Get the global alert engine instance"""
    return alert_engine