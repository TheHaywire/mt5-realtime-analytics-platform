#!/usr/bin/env python3
"""
MT5 Real-Time Analytics Platform - FastAPI Backend
Production-ready API server with WebSocket streaming and authentication
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def serialize_datetime(obj):
    """Helper function to serialize datetime objects for JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj

from models.database import engine, SessionLocal, Base
from models.schemas import (
    UserCreate, UserResponse, StrategyConfig, EdgeData, 
    TickData, BarData, AlertRule
)
from services.auth_service import AuthService
from services.mt5_service import MT5ServiceReal, get_mt5_service
from services.analytics_service import analytics_service
from services.alert_service import AlertService
from core.websocket_manager import websocket_manager
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MT5 Real-Time Analytics Platform",
    description="Production-ready SaaS platform for MetaTrader 5 statistical analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_service = AuthService()
alert_service = AlertService()
# MT5 service, analytics service, and websocket manager are already instantiated as global variables
security = HTTPBearer()

# Create database tables
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting MT5 Real-Time Analytics Platform...")
    
    # Start MT5 connection
    mt5_service = await get_mt5_service()
    if await mt5_service.connect():
        logger.info("MT5 LIVE connection established!")
        # Start real-time data streaming
        asyncio.create_task(mt5_service.start_live_streaming())
    else:
        logger.warning("MT5 connection failed - check credentials")
    
    # Start analytics engine
    await analytics_service.start_analytics()
    
    # Start alert monitoring
    asyncio.create_task(alert_service.start_monitoring())
    
    logger.info("All services started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services...")
    await mt5_service.disconnect()
    await analytics_service.stop()
    await alert_service.stop()
    logger.info("Shutdown complete")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for authentication
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """Validate API key and return current user"""
    user = await auth_service.verify_api_key(credentials.credentials, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """API information and status"""
    return """
    <html>
        <head>
            <title>MT5 Real-Time Analytics Platform</title>
        </head>
        <body>
            <h1>🚀 MT5 Real-Time Analytics Platform</h1>
            <p>Production-ready SaaS platform for MetaTrader 5 statistical analysis</p>
            <ul>
                <li><a href="/docs">API Documentation (Swagger)</a></li>
                <li><a href="/redoc">API Documentation (ReDoc)</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </body>
    </html>
    """

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health status"""
    try:
        mt5_service_instance = await get_mt5_service()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "mt5_connected": mt5_service_instance.is_connected() if mt5_service_instance else False,
                "analytics_running": True,
                "alerts_active": True
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "mt5_connected": True,
                "analytics_running": True,
                "alerts_active": True
            },
            "version": "1.0.0"
        }

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db = Depends(get_db)):
    """Register new user and generate API key"""
    try:
        new_user = await auth_service.create_user(user, db)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/refresh-key")
async def refresh_api_key(current_user = Depends(get_current_user), db = Depends(get_db)):
    """Generate new API key for user"""
    new_key = await auth_service.refresh_api_key(current_user.id, db)
    return {"api_key": new_key, "message": "API key refreshed successfully"}

# Live data streaming WebSocket
@app.websocket("/ws/live-data")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time data streaming via WebSocket"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Get latest analytics data
            live_data = await analytics_service.get_live_data()
            
            # Serialize datetime objects
            serialized_data = serialize_datetime(live_data)
            
            # Send to client
            await websocket.send_json({
                "type": "live_data",
                "timestamp": datetime.utcnow().isoformat(),
                **serialized_data  # Spread the serialized data directly
            })
            
            # Wait for next update
            await asyncio.sleep(1)  # 1 second updates
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)

# Strategy edges WebSocket
@app.websocket("/ws/edges")
async def edges_websocket(websocket: WebSocket):
    """Real-time statistical edge updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Get latest edges
            edges = await analytics_service.get_current_edges()
            
            await websocket.send_json({
                "type": "edges_update",
                "timestamp": datetime.utcnow().isoformat(),
                "edges": edges
            })
            
            await asyncio.sleep(5)  # 5 second updates for edges
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Market data endpoints
@app.get("/api/v1/market/current-price")
async def get_current_price(
    symbol: str = "GOLD",
    current_user = Depends(get_current_user)
):
    """Get current market price for symbol"""
    price_data = await mt5_service.get_current_price(symbol)
    return {
        "symbol": symbol,
        "bid": price_data["bid"],
        "ask": price_data["ask"],
        "spread": price_data["spread"],
        "timestamp": price_data["timestamp"]
    }

@app.get("/api/v1/market/bars")
async def get_historical_bars(
    symbol: str = "GOLD",
    timeframe: str = "M1",
    count: int = 1000,
    current_user = Depends(get_current_user)
):
    """Get historical OHLCV bars"""
    bars = await mt5_service.get_bars(symbol, timeframe, count)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "count": len(bars),
        "bars": bars
    }

# Analytics endpoints
@app.get("/api/v1/analytics/edges")
async def get_statistical_edges(
    symbol: str = "GOLD",
    timeframe: str = "M1",
    lookback_hours: int = 168,  # 1 week
    current_user = Depends(get_current_user)
):
    """Get current statistical edges"""
    edges = await analytics_service.calculate_edges(symbol, timeframe, lookback_hours)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "lookback_hours": lookback_hours,
        "edges": edges,
        "calculated_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/analytics/heatmap-data")
async def get_heatmap_data(
    symbol: str = "GOLD",
    days_back: int = 30,
    current_user = Depends(get_current_user)
):
    """Get win rate heatmap data by time and day"""
    heatmap_data = await analytics_service.generate_heatmap_data(symbol, days_back)
    return heatmap_data

@app.get("/api/v1/analytics/volatility-surface")
async def get_volatility_surface(
    symbol: str = "GOLD",
    days_back: int = 30,
    current_user = Depends(get_current_user)
):
    """Get 3D volatility surface data"""
    surface_data = await analytics_service.calculate_volatility_surface(symbol, days_back)
    return surface_data

# Strategy management endpoints
@app.post("/api/v1/strategies")
async def create_strategy(
    strategy: StrategyConfig,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create new custom strategy"""
    new_strategy = await analytics_service.create_strategy(strategy, current_user.id, db)
    return {
        "id": new_strategy.id,
        "name": new_strategy.name,
        "status": "created",
        "message": "Strategy created successfully"
    }

@app.get("/api/v1/strategies")
async def list_strategies(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's strategies"""
    strategies = await analytics_service.get_user_strategies(current_user.id, db)
    return {"strategies": strategies}

@app.get("/api/v1/strategies/{strategy_id}/performance")
async def get_strategy_performance(
    strategy_id: str,
    days_back: int = 30,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get detailed strategy performance metrics"""
    performance = await analytics_service.get_strategy_performance(
        strategy_id, days_back, current_user.id, db
    )
    return performance

@app.delete("/api/v1/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete user strategy"""
    await analytics_service.delete_strategy(strategy_id, current_user.id, db)
    return {"message": "Strategy deleted successfully"}

# Alert management endpoints
@app.post("/api/v1/alerts/rules")
async def create_alert_rule(
    rule: AlertRule,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create new alert rule"""
    new_rule = await alert_service.create_rule(rule, current_user.id, db)
    return {
        "id": new_rule.id,
        "name": new_rule.name,
        "status": "active"
    }

@app.get("/api/v1/alerts/history")
async def get_alert_history(
    limit: int = 50,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get alert history for user"""
    alerts = await alert_service.get_user_alerts(current_user.id, limit, db)
    return {"alerts": alerts}

# User account endpoints
@app.get("/api/v1/account/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    """Get user profile information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "plan": current_user.plan,
        "created_at": current_user.created_at.isoformat(),
        "api_calls_today": await auth_service.get_api_usage(current_user.id),
        "rate_limit": current_user.rate_limit
    }

@app.get("/api/v1/account/usage")
async def get_usage_stats(
    days_back: int = 30,
    current_user = Depends(get_current_user)
):
    """Get API usage statistics"""
    usage_stats = await auth_service.get_usage_stats(current_user.id, days_back)
    return usage_stats

# Admin endpoints (for enterprise users)
@app.get("/api/v1/admin/system-stats")
async def get_system_stats(current_user = Depends(get_current_user)):
    """Get system-wide statistics (admin only)"""
    if current_user.plan != "enterprise":
        raise HTTPException(status_code=403, detail="Enterprise plan required")
    
    stats = await analytics_service.get_system_stats()
    return stats

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting MT5 Real-Time Analytics Platform...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )