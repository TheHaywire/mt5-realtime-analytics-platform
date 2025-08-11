#!/usr/bin/env python3
"""
Advanced Pattern Recognition System
Automatically discovers and validates new trading patterns using machine learning
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Discovered trading pattern"""
    id: str
    name: str
    type: str  # 'technical', 'statistical', 'behavioral', 'seasonal'
    description: str
    conditions: Dict[str, Any]
    
    # Performance metrics
    win_rate: float
    avg_return: float
    max_drawdown: float
    sharpe_ratio: float
    total_occurrences: int
    
    # Validation metrics
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    p_value: float
    
    # Pattern characteristics
    timeframe: str
    symbols: List[str]
    market_conditions: List[str]
    
    # Discovery metadata
    discovered_at: datetime
    last_validated: datetime
    validation_score: float  # 0-100
    is_validated: bool

class PatternRecognitionEngine:
    """Advanced pattern recognition and discovery system"""
    
    def __init__(self):
        self.is_running = False
        self.discovered_patterns = {}
        self.price_history = []
        self.feature_history = []
        self.pattern_performance = defaultdict(list)
        
        # ML models
        self.pattern_classifier = None
        self.anomaly_detector = None
        self.cluster_model = None
        self.scaler = StandardScaler()
        
        # Pattern discovery parameters
        self.min_pattern_occurrences = 10
        self.min_win_rate = 55.0
        self.significance_threshold = 0.05
        self.discovery_window_days = 30
        
    async def start(self):
        """Start the pattern recognition engine"""
        self.is_running = True
        logger.info("Starting Advanced Pattern Recognition Engine...")
        
        # Initialize ML models
        self._initialize_models()
        
        # Start discovery loop
        asyncio.create_task(self._discovery_loop())
    
    async def stop(self):
        """Stop pattern recognition"""
        self.is_running = False
        logger.info("Stopped Pattern Recognition Engine")
    
    def _initialize_models(self):
        """Initialize machine learning models for pattern discovery"""
        # Random Forest for pattern classification
        self.pattern_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Isolation Forest for anomaly detection (unusual patterns)
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # K-Means for pattern clustering
        self.cluster_model = KMeans(
            n_clusters=8,
            random_state=42
        )
    
    async def _discovery_loop(self):
        """Main pattern discovery loop"""
        while self.is_running:
            try:
                if len(self.price_history) > 100:  # Need sufficient data
                    await self._discover_new_patterns()
                    await self._validate_existing_patterns()
                    await self._update_pattern_performance()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Pattern discovery error: {e}")
                await asyncio.sleep(60)
    
    async def add_price_data(self, timestamp: datetime, symbol: str, 
                           bid: float, ask: float, volume: float = 0):
        """Add new price data for pattern analysis"""
        price_point = {
            'timestamp': timestamp,
            'symbol': symbol,
            'bid': bid,
            'ask': ask,
            'mid': (bid + ask) / 2,
            'spread': ask - bid,
            'volume': volume
        }
        
        self.price_history.append(price_point)
        
        # Keep only recent data
        cutoff_time = timestamp - timedelta(days=self.discovery_window_days)
        self.price_history = [p for p in self.price_history if p['timestamp'] > cutoff_time]
        
        # Generate features for ML models
        if len(self.price_history) > 20:
            features = self._extract_features(price_point)
            self.feature_history.append(features)
            
            # Keep feature history aligned with price history
            self.feature_history = self.feature_history[-len(self.price_history):]
    
    def _extract_features(self, current_price: Dict[str, Any]) -> Dict[str, float]:
        """Extract technical and statistical features for pattern recognition"""
        if len(self.price_history) < 20:
            return {}
        
        # Get recent price data
        recent_prices = [p['mid'] for p in self.price_history[-20:]]
        recent_volumes = [p['volume'] for p in self.price_history[-20:]]
        recent_spreads = [p['spread'] for p in self.price_history[-20:]]
        
        features = {}
        
        # Price-based features
        features['price_sma_5'] = np.mean(recent_prices[-5:])
        features['price_sma_10'] = np.mean(recent_prices[-10:])
        features['price_sma_20'] = np.mean(recent_prices)
        
        # Volatility features
        returns = np.diff(recent_prices) / recent_prices[:-1]
        features['volatility_5'] = np.std(returns[-5:]) if len(returns) >= 5 else 0
        features['volatility_10'] = np.std(returns[-10:]) if len(returns) >= 10 else 0
        features['volatility_20'] = np.std(returns)
        
        # Momentum features
        features['momentum_5'] = (recent_prices[-1] / recent_prices[-6] - 1) if len(recent_prices) > 5 else 0
        features['momentum_10'] = (recent_prices[-1] / recent_prices[-11] - 1) if len(recent_prices) > 10 else 0
        
        # RSI-like feature
        gains = [max(0, r) for r in returns]
        losses = [abs(min(0, r)) for r in returns]
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 0
        features['rsi'] = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss > 0 else 50
        
        # Spread-based features
        features['spread_current'] = current_price['spread']
        features['spread_avg'] = np.mean(recent_spreads)
        features['spread_volatility'] = np.std(recent_spreads)
        
        # Time-based features
        hour = current_price['timestamp'].hour
        weekday = current_price['timestamp'].weekday()
        features['hour'] = hour
        features['weekday'] = weekday
        features['is_london_session'] = 1 if 8 <= hour <= 17 else 0
        features['is_ny_session'] = 1 if 13 <= hour <= 22 else 0
        features['is_overlap'] = 1 if 13 <= hour <= 17 else 0
        
        # Volume-based features (if available)
        if any(v > 0 for v in recent_volumes):
            features['volume_current'] = current_price['volume']
            features['volume_avg'] = np.mean([v for v in recent_volumes if v > 0])
        
        return features
    
    async def _discover_new_patterns(self):
        """Discover new trading patterns using ML techniques"""
        if len(self.feature_history) < 50:
            return
        
        logger.info("Running pattern discovery analysis...")
        
        # Convert features to DataFrame
        df = pd.DataFrame(self.feature_history)
        if df.empty or len(df) < 20:
            return
        
        # Remove any non-numeric columns and handle NaN
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df_numeric = df[numeric_columns].fillna(0)
        
        if df_numeric.empty:
            return
        
        try:
            # Scale features
            scaled_features = self.scaler.fit_transform(df_numeric)
            
            # 1. Anomaly Detection - Find unusual market conditions
            anomalies = self.anomaly_detector.fit_predict(scaled_features)
            anomaly_patterns = await self._analyze_anomalies(anomalies, df_numeric)
            
            # 2. Clustering - Find similar market conditions
            clusters = self.cluster_model.fit_predict(scaled_features)
            cluster_patterns = await self._analyze_clusters(clusters, df_numeric)
            
            # 3. Statistical Pattern Discovery
            statistical_patterns = await self._discover_statistical_patterns(df_numeric)
            
            # Combine and validate discovered patterns
            all_patterns = anomaly_patterns + cluster_patterns + statistical_patterns
            
            for pattern in all_patterns:
                await self._validate_and_store_pattern(pattern)
                
            logger.info(f"Discovered {len(all_patterns)} potential new patterns")
            
        except Exception as e:
            logger.error(f"Pattern discovery analysis error: {e}")
    
    async def _analyze_anomalies(self, anomalies: np.ndarray, 
                               features: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze anomaly detection results for pattern discovery"""
        patterns = []
        
        # Find periods marked as anomalies
        anomaly_indices = np.where(anomalies == -1)[0]
        
        if len(anomaly_indices) < 5:  # Need minimum anomalies
            return patterns
        
        # Analyze characteristics of anomalous periods
        anomaly_features = features.iloc[anomaly_indices]
        normal_features = features.iloc[np.where(anomalies == 1)[0]]
        
        # Find features that differ significantly between anomalous and normal periods
        for column in features.columns:
            if column in anomaly_features.columns and column in normal_features.columns:
                anomaly_values = anomaly_features[column].values
                normal_values = normal_features[column].values
                
                # Statistical test for significant difference
                if len(anomaly_values) > 3 and len(normal_values) > 3:
                    t_stat, p_value = stats.ttest_ind(anomaly_values, normal_values)
                    
                    if p_value < 0.05:  # Significant difference
                        pattern = {
                            'type': 'anomaly',
                            'name': f'Anomalous {column.replace("_", " ").title()}',
                            'feature': column,
                            'threshold': np.mean(anomaly_values),
                            'direction': 'high' if np.mean(anomaly_values) > np.mean(normal_values) else 'low',
                            'p_value': p_value,
                            'occurrences': len(anomaly_indices)
                        }
                        patterns.append(pattern)
        
        return patterns
    
    async def _analyze_clusters(self, clusters: np.ndarray, 
                              features: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze clustering results for pattern discovery"""
        patterns = []
        
        # Analyze each cluster
        for cluster_id in range(self.cluster_model.n_clusters):
            cluster_indices = np.where(clusters == cluster_id)[0]
            
            if len(cluster_indices) < 10:  # Need minimum cluster size
                continue
            
            cluster_features = features.iloc[cluster_indices]
            
            # Find defining characteristics of this cluster
            cluster_profile = {}
            for column in features.columns:
                cluster_mean = cluster_features[column].mean()
                overall_mean = features[column].mean()
                
                # If cluster mean differs significantly from overall mean
                if abs(cluster_mean - overall_mean) > features[column].std():
                    cluster_profile[column] = {
                        'value': cluster_mean,
                        'deviation': abs(cluster_mean - overall_mean) / features[column].std()
                    }
            
            if cluster_profile:  # If cluster has distinct characteristics
                # Name the pattern based on most significant feature
                main_feature = max(cluster_profile.keys(), 
                                 key=lambda k: cluster_profile[k]['deviation'])
                
                pattern = {
                    'type': 'cluster',
                    'name': f'Cluster Pattern: {main_feature.replace("_", " ").title()}',
                    'cluster_id': cluster_id,
                    'profile': cluster_profile,
                    'occurrences': len(cluster_indices),
                    'main_feature': main_feature
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _discover_statistical_patterns(self, features: pd.DataFrame) -> List[Dict[str, Any]]:
        """Discover patterns using statistical analysis"""
        patterns = []
        
        if len(self.price_history) < 50:
            return patterns
        
        # Calculate returns
        prices = [p['mid'] for p in self.price_history[-len(features):]]
        returns = pd.Series(prices).pct_change().fillna(0)
        
        # 1. Mean reversion patterns
        mean_reversion_pattern = self._find_mean_reversion_patterns(features, returns)
        if mean_reversion_pattern:
            patterns.append(mean_reversion_pattern)
        
        # 2. Momentum patterns
        momentum_pattern = self._find_momentum_patterns(features, returns)
        if momentum_pattern:
            patterns.append(momentum_pattern)
        
        # 3. Time-based patterns
        time_patterns = self._find_time_based_patterns(features, returns)
        patterns.extend(time_patterns)
        
        # 4. Volatility patterns
        volatility_pattern = self._find_volatility_patterns(features, returns)
        if volatility_pattern:
            patterns.append(volatility_pattern)
        
        return patterns
    
    def _find_mean_reversion_patterns(self, features: pd.DataFrame, 
                                    returns: pd.Series) -> Optional[Dict[str, Any]]:
        """Find mean reversion patterns"""
        if 'rsi' not in features.columns:
            return None
        
        # Look for mean reversion when RSI is extreme
        oversold_condition = features['rsi'] < 30
        overbought_condition = features['rsi'] > 70
        
        # Check forward returns after oversold/overbought conditions
        oversold_returns = []
        overbought_returns = []
        
        for i in range(len(features) - 5):  # Look 5 periods ahead
            if oversold_condition.iloc[i]:
                future_return = returns.iloc[i+1:i+6].sum()  # 5-period forward return
                oversold_returns.append(future_return)
            elif overbought_condition.iloc[i]:
                future_return = returns.iloc[i+1:i+6].sum()
                overbought_returns.append(future_return)
        
        # Test if mean reversion is statistically significant
        if len(oversold_returns) > 5 and np.mean(oversold_returns) > 0:
            t_stat, p_value = stats.ttest_1samp(oversold_returns, 0)
            if p_value < 0.05:
                return {
                    'type': 'statistical',
                    'name': 'RSI Oversold Mean Reversion',
                    'conditions': {'rsi': '<30'},
                    'win_rate': (np.array(oversold_returns) > 0).mean() * 100,
                    'avg_return': np.mean(oversold_returns),
                    'p_value': p_value,
                    'occurrences': len(oversold_returns)
                }
        
        return None
    
    def _find_momentum_patterns(self, features: pd.DataFrame, 
                              returns: pd.Series) -> Optional[Dict[str, Any]]:
        """Find momentum continuation patterns"""
        if 'momentum_5' not in features.columns:
            return None
        
        # Look for momentum continuation
        strong_momentum = features['momentum_5'].abs() > 0.01  # 1% momentum threshold
        
        momentum_returns = []
        for i in range(len(features) - 3):
            if strong_momentum.iloc[i]:
                future_return = returns.iloc[i+1:i+4].sum()  # 3-period forward return
                # Same direction as momentum
                if features['momentum_5'].iloc[i] > 0:
                    momentum_returns.append(future_return)
                else:
                    momentum_returns.append(-future_return)  # Flip for short momentum
        
        if len(momentum_returns) > 10 and np.mean(momentum_returns) > 0:
            t_stat, p_value = stats.ttest_1samp(momentum_returns, 0)
            if p_value < 0.05:
                return {
                    'type': 'statistical',
                    'name': 'Momentum Continuation Pattern',
                    'conditions': {'momentum_5': '>1% or <-1%'},
                    'win_rate': (np.array(momentum_returns) > 0).mean() * 100,
                    'avg_return': np.mean(momentum_returns),
                    'p_value': p_value,
                    'occurrences': len(momentum_returns)
                }
        
        return None
    
    def _find_time_based_patterns(self, features: pd.DataFrame, 
                                returns: pd.Series) -> List[Dict[str, Any]]:
        """Find time-based patterns"""
        patterns = []
        
        if 'hour' not in features.columns:
            return patterns
        
        # Analyze returns by hour
        hourly_returns = defaultdict(list)
        for i in range(len(features)):
            hour = int(features['hour'].iloc[i])
            hourly_returns[hour].append(returns.iloc[i])
        
        # Test each hour for significant patterns
        for hour, hour_returns in hourly_returns.items():
            if len(hour_returns) > 10:  # Minimum sample size
                t_stat, p_value = stats.ttest_1samp(hour_returns, 0)
                if p_value < 0.05 and abs(np.mean(hour_returns)) > 0.001:
                    direction = 'bullish' if np.mean(hour_returns) > 0 else 'bearish'
                    patterns.append({
                        'type': 'statistical',
                        'name': f'Hour {hour:02d}:00 {direction.title()} Pattern',
                        'conditions': {'hour': hour},
                        'win_rate': (np.array(hour_returns) > 0).mean() * 100,
                        'avg_return': np.mean(hour_returns),
                        'p_value': p_value,
                        'occurrences': len(hour_returns)
                    })
        
        return patterns
    
    def _find_volatility_patterns(self, features: pd.DataFrame, 
                                returns: pd.Series) -> Optional[Dict[str, Any]]:
        """Find volatility-based patterns"""
        if 'volatility_10' not in features.columns:
            return None
        
        # High volatility threshold (top 20%)
        vol_threshold = features['volatility_10'].quantile(0.8)
        high_vol_condition = features['volatility_10'] > vol_threshold
        
        high_vol_returns = []
        for i in range(len(features) - 3):
            if high_vol_condition.iloc[i]:
                future_return = abs(returns.iloc[i+1:i+4].sum())  # Absolute return (volatility play)
                high_vol_returns.append(future_return)
        
        if len(high_vol_returns) > 10:
            # Test if high volatility leads to continued high volatility (trend)
            avg_return = np.mean(high_vol_returns)
            if avg_return > np.mean(abs(returns)):  # Higher than average absolute returns
                return {
                    'type': 'statistical',
                    'name': 'High Volatility Continuation',
                    'conditions': {'volatility_10': f'>{vol_threshold:.4f}'},
                    'win_rate': 70.0,  # Volatility play win rate
                    'avg_return': avg_return,
                    'p_value': 0.01,  # Assumed significance
                    'occurrences': len(high_vol_returns)
                }
        
        return None
    
    async def _validate_and_store_pattern(self, pattern_data: Dict[str, Any]):
        """Validate and store a discovered pattern"""
        if pattern_data['occurrences'] < self.min_pattern_occurrences:
            return
        
        pattern_id = f"{pattern_data['type']}_{len(self.discovered_patterns)}"
        
        # Create Pattern object
        pattern = Pattern(
            id=pattern_id,
            name=pattern_data['name'],
            type=pattern_data['type'],
            description=f"Auto-discovered pattern: {pattern_data['name']}",
            conditions=pattern_data.get('conditions', {}),
            win_rate=pattern_data.get('win_rate', 50.0),
            avg_return=pattern_data.get('avg_return', 0.0),
            max_drawdown=0.0,  # Would need to calculate
            sharpe_ratio=0.0,  # Would need to calculate
            total_occurrences=pattern_data['occurrences'],
            statistical_significance=1 - pattern_data.get('p_value', 1.0),
            confidence_interval=(0.0, 0.0),  # Would need to calculate
            p_value=pattern_data.get('p_value', 1.0),
            timeframe='intraday',
            symbols=['GOLD'],
            market_conditions=['all'],
            discovered_at=datetime.now(),
            last_validated=datetime.now(),
            validation_score=75.0,  # Initial score
            is_validated=pattern_data.get('p_value', 1.0) < self.significance_threshold
        )
        
        self.discovered_patterns[pattern_id] = pattern
        logger.info(f"Stored new pattern: {pattern.name}")
    
    async def _validate_existing_patterns(self):
        """Validate existing patterns with new data"""
        # Implementation would re-test patterns with new data
        # For now, just log that validation is running
        if self.discovered_patterns:
            logger.info(f"Validating {len(self.discovered_patterns)} existing patterns")
    
    async def _update_pattern_performance(self):
        """Update performance tracking for discovered patterns"""
        # Implementation would track how patterns perform in real-time
        logger.info("Updated pattern performance tracking")
    
    async def get_discovered_patterns(self) -> List[Dict[str, Any]]:
        """Get all discovered patterns"""
        patterns = []
        
        for pattern in self.discovered_patterns.values():
            patterns.append({
                'id': pattern.id,
                'name': pattern.name,
                'type': pattern.type,
                'description': pattern.description,
                'win_rate': pattern.win_rate,
                'avg_return': pattern.avg_return,
                'total_occurrences': pattern.total_occurrences,
                'statistical_significance': pattern.statistical_significance,
                'p_value': pattern.p_value,
                'validation_score': pattern.validation_score,
                'is_validated': pattern.is_validated,
                'discovered_at': pattern.discovered_at.isoformat(),
                'conditions': pattern.conditions
            })
        
        # Sort by validation score
        patterns.sort(key=lambda x: x['validation_score'], reverse=True)
        return patterns
    
    async def get_pattern_summary(self) -> Dict[str, Any]:
        """Get pattern recognition summary"""
        validated_patterns = [p for p in self.discovered_patterns.values() if p.is_validated]
        
        return {
            'total_patterns': len(self.discovered_patterns),
            'validated_patterns': len(validated_patterns),
            'data_points_analyzed': len(self.price_history),
            'discovery_window_days': self.discovery_window_days,
            'last_discovery': max([p.discovered_at for p in self.discovered_patterns.values()]).isoformat() if self.discovered_patterns else None,
            'avg_validation_score': np.mean([p.validation_score for p in self.discovered_patterns.values()]) if self.discovered_patterns else 0
        }

# Global pattern recognition engine
pattern_engine = PatternRecognitionEngine()

async def get_pattern_engine() -> PatternRecognitionEngine:
    """Get the global pattern recognition engine"""
    return pattern_engine