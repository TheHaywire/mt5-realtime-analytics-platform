#!/usr/bin/env python3
"""
Pydantic schemas for request/response models
Data validation and serialization for the API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    plan: str = Field(default="free")

class UserResponse(BaseModel):
    id: int
    email: str
    plan: str
    is_active: bool
    created_at: datetime
    api_key: str
    
    class Config:
        from_attributes = True

# Strategy schemas
class StrategyConfig(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str  # time_based, pattern, custom
    config: Dict[str, Any]  # Strategy-specific configuration
    is_active: bool = True

class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy_type: str
    is_active: bool
    total_trades: int
    winning_trades: int
    total_pnl: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Market data schemas
class TickData(BaseModel):
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    volume: Optional[int] = None
    spread: Optional[float] = None

class BarData(BaseModel):
    symbol: str
    timeframe: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    spread: Optional[float] = None
    
    class Config:
        from_attributes = True

# Analytics schemas
class EdgeData(BaseModel):
    symbol: str
    edge_type: str
    pattern_key: str
    win_rate: float
    confidence_level: float
    sample_size: int
    avg_return: float
    is_significant: bool
    discovered_at: datetime

class HeatmapData(BaseModel):
    symbol: str
    hours: List[int]
    days: List[str]
    data: List[List[Dict[str, float]]]
    generated_at: datetime

# Alert schemas
class AlertRule(BaseModel):
    name: str
    description: Optional[str] = None
    alert_type: str
    conditions: Dict[str, Any]
    channels: str  # comma-separated
    webhook_url: Optional[str] = None
    cooldown_minutes: int = 30
    is_active: bool = True

class AlertResponse(BaseModel):
    id: int
    name: str
    alert_type: str
    is_active: bool
    total_triggers: int
    last_triggered: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# WebSocket message schemas
class WSMessage(BaseModel):
    type: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None

class LiveDataMessage(WSMessage):
    type: str = "live_data"
    market_status: str
    total_patterns: int
    significant_edges: int
    best_edge: Optional[Dict[str, Any]]
    volatility_level: float

# API response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Subscription and billing
class PlanEnum(str, Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class UsageStats(BaseModel):
    user_id: int
    api_calls_today: int
    api_calls_month: int
    rate_limit: int
    plan: PlanEnum
    billing_cycle_start: datetime
    billing_cycle_end: datetime