# Gold Trading Strategy Analysis Tools

This folder contains interactive tools and downloadable resources based on the Medium blog series:
"Data-Driven Gold Trading: Uncovering Statistical Edges in 2025"

## Files Included

### Excel Tools (.xlsx)
- **Gold_Strategy_Calculator.xlsx** - Interactive calculator for strategy performance analysis
- **Trading_Journal_Template.xlsx** - Professional trading journal template
- **Risk_Position_Calculator.xlsx** - Position sizing and risk management calculator
- **Complete_Strategy_Backtest.xlsx** - Detailed backtesting results for all 5 strategies

### Data Files (.csv)
- **Strategy_Performance_Summary.csv** - Summary statistics for all strategies
- **Weekday_Statistics.csv** - Performance analysis by weekday
- **Interval_Statistics.csv** - Win rates and performance by time intervals

## Strategy Overview

Based on analysis of 25 trading days and 85 actual trades:

### 1. 3:17 AM Edge (64% win rate)
- Enter long at market open (01:00), exit at 03:17
- Duration: 2 hours 17 minutes
- Best performing time-based strategy

### 2. Friday Rush (60% win rate) 
- Hold gold positions through entire Friday session
- Best performing weekday (+0.48% average daily change)

### 3. Wednesday Fade (60% win rate)
- Short gold on Wednesdays (worst performing day)
- Average daily change: -0.43%

### 4. Morning Weakness (56% win rate)
- Short gold from 07:53 to 12:29
- Duration: 4 hours 36 minutes

### 5. Late Momentum (52% win rate)
- Long gold from 21:41 to session close
- Duration: 2 hours 17 minutes

## Key Findings

- **Account Balance Analyzed**: $21,565.76
- **Total Bars Analyzed**: 46,040+
- **Sample Period**: 35 days (July-August 2025)
- **Best Strategy**: 3:17 AM Edge with 64% win rate
- **Most Profitable**: Friday Rush with highest average daily returns

## How to Use These Tools

1. **Strategy Calculator**: Input your account parameters to see expected returns
2. **Trading Journal**: Track your own trades using our proven format
3. **Risk Calculator**: Determine optimal position sizes for your account
4. **Backtest Data**: Analyze detailed trade-by-trade results

## Risk Disclaimer

- Past performance does not guarantee future results
- All trading involves risk of substantial loss
- Use proper position sizing and risk management
- Consider transaction costs and slippage in your calculations
- This is educational content, not financial advice

## Data Source

All data extracted from MetaTrader 5 platform using Python analysis scripts.
Analysis conducted on XMGlobal-MT5 server with real market data.

## Contact

For questions about these tools or the analysis methodology, please refer to the 
Medium blog series or GitHub repository linked in the articles.

---
Generated: 2025-08-11 02:01:35
Analysis Period: July-August 2025
Data Points: 46,040+ price bars analyzed
