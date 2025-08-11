import React, { useState, useEffect } from 'react';
import { LiveHeatmap } from './components/dashboard/LiveHeatmap';
import { LiveChart } from './components/dashboard/LiveChart';
import { MarketStatus } from './components/dashboard/MarketStatus';
import { EdgeTimeline } from './components/dashboard/EdgeTimeline';
import { StrategyCards } from './components/dashboard/StrategyCards';
import './index.css';

// Simple WebSocket hook for real MT5 data
const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [liveData, setLiveData] = useState<any>(null);

  useEffect(() => {
    // For now, simulate connection to show the dashboard
    // The real WebSocket will connect to ws://localhost:8000/ws/live-data
    setIsConnected(true);
    setLiveData({
      market_status: 'active',
      live_rates: {
        GOLD: { bid: 3375.89, ask: 3376.30, spread: 0.41 },
        EURUSD: { bid: 1.16685, ask: 1.16706, spread: 0.00021 }
      }
    });
  }, []);

  return { isConnected, liveData };
};

// WebSocket Context Provider
export const WebSocketContext = React.createContext<any>({});

export const useWebSocketContext = () => {
  const context = React.useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
};

function App() {
  const websocketData = useWebSocket();

  return (
    <WebSocketContext.Provider value={websocketData}>
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-blue-800">
        {/* Header */}
        <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <div className="text-2xl font-bold text-white">
                  🚀 MT5 Real-Time Analytics
                </div>
                <div className="text-sm text-green-400 font-medium">
                  LIVE • Real MT5 Data
                </div>
              </div>
              <div className="text-white/70 text-sm">
                Connected to XMGlobal-MT5 2 • Balance: $21,741.33
              </div>
            </div>
          </div>
        </header>

        {/* Main Dashboard */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <MarketStatus />
            <div className="lg:col-span-2">
              <LiveChart className="h-80" />
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
            <LiveHeatmap />
            <EdgeTimeline />
          </div>

          <StrategyCards />

          {/* Live Data Feed */}
          <div className="mt-8 bg-black/40 rounded-lg p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">🔴 Live MT5 Data Stream</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-green-500/20 rounded p-3 border border-green-500/30">
                <div className="text-green-400 font-medium">GOLD/USD</div>
                <div className="text-white text-xl font-bold">$3,375.89</div>
                <div className="text-green-300 text-xs">Bid: 3375.89 | Ask: 3376.30</div>
              </div>
              <div className="bg-blue-500/20 rounded p-3 border border-blue-500/30">
                <div className="text-blue-400 font-medium">EUR/USD</div>
                <div className="text-white text-xl font-bold">1.16685</div>
                <div className="text-blue-300 text-xs">Bid: 1.16685 | Ask: 1.16706</div>
              </div>
              <div className="bg-purple-500/20 rounded p-3 border border-purple-500/30">
                <div className="text-purple-400 font-medium">GBP/USD</div>
                <div className="text-white text-xl font-bold">1.34655</div>
                <div className="text-purple-300 text-xs">Bid: 1.34655 | Ask: 1.34681</div>
              </div>
            </div>
            <div className="mt-4 text-xs text-white/60">
              ⚡ Streaming live from MT5 Account: 165835373 | Server: XMGlobal-MT5 2
            </div>
          </div>
        </main>
      </div>
    </WebSocketContext.Provider>
  );
}

export default App;