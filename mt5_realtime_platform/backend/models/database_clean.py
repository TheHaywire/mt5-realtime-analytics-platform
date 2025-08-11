#!/usr/bin/env python3
"""
Database models and connection setup for MT5 Real-Time Analytics Platform
SQLAlchemy ORM models for users, strategies, bars, alerts, and analytics data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from pathlib import Path

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./mt5_analytics.db')

# Ensure data directory exists for SQLite
if DATABASE_URL.startswith('sqlite'):
    db_path = DATABASE_URL.replace('sqlite:///', '')
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# Create engine with optimized settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

class User(Base):
    """
    User accounts for SaaS platform
    Supports free, pro, and enterprise tiers
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    
    # Subscription info
    plan = Column(String, default="free")  # free, pro, enterprise
    rate_limit = Column(Integer, default=100)  # API calls per hour
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    strategies = relationship("Strategy", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    api_usage = relationship("APIUsage", back_populates="user")

class BarData(Base):
    """
    OHLCV bar data from MT5
    Stores 1-minute bars aggregated from tick data
    """
    __tablename__ = "bar_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, nullable=False)
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False) 
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Additional data
    spread = Column(Float)
    tick_count = Column(Integer)
    
    # Timestamps
    timestamp = Column(DateTime, index=True, nullable=False)  # Bar timestamp
    created_at = Column(DateTime, default=func.now())  # Database insert time
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_bar_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_bar_timeframe_timestamp', 'timeframe', 'timestamp'),
    )

class TickData(Base):
    """
    Raw tick data from MT5 (optional storage)
    For high-frequency analysis and validation
    """
    __tablename__ = "tick_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    
    # Tick data
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    volume = Column(Integer)
    spread = Column(Float)
    
    # Timestamps
    timestamp = Column(DateTime, index=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Strategy(Base):
    """
    User-defined trading strategies
    Configuration and performance tracking
    """
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Strategy info
    name = Column(String, nullable=False)
    description = Column(Text)
    strategy_type = Column(String, nullable=False)  # time_based, pattern, custom
    
    # Configuration (JSON stored as text)
    config = Column(Text, nullable=False)  # JSON string
    
    # Status and performance
    is_active = Column(Boolean, default=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")

class Trade(Base):
    """
    Individual trade executions and backtests
    Links to strategies for performance tracking
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # Trade details
    symbol = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # long, short
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    position_size = Column(Float, nullable=False)
    
    # P&L and metrics
    pnl_pips = Column(Float)
    pnl_dollars = Column(Float)
    pnl_percentage = Column(Float)
    
    # Trade timing
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Market conditions
    entry_spread = Column(Float)
    exit_spread = Column(Float)
    market_volatility = Column(Float)
    
    # Status
    status = Column(String, default="open")  # open, closed, cancelled
    is_backtest = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    strategy = relationship("Strategy", back_populates="trades")

class StatisticalEdge(Base):
    """
    Discovered statistical edges and patterns
    Time-based and pattern-based analysis results
    """
    __tablename__ = "statistical_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Edge identification
    symbol = Column(String, nullable=False)
    edge_type = Column(String, nullable=False)  # time_of_day, day_of_week, pattern
    pattern_key = Column(String, nullable=False)  # e.g., "03:17", "Friday", "breakout"
    
    # Statistical metrics
    win_rate = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)  # p-value based
    sample_size = Column(Integer, nullable=False)
    avg_return = Column(Float, nullable=False)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    
    # Edge strength and significance
    edge_strength = Column(Float, nullable=False)  # Combined metric
    is_significant = Column(Boolean, default=False)
    z_score = Column(Float)
    p_value = Column(Float)
    
    # Analysis period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    timeframe = Column(String, nullable=False)
    
    # Timestamps
    discovered_at = Column(DateTime, default=func.now())
    last_validated = Column(DateTime, default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_edge_symbol_type', 'symbol', 'edge_type'),
        Index('ix_edge_pattern_key', 'pattern_key'),
        Index('ix_edge_discovered', 'discovered_at'),
    )

class Alert(Base):
    """
    User alert configurations and history
    Email, Telegram, and webhook notifications
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert configuration
    name = Column(String, nullable=False)
    description = Column(Text)
    alert_type = Column(String, nullable=False)  # edge_discovery, strategy_performance, system
    
    # Trigger conditions (JSON)
    conditions = Column(Text, nullable=False)  # JSON string
    
    # Delivery settings
    channels = Column(String, nullable=False)  # comma-separated: email,telegram,webhook
    webhook_url = Column(String)
    
    # Status and limits
    is_active = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=30)
    max_triggers_per_day = Column(Integer, default=10)
    
    # Statistics
    total_triggers = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    notifications = relationship("Notification", back_populates="alert")

class Notification(Base):
    """
    Alert notification history
    Tracks sent notifications for analytics
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    
    # Notification details
    channel = Column(String, nullable=False)  # email, telegram, webhook
    recipient = Column(String, nullable=False)  # email address, chat_id, webhook_url
    subject = Column(String)
    message = Column(Text, nullable=False)
    
    # Delivery status
    status = Column(String, default="pending")  # pending, sent, failed, delivered
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Relationships
    alert = relationship("Alert", back_populates="notifications")

class APIUsage(Base):
    """
    API usage tracking for rate limiting and analytics
    Tracks user API calls and billing
    """
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request details
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Response details
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    
    # Usage tracking
    api_key_used = Column(String, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="api_usage")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_usage_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_usage_endpoint_timestamp', 'endpoint', 'timestamp'),
    )

class SystemMetric(Base):
    """
    System performance and health metrics
    For monitoring and analytics
    """
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric details
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String)  # requests/sec, %, MB, etc.
    
    # Context
    component = Column(String)  # api, websocket, analytics, mt5
    tags = Column(String)  # JSON string for additional metadata
    
    # Timestamp
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_metric_name_timestamp', 'metric_name', 'timestamp'),
        Index('ix_metric_component_timestamp', 'component', 'timestamp'),
    )

# Database utility functions
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def drop_all_tables():
    """Drop all tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")

# Database connection test
def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        # Test query
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing MT5 Analytics Database...")
    init_database()
    
    if test_connection():
        print("[OK] Database connection successful")
    else:
        print("[ERROR] Database connection failed")
        
    print(f"Database URL: {DATABASE_URL}")
    print("Database setup complete!")