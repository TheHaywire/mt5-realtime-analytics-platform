#!/usr/bin/env python3
"""
MT5 Real-Time Analytics Platform - One-Command Launcher
Starts the complete platform with all services
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path
import threading
import webbrowser
from datetime import datetime

# Platform configuration
PLATFORM_NAME = "MT5 Real-Time Analytics Platform"
VERSION = "1.0.0"
BACKEND_PORT = 8000
FRONTEND_PORT = 3000

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print(f" {PLATFORM_NAME}")
    print(f" Version {VERSION}")
    print("")
    print(" Production-ready SaaS platform for MT5 statistical analysis")
    print(" Real-time tick data * Live edge detection * Strategy monitor")
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are available"""
    print("[INFO] Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ required")
        return False
    
    # Check Docker availability
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("[OK] Docker available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN]  Docker not available - falling back to local development")
    
    # Check Node.js for frontend
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        print("[OK] Node.js and npm available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN]  Node.js not available - using Docker for frontend")
    
    return True

def setup_environment():
    """Set up environment variables and configuration"""
    print("[SETUP]  Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = f"""# MT5 Real-Time Analytics Platform Configuration
# Database
DATABASE_URL=sqlite:///./data/mt5_analytics.db

# Redis
REDIS_URL=redis://localhost:6379

# JWT Secret (change in production!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-{int(time.time())}

# MT5 Configuration
MT5_SYMBOLS=GOLD,EURUSD,GBPUSD
MT5_SERVER=Demo-Server
MT5_LOGIN=12345
MT5_PASSWORD=your-mt5-password

# Alert Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-email-password

# API Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production settings
ENVIRONMENT=development
DEBUG=true
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("[OK] Created .env configuration file")
    
    # Create necessary directories
    directories = ['data', 'logs', 'config']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("[OK] Created necessary directories")

def start_with_docker():
    """Start platform using Docker Compose"""
    print("🐳 Starting platform with Docker...")
    
    try:
        # Build and start services
        subprocess.run([
            "docker-compose", "up", "--build", "-d"
        ], check=True)
        
        print("[OK] Platform started with Docker")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Docker startup failed: {e}")
        return False

def start_local_development():
    """Start platform in local development mode"""
    print("[DEV] Starting platform in local development mode...")
    
    processes = []
    
    try:
        # Start backend
        print("🔧 Starting FastAPI backend...")
        backend_env = os.environ.copy()
        backend_env['PYTHONPATH'] = str(Path('backend').absolute())
        
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", str(BACKEND_PORT),
            "--reload"
        ], cwd="backend", env=backend_env)
        processes.append(("Backend", backend_process))
        
        # Wait for backend to start
        time.sleep(5)
        
        # Start frontend
        print("🎨 Starting React frontend...")
        
        # Check if node_modules exists
        if not Path("frontend/node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd="frontend", check=True)
        
        frontend_process = subprocess.Popen([
            "npm", "start"
        ], cwd="frontend")
        processes.append(("Frontend", frontend_process))
        
        print("[OK] Platform started in development mode")
        return processes
        
    except Exception as e:
        print(f"[ERROR] Local startup failed: {e}")
        # Cleanup processes
        for name, process in processes:
            process.terminate()
        return []

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to be ready...")
    
    import requests
    
    # Wait for backend
    backend_ready = False
    for i in range(30):
        try:
            response = requests.get(f"http://localhost:{BACKEND_PORT}/health", timeout=5)
            if response.status_code == 200:
                backend_ready = True
                break
        except:
            pass
        time.sleep(2)
        print(f"   Backend check {i+1}/30...")
    
    if backend_ready:
        print("[OK] Backend is ready")
    else:
        print("[WARN]  Backend startup timeout")
    
    # Wait for frontend
    frontend_ready = False
    for i in range(15):
        try:
            response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=5)
            if response.status_code == 200:
                frontend_ready = True
                break
        except:
            pass
        time.sleep(2)
        print(f"   Frontend check {i+1}/15...")
    
    if frontend_ready:
        print("[OK] Frontend is ready")
    else:
        print("[WARN]  Frontend startup timeout")
    
    return backend_ready and frontend_ready

def show_access_info():
    """Show how to access the platform"""
    access_info = f"""
🌟 Platform is ready! Access your analytics dashboard:

DASHBOARD: DASHBOARD: http://localhost:{FRONTEND_PORT}
🔧 API DOCS:  http://localhost:{BACKEND_PORT}/docs
API: API:       http://localhost:{BACKEND_PORT}

🔑 Default Login:
   Email: admin@mt5analytics.com
   Password: admin123

📋 Features Available:
   [OK] Real-time MT5 data streaming
   [OK] Statistical edge detection  
   [OK] Live heatmaps and visualizations
   [OK] Strategy performance monitoring
   [OK] WebSocket live updates
   [OK] Professional API with authentication

🛠️  Development:
   • Backend logs: tail -f logs/backend.log
   • Frontend logs: check browser console
   • Database: SQLite at data/mt5_analytics.db
   • Redis: redis-cli (if running locally)

[WARN]  First-time setup:
   1. Configure MT5 credentials in .env file
   2. Set up Telegram/email alerts (optional)
   3. Create user account via API or use default admin

💰 SaaS Ready:
   • Multi-tenant architecture
   • API key authentication  
   • Usage tracking and rate limiting
   • Subscription plans (free/pro/enterprise)

[READY] Ready for production deployment!
"""
    print(access_info)

def main():
    """Main entry point"""
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    setup_environment()
    
    # Choose deployment method
    use_docker = True
    
    # Check if docker-compose is available
    try:
        subprocess.run(["docker-compose", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN]  Docker Compose not available, using local development")
        use_docker = False
    
    processes = []
    
    try:
        if use_docker:
            if start_with_docker():
                if wait_for_services():
                    show_access_info()
                    
                    # Open browser automatically
                    try:
                        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
                    except:
                        pass
                    
                    print("\\nPress Ctrl+C to stop the platform...")
                    
                    # Keep running until interrupted
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\\n🛑 Stopping platform...")
                        subprocess.run(["docker-compose", "down"])
                        print("[OK] Platform stopped")
            else:
                print("[ERROR] Failed to start with Docker")
                sys.exit(1)
        else:
            processes = start_local_development()
            if processes:
                if wait_for_services():
                    show_access_info()
                    
                    # Open browser automatically
                    try:
                        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
                    except:
                        pass
                    
                    print("\\nPress Ctrl+C to stop the platform...")
                    
                    # Keep running until interrupted
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\\n🛑 Stopping platform...")
                        for name, process in processes:
                            process.terminate()
                            print(f"[OK] {name} stopped")
            else:
                print("[ERROR] Failed to start in local mode")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\\n🛑 Shutdown requested...")
        if use_docker:
            subprocess.run(["docker-compose", "down"])
        else:
            for name, process in processes:
                process.terminate()
        print("[OK] Platform shutdown complete")

if __name__ == "__main__":
    main()