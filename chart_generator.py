#!/usr/bin/env python3
"""
Comprehensive Chart Generator for Medium Blog Series
Creates professional trading visualizations using matplotlib, plotly, and seaborn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from pathlib import Path
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Try to import mplfinance for candlestick charts
try:
    import mplfinance as mpf
    HAS_MPLFINANCE = True
except ImportError:
    print("mplfinance not available. Install with: pip install mplfinance")
    HAS_MPLFINANCE = False

class TradingChartGenerator:
    def __init__(self, data_dir="blog_data_exports"):
        self.data_dir = Path(data_dir)
        self.charts_dir = self.data_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)
        
        # Set style preferences
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
        
        # Color schemes for consistency
        self.colors = {
            'bullish': '#2ECC71',
            'bearish': '#E74C3C',
            'neutral': '#95A5A6',
            'accent': '#3498DB',
            'warning': '#F39C12',
            'background': '#FFFFFF'
        }
    
    def load_data(self):
        """Load all exported data for visualization"""
        try:
            # Load main datasets
            self.weekday_performance = pd.read_csv(self.data_dir / "analysis_results" / "weekday_performance.csv")
            self.interval_analysis = pd.read_csv(self.data_dir / "analysis_results" / "interval_analysis.csv")
            self.all_strategies = pd.read_csv(self.data_dir / "trading_logs" / "all_strategies_backtest.csv")
            
            # Load statistics
            with open(self.data_dir / "analysis_results" / "weekday_statistics.json", 'r') as f:
                self.weekday_stats = json.load(f)
            
            with open(self.data_dir / "analysis_results" / "interval_statistics.json", 'r') as f:
                self.interval_stats = json.load(f)
                
            with open(self.data_dir / "trading_logs" / "strategy_summaries.json", 'r') as f:
                self.strategy_summaries = json.load(f)
            
            # Load raw OHLC data (M1 for detailed charts)
            raw_data_files = list((self.data_dir / "raw_data").glob("GOLD_M1_*.csv"))
            if raw_data_files:
                self.ohlc_data = pd.read_csv(raw_data_files[0])
                self.ohlc_data['datetime'] = pd.to_datetime(self.ohlc_data['datetime'])
            
            print("All data loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_weekday_performance_chart(self):
        """Create comprehensive weekday performance visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Gold Weekday Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Average daily change by weekday
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        avg_changes = [self.weekday_stats[day]['avg_daily_change'] for day in weekdays]
        colors = [self.colors['bullish'] if x > 0 else self.colors['bearish'] for x in avg_changes]
        
        bars1 = ax1.bar(weekdays, avg_changes, color=colors, alpha=0.7)
        ax1.set_title('Average Daily Change by Weekday')
        ax1.set_ylabel('Average Change (%)')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars1, avg_changes):
            height = bar.get_height()
            ax1.annotate(f'{value:.2f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -15),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        fontweight='bold')
        
        # 2. Win rate by weekday
        win_rates = [self.weekday_stats[day]['win_rate'] for day in weekdays]
        bars2 = ax2.bar(weekdays, win_rates, color=self.colors['accent'], alpha=0.7)
        ax2.set_title('Win Rate by Weekday')
        ax2.set_ylabel('Win Rate (%)')
        ax2.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Breakeven')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        for bar, value in zip(bars2, win_rates):
            height = bar.get_height()
            ax2.annotate(f'{value:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        # 3. Average daily range by weekday
        avg_ranges = [self.weekday_stats[day]['avg_daily_range'] for day in weekdays]
        bars3 = ax3.bar(weekdays, avg_ranges, color=self.colors['warning'], alpha=0.7)
        ax3.set_title('Average Daily Range by Weekday')
        ax3.set_ylabel('Average Range (%)')
        ax3.grid(True, alpha=0.3)
        
        for bar, value in zip(bars3, avg_ranges):
            height = bar.get_height()
            ax3.annotate(f'{value:.2f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        # 4. Best vs Worst day for each weekday
        best_days = [self.weekday_stats[day]['best_day'] for day in weekdays]
        worst_days = [self.weekday_stats[day]['worst_day'] for day in weekdays]
        
        x = np.arange(len(weekdays))
        width = 0.35
        
        ax4.bar(x - width/2, best_days, width, label='Best Day', color=self.colors['bullish'], alpha=0.7)
        ax4.bar(x + width/2, worst_days, width, label='Worst Day', color=self.colors['bearish'], alpha=0.7)
        
        ax4.set_title('Best vs Worst Day Performance')
        ax4.set_ylabel('Daily Change (%)')
        ax4.set_xticks(x)
        ax4.set_xticklabels(weekdays)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / "weekday_performance_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Created weekday performance chart")
    
    def create_interval_heatmap(self):
        """Create heatmap showing win rates by time interval and weekday"""
        # Prepare data for heatmap
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        intervals = list(range(0, 101, 10))
        
        heatmap_data = []
        
        for weekday in weekdays:
            weekday_data = self.interval_analysis[self.interval_analysis['weekday'] == weekday]
            row = []
            
            for interval in intervals:
                interval_data = weekday_data[weekday_data['interval_pct'] == interval]
                if len(interval_data) > 0:
                    win_rate = (interval_data['change_from_open_pct'] > 0).mean() * 100
                    row.append(win_rate)
                else:
                    row.append(np.nan)
            
            heatmap_data.append(row)
        
        heatmap_df = pd.DataFrame(heatmap_data, 
                                 index=weekdays, 
                                 columns=[f"{i}%" for i in intervals])
        
        # Create the heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.heatmap(heatmap_df, 
                   annot=True, 
                   fmt='.1f', 
                   cmap='RdYlGn', 
                   center=50,
                   cbar_kws={'label': 'Win Rate (%)'},
                   linewidths=0.5,
                   ax=ax)
        
        ax.set_title('Win Rate Heatmap: Time Intervals vs Weekdays', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Time Through Trading Day', fontsize=12)
        ax.set_ylabel('Weekday', fontsize=12)
        
        # Add annotations for high-probability setups
        for i, weekday in enumerate(weekdays):
            for j, interval in enumerate(intervals):
                value = heatmap_df.iloc[i, j]
                if not np.isnan(value):
                    if value >= 75:
                        ax.add_patch(Rectangle((j, i), 1, 1, fill=False, edgecolor='blue', lw=3))
                        ax.text(j + 0.5, i + 0.7, '🎯', ha='center', va='center', fontsize=8)
                    elif value <= 25:
                        ax.add_patch(Rectangle((j, i), 1, 1, fill=False, edgecolor='red', lw=3))
                        ax.text(j + 0.5, i + 0.7, '⚠️', ha='center', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / "interval_winrate_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Created interval win rate heatmap")
    
    def create_strategy_performance_dashboard(self):
        """Create comprehensive strategy performance dashboard"""
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Strategy names for display
        strategy_names = {
            'Strategy_1_0317_Edge': '3:17 AM Edge',
            'Strategy_2_Friday_Rush': 'Friday Rush',
            'Strategy_3_Wednesday_Fade': 'Wednesday Fade',
            'Strategy_4_Morning_Weakness': 'Morning Weakness',
            'Strategy_5_Late_Momentum': 'Late Momentum'
        }
        
        strategies = list(self.strategy_summaries.keys())
        
        # 1. Win Rate Comparison
        ax1 = fig.add_subplot(gs[0, :2])
        win_rates = [self.strategy_summaries[s]['win_rate'] for s in strategies]
        display_names = [strategy_names.get(s, s) for s in strategies]
        colors = [self.colors['bullish'] if wr > 50 else self.colors['bearish'] for wr in win_rates]
        
        bars = ax1.bar(display_names, win_rates, color=colors, alpha=0.7)
        ax1.set_title('Strategy Win Rates', fontweight='bold')
        ax1.set_ylabel('Win Rate (%)')
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Breakeven')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        for bar, value in zip(bars, win_rates):
            height = bar.get_height()
            ax1.annotate(f'{value:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        # 2. Total P&L Comparison
        ax2 = fig.add_subplot(gs[0, 2:])
        total_pnls = [self.strategy_summaries[s]['total_pnl_dollars'] for s in strategies]
        colors_pnl = [self.colors['bullish'] if pnl > 0 else self.colors['bearish'] for pnl in total_pnls]
        
        bars2 = ax2.bar(display_names, total_pnls, color=colors_pnl, alpha=0.7)
        ax2.set_title('Strategy Total P&L', fontweight='bold')
        ax2.set_ylabel('P&L ($)')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.grid(True, alpha=0.3)
        
        for bar, value in zip(bars2, total_pnls):
            height = bar.get_height()
            ax2.annotate(f'${value:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -15),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        fontweight='bold')
        
        # 3. Risk-Reward Analysis
        ax3 = fig.add_subplot(gs[1, :2])
        avg_wins = [self.strategy_summaries[s].get('best_trade', 0) for s in strategies]
        avg_losses = [abs(self.strategy_summaries[s].get('worst_trade', 0)) for s in strategies]
        
        x = np.arange(len(strategies))
        width = 0.35
        
        ax3.bar(x - width/2, avg_wins, width, label='Best Trade', color=self.colors['bullish'], alpha=0.7)
        ax3.bar(x + width/2, [-loss for loss in avg_losses], width, label='Worst Trade', color=self.colors['bearish'], alpha=0.7)
        
        ax3.set_title('Best vs Worst Trade by Strategy', fontweight='bold')
        ax3.set_ylabel('Trade P&L ($)')
        ax3.set_xticks(x)
        ax3.set_xticklabels([strategy_names.get(s, s) for s in strategies], rotation=45)
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Trade Count Distribution
        ax4 = fig.add_subplot(gs[1, 2:])
        trade_counts = [self.strategy_summaries[s]['total_trades'] for s in strategies]
        
        bars4 = ax4.bar(display_names, trade_counts, color=self.colors['accent'], alpha=0.7)
        ax4.set_title('Number of Trades per Strategy', fontweight='bold')
        ax4.set_ylabel('Trade Count')
        ax4.grid(True, alpha=0.3)
        
        for bar, value in zip(bars4, trade_counts):
            height = bar.get_height()
            ax4.annotate(f'{value}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        # 5. Strategy Performance Summary Table
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('tight')
        ax5.axis('off')
        
        # Create summary table
        table_data = []
        headers = ['Strategy', 'Trades', 'Win Rate', 'Total P&L', 'Avg P&L', 'Best Trade', 'Worst Trade']
        
        for strategy in strategies:
            s = self.strategy_summaries[strategy]
            table_data.append([
                strategy_names.get(strategy, strategy),
                f"{s['total_trades']}",
                f"{s['win_rate']:.1f}%",
                f"${s['total_pnl_dollars']:.0f}",
                f"${s['avg_pnl_dollars']:.0f}",
                f"${s['best_trade']:.0f}",
                f"${s['worst_trade']:.0f}"
            ])
        
        table = ax5.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 2)
        
        # Color code the table
        for i in range(len(table_data)):
            # Win rate cell
            win_rate = float(table_data[i][2].replace('%', ''))
            if win_rate > 60:
                table[(i+1, 2)].set_facecolor('#d5f4e6')
            elif win_rate < 40:
                table[(i+1, 2)].set_facecolor('#ffeaa7')
            
            # P&L cell
            pnl = float(table_data[i][3].replace('$', ''))
            if pnl > 0:
                table[(i+1, 3)].set_facecolor('#d5f4e6')
            else:
                table[(i+1, 3)].set_facecolor('#fab1a0')
        
        plt.suptitle('Strategy Performance Dashboard', fontsize=16, fontweight='bold', y=0.95)
        plt.savefig(self.charts_dir / "strategy_performance_dashboard.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Created strategy performance dashboard")
    
    def create_interactive_candlestick_chart(self, days_to_show=7):
        """Create interactive candlestick chart with strategy markers"""
        if not hasattr(self, 'ohlc_data'):
            print("OHLC data not available for candlestick chart")
            return
        
        # Get recent data
        recent_data = self.ohlc_data.tail(days_to_show * 1440)  # Approximate minutes per day
        
        # Resample to 15-minute bars for cleaner chart
        recent_data.set_index('datetime', inplace=True)
        ohlc_15m = recent_data.resample('15T').agg({
            'open': 'first',
            'high': 'max', 
            'low': 'min',
            'close': 'last',
            'tick_volume': 'sum'
        }).dropna()
        
        # Create plotly candlestick chart
        fig = go.Figure()
        
        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=ohlc_15m.index,
            open=ohlc_15m['open'],
            high=ohlc_15m['high'],
            low=ohlc_15m['low'],
            close=ohlc_15m['close'],
            name='GOLD',
            increasing_line_color=self.colors['bullish'],
            decreasing_line_color=self.colors['bearish']
        ))
        
        # Add moving averages
        ohlc_15m['sma_20'] = ohlc_15m['close'].rolling(20).mean()
        ohlc_15m['sma_50'] = ohlc_15m['close'].rolling(50).mean()
        
        fig.add_trace(go.Scatter(
            x=ohlc_15m.index,
            y=ohlc_15m['sma_20'],
            name='SMA 20',
            line=dict(color='orange', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=ohlc_15m.index,
            y=ohlc_15m['sma_50'],
            name='SMA 50',
            line=dict(color='blue', width=1)
        ))
        
        # Add strategy markers
        strategy_trades = self.all_strategies.copy()
        strategy_trades['datetime'] = pd.to_datetime(strategy_trades['date'].astype(str) + ' ' + strategy_trades['entry_time'])
        
        # Filter for recent trades
        recent_trades = strategy_trades[
            strategy_trades['datetime'] >= ohlc_15m.index.min()
        ]
        
        for _, trade in recent_trades.iterrows():
            color = self.colors['bullish'] if trade['direction'] == 'long' else self.colors['bearish']
            symbol = '▲' if trade['direction'] == 'long' else '▼'
            
            fig.add_trace(go.Scatter(
                x=[trade['datetime']],
                y=[trade['entry_price']],
                mode='markers+text',
                text=[symbol],
                textposition='top center' if trade['direction'] == 'long' else 'bottom center',
                marker=dict(
                    size=15,
                    color=color,
                    symbol='circle'
                ),
                name=f"{trade['strategy']} Entry",
                showlegend=False,
                hovertemplate=f"<b>{trade['strategy']}</b><br>" +
                             f"Entry: ${trade['entry_price']:.2f}<br>" +
                             f"Direction: {trade['direction']}<br>" +
                             f"P&L: ${trade['pnl_dollars']:.2f}<extra></extra>"
            ))
        
        # Update layout
        fig.update_layout(
            title='Gold Price with Strategy Entry Points',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=600,
            showlegend=True
        )
        
        # Save as HTML
        fig.write_html(self.charts_dir / "interactive_candlestick_chart.html")
        print("Created interactive candlestick chart")
    
    def create_profit_curve_chart(self):
        """Create cumulative profit curves for each strategy"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for strategy_name in self.strategy_summaries.keys():
            strategy_trades = self.all_strategies[self.all_strategies['strategy'] == strategy_name].copy()
            strategy_trades = strategy_trades.sort_values('date')
            strategy_trades['cumulative_pnl'] = strategy_trades['pnl_dollars'].cumsum()
            
            display_name = {
                'Strategy_1_0317_Edge': '3:17 AM Edge',
                'Strategy_2_Friday_Rush': 'Friday Rush',
                'Strategy_3_Wednesday_Fade': 'Wednesday Fade',
                'Strategy_4_Morning_Weakness': 'Morning Weakness',
                'Strategy_5_Late_Momentum': 'Late Momentum'
            }.get(strategy_name, strategy_name)
            
            ax.plot(range(len(strategy_trades)), strategy_trades['cumulative_pnl'], 
                   marker='o', linewidth=2, label=display_name)
        
        ax.set_title('Cumulative P&L by Strategy', fontsize=14, fontweight='bold')
        ax.set_xlabel('Trade Number')
        ax.set_ylabel('Cumulative P&L ($)')
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / "profit_curves.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Created profit curve chart")
    
    def generate_all_charts(self):
        """Generate all charts for the blog series"""
        print("Starting comprehensive chart generation...")
        
        if not self.load_data():
            print("Failed to load data. Please run data export first.")
            return False
        
        # Create all charts
        self.create_weekday_performance_chart()
        self.create_interval_heatmap()
        self.create_strategy_performance_dashboard()
        self.create_interactive_candlestick_chart()
        self.create_profit_curve_chart()
        
        print(f"\nAll charts generated successfully!")
        print(f"Charts saved to: {self.charts_dir}")
        print(f"Generated files:")
        for chart_file in self.charts_dir.glob("*"):
            print(f"  - {chart_file.name}")
        
        return True

def main():
    generator = TradingChartGenerator()
    generator.generate_all_charts()

if __name__ == "__main__":
    main()