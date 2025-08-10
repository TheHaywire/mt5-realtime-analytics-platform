# API Reference 📚

Complete documentation for all classes, methods, and functions in the Gold Trading Statistical Analysis system.

## 🏗️ Core Modules

### MT5DataExporter

**File**: `mt5_data_exporter.py`

**Purpose**: Extract and process real-time data from MetaTrader 5 platform.

#### Class Definition
```python
class MT5DataExporter:
    """
    Comprehensive data extraction system for MetaTrader 5 platform.
    Handles connection management, data export, and statistical processing.
    """
```

#### Constructor
```python
def __init__(self, data_dir="blog_data_exports"):
    """
    Initialize MT5 data exporter.
    
    Parameters:
    -----------
    data_dir : str, optional
        Directory to store exported data (default: "blog_data_exports")
    """
```

#### Methods

##### connect_mt5()
```python
def connect_mt5(self) -> bool:
    """
    Establish connection to MetaTrader 5 platform.
    
    Returns:
    --------
    bool
        True if connection successful, False otherwise
        
    Raises:
    -------
    ConnectionError
        If MT5 platform is not available or connection fails
        
    Example:
    --------
    >>> exporter = MT5DataExporter()
    >>> if exporter.connect_mt5():
    ...     print("Connected to MT5")
    """
```

##### export_raw_ohlc_data()
```python
def export_raw_ohlc_data(self, symbol='GOLD', days_back=35) -> dict:
    """
    Export OHLC data across multiple timeframes.
    
    Parameters:
    -----------
    symbol : str, optional
        Trading symbol to export (default: 'GOLD')
    days_back : int, optional
        Number of days to look back (default: 35)
        
    Returns:
    --------
    dict
        Dictionary with timeframe names as keys and file paths as values
        
    Example:
    --------
    >>> files = exporter.export_raw_ohlc_data('GOLD', 30)
    >>> print(files['M1'])  # Path to 1-minute data file
    """
```

##### analyze_weekday_patterns()
```python
def analyze_weekday_patterns(self, symbol='GOLD', days_back=25) -> dict:
    """
    Analyze trading patterns by weekday.
    
    Parameters:
    -----------
    symbol : str, optional
        Trading symbol to analyze
    days_back : int, optional
        Number of days for analysis
        
    Returns:
    --------
    dict
        Weekday statistics including win rates and average changes
        
    Statistical Metrics:
    -------------------
    - sample_size: Number of observations per weekday
    - avg_daily_change: Average percentage change
    - win_rate: Percentage of positive days
    - avg_daily_range: Average high-low range
    - best_day: Best single day performance
    - worst_day: Worst single day performance
    """
```

##### backtest_strategy()
```python
def backtest_strategy(self, strategy_name: str, entry_time: str, 
                     exit_time: str, direction: str = 'long') -> list:
    """
    Backtest a time-based trading strategy.
    
    Parameters:
    -----------
    strategy_name : str
        Name identifier for the strategy
    entry_time : str
        Entry time in HH:MM format (24-hour)
    exit_time : str
        Exit time in HH:MM format (24-hour)
    direction : str, optional
        Trade direction: 'long' or 'short' (default: 'long')
        
    Returns:
    --------
    list
        List of trade dictionaries containing:
        - date: Trade date
        - entry_time: Actual entry time
        - exit_time: Actual exit time
        - entry_price: Entry price level
        - exit_price: Exit price level
        - pnl_pct: Profit/loss percentage
        - pnl_dollars: Profit/loss in dollars
        - win: Boolean indicating winning trade
        
    Example:
    --------
    >>> trades = exporter.backtest_strategy(
    ...     "3AM Edge", "01:00", "03:17", "long"
    ... )
    >>> win_rate = sum(t['win'] for t in trades) / len(trades)
    """
```

---

### ChartGenerator

**File**: `chart_generator.py`

**Purpose**: Create professional-grade visualizations and charts.

#### Class Definition
```python
class ChartGenerator:
    """
    Professional visualization system for trading analysis.
    Creates static and interactive charts using matplotlib, seaborn, and plotly.
    """
```

#### Constructor
```python
def __init__(self, data_dir="blog_data_exports"):
    """
    Initialize chart generator with data directory.
    
    Parameters:
    -----------
    data_dir : str, optional
        Directory containing analysis data
    """
```

#### Methods

##### create_weekday_performance_chart()
```python
def create_weekday_performance_chart(self) -> str:
    """
    Create comprehensive weekday performance analysis chart.
    
    Returns:
    --------
    str
        Path to generated chart file
        
    Chart Components:
    ----------------
    - Win rate by weekday (bar chart)
    - Average daily change (line chart)
    - Daily range analysis (box plot)  
    - Statistical significance indicators
    - Professional styling and annotations
        
    Example:
    --------
    >>> generator = ChartGenerator()
    >>> chart_path = generator.create_weekday_performance_chart()
    >>> print(f"Chart saved to: {chart_path}")
    """
```

##### create_strategy_performance_dashboard()
```python
def create_strategy_performance_dashboard(self) -> str:
    """
    Create comprehensive strategy performance dashboard.
    
    Returns:
    --------
    str
        Path to generated dashboard image
        
    Dashboard Elements:
    ------------------
    - Strategy comparison table
    - Win rate visualization
    - Profit/loss distribution
    - Risk-adjusted returns
    - Performance metrics summary
    """
```

##### create_interactive_candlestick_chart()
```python
def create_interactive_candlestick_chart(self, symbol='GOLD', 
                                       timeframe='H1') -> str:
    """
    Create interactive candlestick chart with strategy markers.
    
    Parameters:
    -----------
    symbol : str, optional
        Trading symbol for chart
    timeframe : str, optional
        Chart timeframe ('M1', 'M5', 'H1', etc.)
        
    Returns:
    --------
    str
        Path to generated HTML file
        
    Interactive Features:
    --------------------
    - Zoom and pan functionality
    - Strategy entry/exit markers
    - Hover tooltips with OHLC data
    - Time-based highlighting
    - Volume overlay (if available)
    """
```

---

### InteractiveToolsCreator

**File**: `interactive_analysis_tools.py`

**Purpose**: Generate Excel-based calculators and analysis tools.

#### Class Definition
```python
class InteractiveToolsCreator:
    """
    Creates interactive Excel tools and downloadable resources.
    Generates professional calculators, templates, and analysis spreadsheets.
    """
```

#### Methods

##### create_strategy_calculator()
```python
def create_strategy_calculator(self) -> str:
    """
    Create interactive Excel strategy performance calculator.
    
    Returns:
    --------
    str
        Path to generated Excel file
        
    Calculator Features:
    -------------------
    - Input parameters section (account size, risk %)
    - Strategy selection dropdown
    - Automated performance calculations
    - Monte Carlo simulation results
    - Risk metrics (Sharpe ratio, max drawdown)
    - Position sizing recommendations
        
    Worksheets:
    ----------
    - Strategy Calculator: Main calculation engine
    - Historical Data: Performance statistics
    - Instructions: Usage guide and methodology
    """
```

##### create_trading_journal_template()
```python
def create_trading_journal_template(self) -> str:
    """
    Create professional trading journal template.
    
    Returns:
    --------
    str
        Path to generated journal template
        
    Template Features:
    -----------------
    - Trade logging columns (entry, exit, P&L)
    - Strategy classification system
    - Performance tracking formulas
    - Monthly summary calculations
    - Risk management metrics
    - Psychology and emotion tracking
    """
```

##### create_risk_calculator()
```python
def create_risk_calculator(self) -> str:
    """
    Create position sizing and risk management calculator.
    
    Returns:
    --------
    str
        Path to generated risk calculator
        
    Calculator Components:
    ---------------------
    - Account information inputs
    - Position sizing formulas
    - Risk scenario analysis
    - Margin requirement calculations
    - Portfolio risk allocation
    - Kelly criterion optimization
    """
```

---

## 🔢 Statistical Functions

### Utility Functions

#### calculate_win_rate()
```python
def calculate_win_rate(trades: list) -> float:
    """
    Calculate win rate from list of trades.
    
    Parameters:
    -----------
    trades : list
        List of trade dictionaries with 'win' boolean field
        
    Returns:
    --------
    float
        Win rate as percentage (0-100)
        
    Example:
    --------
    >>> trades = [{'win': True}, {'win': False}, {'win': True}]
    >>> win_rate = calculate_win_rate(trades)
    >>> print(f"Win rate: {win_rate:.1f}%")  # Output: 66.7%
    """
```

#### calculate_sharpe_ratio()
```python
def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio for return series.
    
    Parameters:
    -----------
    returns : list
        List of periodic returns
    risk_free_rate : float, optional
        Annual risk-free rate (default: 2%)
        
    Returns:
    --------
    float
        Annualized Sharpe ratio
        
    Formula:
    --------
    Sharpe = (Portfolio Return - Risk Free Rate) / Portfolio Volatility
    """
```

#### calculate_maximum_drawdown()
```python
def calculate_maximum_drawdown(equity_curve: list) -> dict:
    """
    Calculate maximum drawdown from equity curve.
    
    Parameters:
    -----------
    equity_curve : list
        List of cumulative portfolio values
        
    Returns:
    --------
    dict
        Dictionary containing:
        - max_drawdown: Maximum drawdown percentage
        - drawdown_duration: Duration in periods
        - peak_date: Date of equity peak
        - trough_date: Date of equity trough
    """
```

---

## 🎯 Configuration Classes

### AnalysisConfig
```python
class AnalysisConfig:
    """Configuration settings for statistical analysis."""
    
    # Data collection settings
    DEFAULT_SYMBOL = 'GOLD'
    DEFAULT_TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
    DEFAULT_ANALYSIS_PERIOD = 25  # days
    
    # Statistical settings  
    MIN_SAMPLE_SIZE = 25
    CONFIDENCE_LEVEL = 0.95
    SIGNIFICANCE_THRESHOLD = 0.05
    
    # Risk management
    DEFAULT_POSITION_SIZE = 0.1  # lots
    DEFAULT_RISK_PER_TRADE = 0.01  # 1%
    MAX_DAILY_RISK = 0.05  # 5%
    
    # File paths
    DATA_EXPORT_DIR = 'blog_data_exports'
    CHARTS_DIR = 'charts'
    TOOLS_DIR = 'downloadable_tools'
```

---

## 📊 Data Structures

### Trade Dictionary
```python
trade = {
    'date': '2025-01-15',           # Trade date (YYYY-MM-DD)
    'weekday': 'Monday',            # Day of week
    'strategy': 'Strategy_1_0317',  # Strategy identifier
    'entry_time': '01:00',          # Entry time (HH:MM)
    'exit_time': '03:17',           # Exit time (HH:MM)
    'entry_price': 2045.50,         # Entry price level
    'exit_price': 2046.75,          # Exit price level
    'direction': 'long',            # Trade direction
    'position_size': 0.1,           # Position size in lots
    'pnl_pct': 0.061,              # P&L percentage
    'pnl_dollars': 12.50,          # P&L in dollars
    'win': True,                   # Boolean win indicator
    'duration_minutes': 137,        # Trade duration
    'spread': 1.5,                 # Spread in pips
    'commission': 7.0              # Commission cost
}
```

### Strategy Statistics
```python
strategy_stats = {
    'strategy_name': '3:17 AM Edge',
    'total_trades': 25,
    'winning_trades': 16,
    'losing_trades': 9,
    'win_rate': 64.0,              # Percentage
    'total_pnl_dollars': 287.50,
    'avg_pnl_dollars': 11.50,
    'best_trade': 31.25,
    'worst_trade': -22.75,
    'sharpe_ratio': 1.45,
    'max_drawdown': -8.3,          # Percentage
    'profit_factor': 2.1,
    'avg_trade_duration': 137      # Minutes
}
```

---

## 🔧 Error Handling

### Custom Exceptions
```python
class MT5ConnectionError(Exception):
    """Raised when MetaTrader 5 connection fails."""
    pass

class InsufficientDataError(Exception):
    """Raised when insufficient data for statistical analysis."""
    pass

class InvalidTimeframeError(Exception):
    """Raised when invalid timeframe specified."""
    pass
```

### Error Handling Example
```python
try:
    exporter = MT5DataExporter()
    exporter.connect_mt5()
    data = exporter.export_raw_ohlc_data('GOLD', 30)
except MT5ConnectionError:
    print("MT5 connection failed - using offline mode")
    data = load_offline_data()
except InsufficientDataError as e:
    print(f"Not enough data: {e}")
    sys.exit(1)
```

---

## 🎨 Styling and Formatting

### Chart Style Configuration
```python
CHART_STYLE = {
    'figure_size': (16, 12),
    'dpi': 300,
    'color_palette': ['#2E8B57', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
    'font_family': 'Arial',
    'title_fontsize': 16,
    'label_fontsize': 12,
    'tick_fontsize': 10,
    'legend_fontsize': 11
}
```

### Excel Style Configuration
```python
EXCEL_STYLES = {
    'header_fill': PatternFill(start_color="4F81BD", end_color="4F81BD"),
    'header_font': Font(color="FFFFFF", bold=True),
    'win_fill': PatternFill(start_color="C6EFCE", end_color="C6EFCE"),
    'loss_fill': PatternFill(start_color="FFC7CE", end_color="FFC7CE"),
    'border': Border(left=Side(style='thin'), right=Side(style='thin'))
}
```

---

## 📈 Performance Optimization

### Recommended Usage Patterns

#### For Large Datasets:
```python
# Use chunked processing for memory efficiency
def process_large_dataset(data, chunk_size=10000):
    for chunk in pd.read_csv(data, chunksize=chunk_size):
        yield process_chunk(chunk)
```

#### For Parallel Processing:
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_analysis(symbols):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(analyze_symbol, symbols)
    return list(results)
```

---

## 🔍 Testing

### Unit Test Examples
```python
import unittest
from mt5_data_exporter import MT5DataExporter

class TestMT5DataExporter(unittest.TestCase):
    
    def setUp(self):
        self.exporter = MT5DataExporter()
    
    def test_calculate_win_rate(self):
        trades = [{'win': True}, {'win': False}, {'win': True}]
        win_rate = calculate_win_rate(trades)
        self.assertAlmostEqual(win_rate, 66.67, places=2)
    
    def test_backtest_strategy_validation(self):
        with self.assertRaises(InvalidTimeframeError):
            self.exporter.backtest_strategy("Test", "25:00", "26:00")
```

---

## 📞 Support

For API-related questions:
- **Documentation Issues**: [GitHub Issues](https://github.com/TheHaywire/gold-trading-statistical-analysis/issues)
- **Implementation Help**: [GitHub Discussions](https://github.com/TheHaywire/gold-trading-statistical-analysis/discussions)
- **Feature Requests**: Use the feature request template

---

*This API reference is automatically generated from code docstrings. For the most up-to-date information, refer to the source code documentation.*