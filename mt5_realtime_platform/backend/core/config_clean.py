#!/usr/bin/env python3
"""
Configuration settings for MT5 Real-Time Analytics Platform
"""

import os

class Settings:
    """Application settings"""
    
    def __init__(self):
        # JWT Configuration
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
        self.ALGORITHM = 'HS256'
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Database
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/mt5_analytics.db')
        
        # MT5 Configuration
        self.MT5_LIVE_LOGIN = os.getenv('MT5_LIVE_LOGIN', '165835373')
        self.MT5_LIVE_PASSWORD = os.getenv('MT5_LIVE_PASSWORD', 'Manan@123!!')
        self.MT5_LIVE_SERVER = os.getenv('MT5_LIVE_SERVER', 'XMGlobal-MT5 2')
        self.MT5_SYMBOLS = os.getenv('MT5_SYMBOLS', 'XAUUSD,GOLD,EURUSD,GBPUSD').split(',')
        
        # API Configuration
        self.API_HOST = os.getenv('API_HOST', '0.0.0.0')
        self.API_PORT = int(os.getenv('API_PORT', '8000'))
        
        # CORS
        self.ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')
        
        # Environment
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# Global settings instance
settings = Settings()