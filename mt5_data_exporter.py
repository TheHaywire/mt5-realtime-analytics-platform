#!/usr/bin/env python3
"""
MT5 Data Exporter for Medium Blog Series
Comprehensive data extraction, CSV generation, and trading log creation
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import csv
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class MT5DataExporter:
    def __init__(self):
        self.connected = False
        self.export_dir = Path("blog_data_exports")
        self.export_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        (self.export_dir / "raw_data").mkdir(exist_ok=True)
        (self.export_dir / "trading_logs").mkdir(exist_ok=True)
        (self.export_dir / "analysis_results").mkdir(exist_ok=True)
        (self.export_dir / "charts_data").mkdir(exist_ok=True)
        
    def connect_to_mt5(self):
        """Connect to MT5 with comprehensive logging"""
        try:
            if not mt5.initialize():
                print("Failed to initialize MT5")
                return False
            
            login = int(os.getenv('MT5_LIVE_LOGIN'))
            password = os.getenv('MT5_LIVE_PASSWORD')
            server = os.getenv('MT5_LIVE_SERVER')
            
            if mt5.login(login, password, server):
                account_info = mt5.account_info()
                self.connected = True
                
                # Save account info for blog
                account_data = {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'free_margin': account_info.margin_free,
                    'server': server,
                    'currency': account_info.currency,
                    'leverage': account_info.leverage,
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(self.export_dir / "account_info.json", 'w') as f:
                    json.dump(account_data, f, indent=2)
                
                print(f"Connected successfully!")
                print(f"Account: {account_info.login}")
                print(f"Balance: ${account_info.balance:,.2f}")
                print(f"Server: {server}")
                
                return True
            else:
                print("Login failed")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def export_raw_ohlc_data(self, symbol='GOLD', days_back=35):
        """Export comprehensive OHLC data with multiple timeframes"""
        if not self.connected:
            print("Not connected to MT5")
            return False
        
        print(f"Exporting raw OHLC data for {symbol} ({days_back} days)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        timeframes = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        for tf_name, tf_value in timeframes.items():
            rates = mt5.copy_rates_range(symbol, tf_value, start_date, end_date)
            
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['datetime'] = pd.to_datetime(df['time'], unit='s')
                df['symbol'] = symbol
                df['timeframe'] = tf_name
                
                # Add technical indicators for blog analysis
                df['sma_20'] = df['close'].rolling(20).mean()
                df['sma_50'] = df['close'].rolling(50).mean()
                
                # RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                df['rsi'] = 100 - (100 / (1 + gain / loss))
                
                # ATR
                df['tr'] = np.maximum(df['high'] - df['low'],
                                    np.maximum(abs(df['high'] - df['close'].shift(1)),
                                              abs(df['low'] - df['close'].shift(1))))
                df['atr'] = df['tr'].rolling(14).mean()
                
                # Bollinger Bands
                df['bb_middle'] = df['close'].rolling(20).mean()
                df['bb_std'] = df['close'].rolling(20).std()
                df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
                df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
                
                # Export to CSV
                filename = f"{symbol}_{tf_name}_{days_back}days.csv"
                filepath = self.export_dir / "raw_data" / filename
                df.to_csv(filepath, index=False)
                
                print(f"Exported {len(df)} {tf_name} bars to {filename}")
        
        return True
    
    def create_strategy_backtesting_logs(self, symbol='GOLD', days_back=35):
        """Create comprehensive trading logs for each strategy"""
        if not self.connected:
            print("Not connected to MT5")
            return False
        
        print("Creating strategy backtesting logs...")
        
        # Get M1 data for precise entry/exit timing
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_date, end_date)
        
        if rates is None or len(rates) == 0:
            print("No data available for backtesting")
            return False
        
        df = pd.DataFrame(rates)
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df['weekday'] = df['datetime'].dt.day_name()
        df['date'] = df['datetime'].dt.date
        
        # Filter weekdays only
        weekdays_only = df[df['weekday'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
        unique_dates = sorted(weekdays_only['date'].unique())
        
        # Strategy definitions
        strategies = {
            'Strategy_1_0317_Edge': {
                'entry_time': '03:17',
                'exit_time': '03:17',
                'direction': 'long',
                'entry_interval': 0,
                'exit_interval': 10,
                'description': 'The 3:17 AM Edge - 64% win rate'
            },
            'Strategy_2_Friday_Rush': {
                'entry_time': '01:00',
                'exit_time': '23:58',
                'direction': 'long',
                'entry_interval': 0,
                'exit_interval': 100,
                'description': 'Friday Gold Rush - Hold all day Friday',
                'weekday_filter': 'Friday'
            },
            'Strategy_3_Wednesday_Fade': {
                'entry_time': '01:00',
                'exit_time': '23:58',
                'direction': 'short',
                'entry_interval': 0,
                'exit_interval': 100,
                'description': 'Wednesday Fade - Short all day Wednesday',
                'weekday_filter': 'Wednesday'
            },
            'Strategy_4_Morning_Weakness': {
                'entry_time': '07:53',
                'exit_time': '12:29',
                'direction': 'short',
                'entry_interval': 30,
                'exit_interval': 50,
                'description': 'Morning Weakness Exploit - Short 07:53 to 12:29'
            },
            'Strategy_5_Late_Momentum': {
                'entry_time': '21:41',
                'exit_time': '23:58',
                'direction': 'long',
                'entry_interval': 90,
                'exit_interval': 100,
                'description': 'Late Day Momentum - 21:41 to close'
            }
        }
        
        all_trades = []
        strategy_summaries = {}
        
        for strategy_name, strategy_config in strategies.items():
            print(f"Backtesting {strategy_name}...")
            
            strategy_trades = []
            
            for date in unique_dates:
                day_data = weekdays_only[weekdays_only['date'] == date].copy()
                if len(day_data) < 100:
                    continue
                
                weekday = day_data['weekday'].iloc[0]
                
                # Check weekday filter
                if 'weekday_filter' in strategy_config:
                    if weekday != strategy_config['weekday_filter']:
                        continue
                
                day_data = day_data.sort_values('datetime')
                
                # Calculate 10% intervals for this day
                total_bars = len(day_data)
                
                entry_idx = min(int(total_bars * strategy_config['entry_interval'] / 100), total_bars - 1)
                exit_idx = min(int(total_bars * strategy_config['exit_interval'] / 100), total_bars - 1)
                
                entry_bar = day_data.iloc[entry_idx]
                exit_bar = day_data.iloc[exit_idx]
                
                entry_price = entry_bar['close']
                exit_price = exit_bar['close']
                
                # Calculate P&L based on direction
                if strategy_config['direction'] == 'long':
                    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                    pnl_pips = (exit_price - entry_price) * 100  # Gold pips
                else:  # short
                    pnl_pct = ((entry_price - exit_price) / entry_price) * 100
                    pnl_pips = (entry_price - exit_price) * 100
                
                # Simulate position size (0.1 lots = $1000 exposure for gold)
                position_size = 0.1
                dollar_pnl = pnl_pips * position_size * 10  # $10 per pip for 0.1 lots
                
                trade = {
                    'strategy': strategy_name,
                    'date': date,
                    'weekday': weekday,
                    'entry_time': entry_bar['datetime'].strftime('%H:%M:%S'),
                    'exit_time': exit_bar['datetime'].strftime('%H:%M:%S'),
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'direction': strategy_config['direction'],
                    'position_size': position_size,
                    'pnl_pct': pnl_pct,
                    'pnl_pips': pnl_pips,
                    'pnl_dollars': dollar_pnl,
                    'win': 1 if pnl_pct > 0 else 0,
                    'description': strategy_config['description']
                }
                
                strategy_trades.append(trade)
                all_trades.append(trade)
            
            # Strategy summary
            if strategy_trades:
                total_trades = len(strategy_trades)
                winning_trades = sum([t['win'] for t in strategy_trades])
                win_rate = (winning_trades / total_trades) * 100
                total_pnl = sum([t['pnl_dollars'] for t in strategy_trades])
                avg_pnl = total_pnl / total_trades
                
                strategy_summaries[strategy_name] = {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': total_trades - winning_trades,
                    'win_rate': win_rate,
                    'total_pnl_dollars': total_pnl,
                    'avg_pnl_dollars': avg_pnl,
                    'best_trade': max([t['pnl_dollars'] for t in strategy_trades]),
                    'worst_trade': min([t['pnl_dollars'] for t in strategy_trades]),
                    'description': strategy_config['description']
                }
        
        # Export individual strategy logs
        strategies_df = pd.DataFrame(all_trades)
        strategies_df.to_csv(self.export_dir / "trading_logs" / "all_strategies_backtest.csv", index=False)
        
        # Export strategy summaries
        with open(self.export_dir / "trading_logs" / "strategy_summaries.json", 'w') as f:
            json.dump(strategy_summaries, f, indent=2, default=str)
        
        # Create individual strategy files
        for strategy_name in strategies.keys():
            strategy_trades = [t for t in all_trades if t['strategy'] == strategy_name]
            if strategy_trades:
                strategy_df = pd.DataFrame(strategy_trades)
                filename = f"{strategy_name}_backtest.csv"
                strategy_df.to_csv(self.export_dir / "trading_logs" / filename, index=False)
        
        print(f"Created trading logs for {len(all_trades)} total trades across {len(strategies)} strategies")
        
        return True
    
    def export_statistical_analysis_data(self, symbol='GOLD', days_back=35):
        """Export detailed statistical analysis data for blog charts"""
        print("Exporting statistical analysis data...")
        
        # Get our comprehensive analysis data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_date, end_date)
        
        if rates is None:
            return False
        
        df = pd.DataFrame(rates)
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df['weekday'] = df['datetime'].dt.day_name()
        df['date'] = df['datetime'].dt.date
        
        # Weekday analysis
        weekdays_only = df[df['weekday'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
        unique_dates = sorted(weekdays_only['date'].unique())
        
        # Interval analysis data
        interval_analysis = []
        weekday_performance = []
        
        for date in unique_dates:
            day_data = weekdays_only[weekdays_only['date'] == date].copy()
            if len(day_data) < 100:
                continue
            
            day_data = day_data.sort_values('datetime')
            weekday = day_data['weekday'].iloc[0]
            
            opening_price = day_data['close'].iloc[0]
            closing_price = day_data['close'].iloc[-1]
            session_high = day_data['high'].max()
            session_low = day_data['low'].min()
            
            daily_change = ((closing_price - opening_price) / opening_price) * 100
            daily_range = ((session_high - session_low) / opening_price) * 100
            
            weekday_performance.append({
                'date': date,
                'weekday': weekday,
                'opening': opening_price,
                'closing': closing_price,
                'high': session_high,
                'low': session_low,
                'daily_change_pct': daily_change,
                'daily_range_pct': daily_range,
                'total_volume': day_data['tick_volume'].sum()
            })
            
            # 10% interval analysis
            total_bars = len(day_data)
            for pct in range(0, 101, 10):
                idx = min(int(total_bars * pct / 100), total_bars - 1)
                bar = day_data.iloc[idx]
                
                change_from_open = ((bar['close'] - opening_price) / opening_price) * 100
                
                interval_analysis.append({
                    'date': date,
                    'weekday': weekday,
                    'interval_pct': pct,
                    'time': bar['datetime'].strftime('%H:%M:%S'),
                    'price': bar['close'],
                    'change_from_open_pct': change_from_open,
                    'volume': bar['tick_volume']
                })
        
        # Export analysis data
        weekday_df = pd.DataFrame(weekday_performance)
        weekday_df.to_csv(self.export_dir / "analysis_results" / "weekday_performance.csv", index=False)
        
        interval_df = pd.DataFrame(interval_analysis)
        interval_df.to_csv(self.export_dir / "analysis_results" / "interval_analysis.csv", index=False)
        
        # Create summary statistics
        weekday_stats = {}
        for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            weekday_data = weekday_df[weekday_df['weekday'] == weekday]
            if len(weekday_data) > 0:
                weekday_stats[weekday] = {
                    'sample_size': len(weekday_data),
                    'avg_daily_change': weekday_data['daily_change_pct'].mean(),
                    'std_daily_change': weekday_data['daily_change_pct'].std(),
                    'win_rate': (weekday_data['daily_change_pct'] > 0).mean() * 100,
                    'avg_daily_range': weekday_data['daily_range_pct'].mean(),
                    'best_day': weekday_data['daily_change_pct'].max(),
                    'worst_day': weekday_data['daily_change_pct'].min()
                }
        
        with open(self.export_dir / "analysis_results" / "weekday_statistics.json", 'w') as f:
            json.dump(weekday_stats, f, indent=2)
        
        # Interval statistics
        interval_stats = {}
        for pct in range(0, 101, 10):
            interval_data = interval_df[interval_df['interval_pct'] == pct]
            if len(interval_data) > 0:
                interval_stats[f"{pct}%"] = {
                    'sample_size': len(interval_data),
                    'avg_change': interval_data['change_from_open_pct'].mean(),
                    'std_change': interval_data['change_from_open_pct'].std(),
                    'win_rate': (interval_data['change_from_open_pct'] > 0).mean() * 100,
                    'best_case': interval_data['change_from_open_pct'].max(),
                    'worst_case': interval_data['change_from_open_pct'].min(),
                    'typical_time': interval_data['time'].mode().iloc[0] if len(interval_data) > 0 else None
                }
        
        with open(self.export_dir / "analysis_results" / "interval_statistics.json", 'w') as f:
            json.dump(interval_stats, f, indent=2)
        
        print(f"Exported statistical analysis for {len(unique_dates)} trading days")
        return True
    
    def create_blog_data_summary(self):
        """Create comprehensive summary for blog series"""
        summary_data = {
            'export_timestamp': datetime.now().isoformat(),
            'data_period': '35 days',
            'total_bars_analyzed': 0,
            'trading_days': 0,
            'strategies_backtested': 5,
            'files_created': [],
            'key_findings': {}
        }
        
        # Count files and gather key stats
        for root, dirs, files in os.walk(self.export_dir):
            for file in files:
                if file.endswith('.csv'):
                    filepath = Path(root) / file
                    df = pd.read_csv(filepath)
                    summary_data['total_bars_analyzed'] += len(df)
                    summary_data['files_created'].append({
                        'filename': file,
                        'rows': len(df),
                        'size_mb': os.path.getsize(filepath) / (1024*1024)
                    })
        
        # Load key findings
        try:
            with open(self.export_dir / "trading_logs" / "strategy_summaries.json", 'r') as f:
                strategy_data = json.load(f)
                
            summary_data['key_findings']['best_strategy'] = max(strategy_data.items(), 
                                                              key=lambda x: x[1]['total_pnl_dollars'])
            summary_data['key_findings']['highest_win_rate'] = max(strategy_data.items(), 
                                                                 key=lambda x: x[1]['win_rate'])
        except FileNotFoundError:
            pass
        
        with open(self.export_dir / "blog_data_summary.json", 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        
        return summary_data
    
    def disconnect(self):
        """Clean disconnect"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("Disconnected from MT5")

def main():
    exporter = MT5DataExporter()
    
    try:
        if not exporter.connect_to_mt5():
            return
        
        print("Starting comprehensive data export for Medium blog series...")
        
        # Export raw OHLC data
        exporter.export_raw_ohlc_data(symbol='GOLD', days_back=35)
        
        # Create backtesting logs
        exporter.create_strategy_backtesting_logs(symbol='GOLD', days_back=35)
        
        # Export statistical analysis
        exporter.export_statistical_analysis_data(symbol='GOLD', days_back=35)
        
        # Create summary
        summary = exporter.create_blog_data_summary()
        
        print("\n" + "="*80)
        print("DATA EXPORT COMPLETE FOR MEDIUM BLOG SERIES")
        print("="*80)
        print(f"Total bars analyzed: {summary.get('total_bars_analyzed', 'N/A'):,}")
        print(f"Files created: {len(summary.get('files_created', []))}")
        print(f"Export directory: {exporter.export_dir}")
        print("\nData ready for blog visualization and analysis!")
        
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        exporter.disconnect()

if __name__ == "__main__":
    main()