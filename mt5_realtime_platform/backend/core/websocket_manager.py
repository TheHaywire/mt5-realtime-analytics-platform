#!/usr/bin/env python3
"""
WebSocket Manager for real-time data streaming
Manages WebSocket connections and broadcasts REAL MT5 data
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            'connected_at': datetime.utcnow(),
            'message_count': 0
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
            self.connection_data[websocket]['message_count'] += 1
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            await self.disconnect(websocket)
            
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSockets"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message, default=str)
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_str)
                self.connection_data[websocket]['message_count'] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(websocket)
                
        # Clean up disconnected sockets
        for websocket in disconnected:
            await self.disconnect(websocket)
            
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
        
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_messages = sum(data['message_count'] for data in self.connection_data.values())
        return {
            'active_connections': len(self.active_connections),
            'total_messages_sent': total_messages,
            'connections_data': [
                {
                    'connected_at': data['connected_at'].isoformat(),
                    'message_count': data['message_count']
                }
                for data in self.connection_data.values()
            ]
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()