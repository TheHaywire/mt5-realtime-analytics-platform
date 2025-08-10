# Installation Guide 🛠️

This guide provides comprehensive instructions for setting up the Gold Trading Statistical Analysis system on your local machine.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (required for MetaTrader 5 Python API)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for data and tools
- **Internet**: Required for MT5 data connection (optional for offline analysis)

### Software Dependencies
- **MetaTrader 5** (optional, for live data): [Download here](https://www.metatrader5.com/en/download)
- **Git** (optional, for development): [Download here](https://git-scm.com/downloads)
- **Python Package Manager**: pip (included with Python 3.8+)

## 🚀 Quick Installation

### Method 1: Standard Installation
```bash
# Clone the repository
git clone https://github.com/TheHaywire/gold-trading-statistical-analysis.git
cd gold-trading-statistical-analysis

# Install Python dependencies
pip install -r requirements_blog.txt

# Verify installation
python -c "import pandas, numpy, matplotlib, seaborn, plotly, openpyxl; print('All packages installed successfully!')"
```

### Method 2: Virtual Environment (Recommended)
```bash
# Create and activate virtual environment
python -m venv trading_analysis_env
trading_analysis_env\Scripts\activate  # Windows
# source trading_analysis_env/bin/activate  # macOS/Linux

# Install dependencies in virtual environment
pip install -r requirements_blog.txt

# Verify installation
python -c "import MetaTrader5 as mt5; print('MT5 available:', mt5.version())"
```

## 📦 Dependencies Explained

### Core Analysis Libraries
```python
# Data processing and analysis
pandas>=1.5.0          # Data manipulation and analysis
numpy>=1.21.0           # Numerical computations
scipy>=1.7.0            # Statistical functions

# Visualization libraries  
matplotlib>=3.5.0       # Static plotting and charts
seaborn>=0.11.0         # Statistical data visualization
plotly>=5.0.0          # Interactive charts and dashboards

# Excel integration
openpyxl>=3.0.0        # Excel file generation and manipulation

# MetaTrader 5 integration (Windows only)
MetaTrader5>=5.0.45    # Live data connection and trading
```

### Optional Dependencies
```python
# Development and testing
pytest>=6.0.0          # Unit testing framework
jupyter>=1.0.0         # Notebook environment
black>=21.0.0          # Code formatting

# Web interface (future enhancement)
streamlit>=1.0.0       # Web app framework
dash>=2.0.0            # Interactive web applications
```

## ⚙️ Configuration Setup

### 1. Basic Configuration
Create a configuration file for your analysis preferences:

```python
# config/analysis_config.py
ANALYSIS_CONFIG = {
    'data_source': 'mt5',  # or 'csv' for offline analysis
    'symbol': 'GOLD',
    'timeframes': ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'],
    'analysis_period': 25,  # days
    'min_sample_size': 25,  # minimum trades for statistical significance
    'confidence_level': 0.95,
    'output_directory': 'blog_data_exports/'
}
```

### 2. MetaTrader 5 Setup (Optional)
For live data analysis, configure MT5 connection:

```python
# config/mt5_config.py
MT5_CONFIG = {
    'server': 'XMGlobal-MT5 2',  # Your broker's server
    'login': 12345678,           # Your account number
    'password': 'your_password', # Your account password
    'timeout': 60000,            # Connection timeout (ms)
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe'  # MT5 path
}
```

**⚠️ Security Note**: Never commit credentials to version control. Use environment variables:
```bash
# Set environment variables (Windows)
set MT5_LOGIN=12345678
set MT5_PASSWORD=your_password
set MT5_SERVER=XMGlobal-MT5 2
```

### 3. Directory Structure Setup
The installation automatically creates this directory structure:
```
gold-trading-statistical-analysis/
├── blog_data_exports/          # Analysis outputs
│   ├── raw_data/              # OHLC price data
│   ├── analysis_results/      # Statistical analysis
│   ├── trading_logs/          # Backtesting results  
│   ├── charts/               # Generated visualizations
│   └── downloadable_tools/    # Excel calculators
├── config/                    # Configuration files
├── docs/                      # Documentation
├── tests/                     # Unit tests
└── src/                       # Source code
```

## 🧪 Verification Tests

### Test 1: Python Environment
```python
# test_environment.py
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print(f"Python version: {sys.version}")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
print(f"Matplotlib version: {plt.matplotlib.__version__}")
print("✅ Environment setup successful!")
```

### Test 2: MetaTrader 5 Connection (Optional)
```python
# test_mt5_connection.py
import MetaTrader5 as mt5

# Test MT5 availability
if mt5.initialize():
    print("✅ MT5 connection successful!")
    print(f"MT5 version: {mt5.version()}")
    print(f"Terminal info: {mt5.terminal_info()}")
    mt5.shutdown()
else:
    print("❌ MT5 connection failed - using offline mode")
```

### Test 3: Data Processing Pipeline
```python
# test_analysis_pipeline.py
from mt5_data_exporter import MT5DataExporter
from chart_generator import ChartGenerator
from interactive_analysis_tools import InteractiveToolsCreator

# Test core functionality
print("Testing data export...")
exporter = MT5DataExporter()
print("✅ Data exporter initialized")

print("Testing chart generation...")
chart_gen = ChartGenerator()
print("✅ Chart generator initialized")

print("Testing tool creation...")
tool_creator = InteractiveToolsCreator()
print("✅ Tool creator initialized")

print("🎉 All systems operational!")
```

## 🔧 Troubleshooting

### Common Installation Issues

#### Issue 1: MetaTrader5 Package Not Found
```bash
# Solution: Install MT5 package specifically
pip install MetaTrader5==5.0.45

# Alternative: Skip MT5 for offline analysis
pip install -r requirements_blog.txt --ignore-installed MetaTrader5
```

#### Issue 2: Permission Errors
```bash
# Solution: Run as administrator or use virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements_blog.txt
```

#### Issue 3: Missing Visual C++ Redistributable
```
Error: Microsoft Visual C++ 14.0 is required
```
**Solution**: Download and install [Visual C++ Redistributable](https://visualstudio.microsoft.com/downloads/)

#### Issue 4: Matplotlib Backend Issues
```python
# Add to top of scripts if GUI issues occur
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

### Performance Optimization

#### For Large Datasets:
```python
# config/performance_config.py
PERFORMANCE_CONFIG = {
    'chunk_size': 10000,        # Process data in chunks
    'parallel_processing': True, # Use multiple CPU cores
    'memory_limit': '4GB',      # Set memory usage limit
    'cache_results': True       # Cache intermediate results
}
```

#### Memory Management:
```python
# Use these settings for large analysis
pd.set_option('display.precision', 4)
pd.set_option('display.float_format', '{:.4f}'.format)

# Enable garbage collection
import gc
gc.enable()
```

## 📊 Data Requirements

### For Live Analysis:
- Active MetaTrader 5 account with data access
- Internet connection for real-time data
- Gold (XAUUSD) symbol availability from broker

### For Offline Analysis:
- Pre-downloaded CSV files in `blog_data_exports/raw_data/`
- Minimum 25 days of OHLC data across multiple timeframes
- Properly formatted timestamp columns

### Data Format Requirements:
```csv
# Expected CSV format for offline analysis
timestamp,open,high,low,close,volume,spread
2025-01-15 00:00:00,2045.50,2046.20,2044.80,2045.90,150,1.5
2025-01-15 00:01:00,2045.90,2047.10,2045.70,2046.80,230,1.4
```

## 🎯 Next Steps

After successful installation:

1. **Run Basic Analysis**:
```bash
python mt5_data_exporter.py --symbol GOLD --days 25
```

2. **Generate Visualizations**:
```bash
python chart_generator.py --create-all-charts
```

3. **Create Analysis Tools**:
```bash
python interactive_analysis_tools.py --create-all-tools
```

4. **View Results**:
- Check `blog_data_exports/` folder for all outputs
- Open Excel files in `downloadable_tools/` subfolder
- View charts in `charts/` subfolder

## 📞 Support

If you encounter installation issues:

1. **Check Requirements**: Ensure Python 3.8+ and Windows OS
2. **Search Issues**: Look through [GitHub Issues](https://github.com/TheHaywire/gold-trading-statistical-analysis/issues)
3. **Create New Issue**: Include error messages and system details
4. **Join Discussions**: Participate in [GitHub Discussions](https://github.com/TheHaywire/gold-trading-statistical-analysis/discussions)

## 🔄 Updates

Keep your installation current:
```bash
# Pull latest changes
git pull origin master

# Update dependencies
pip install -r requirements_blog.txt --upgrade

# Check for new features
python -c "from src import __version__; print(f'Version: {__version__}')"
```

---

**Installation complete!** You're now ready to analyze gold trading patterns with professional-grade statistical tools. 🎉