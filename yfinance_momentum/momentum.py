"""
Momentum-Based Paper Trading Algorithm using yfinance

This algorithm implements a momentum strategy that:
1. Calculates momentum scores for a universe of stocks
2. Ranks stocks by momentum
3. Simulates long/short positions
4. Rebalances periodically
5. Tracks portfolio value in positions.txt
6. Handles weekends and market holidays
7. Saves state for restarts

Requirements:
pip install yfinance pandas numpy pandas-market-calendars
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MomentumTradingStrategy:
    """
    Momentum trading strategy that ranks stocks by their recent performance
    and takes simulated long/short positions.
    """
    
    def __init__(self, initial_capital=100000):
        """
        Initialize the trading strategy.
        
        Args:
            initial_capital: Starting capital for paper trading
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {symbol: {'qty': int, 'entry_price': float, 'side': 'long'/'short'}}
        
        # Strategy parameters
        self.lookback_period = 20  # Days to calculate momentum
        self.rebalance_period = 5   # Days between rebalancing
        self.num_long = 5          # Number of long positions
        self.num_short = 5         # Number of short positions
        self.position_size = 0.15  # 15% of portfolio per position
        
        # Stock universe (S&P 100 subset for demonstration)
        self.universe = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
            'PEP', 'KO', 'AVGO', 'COST', 'WMT', 'MCD', 'CSCO', 'ACN', 'TMO',
            'DIS', 'ABT', 'VZ', 'ADBE', 'NFLX', 'NKE', 'CRM', 'INTC', 'AMD',
            'QCOM', 'TXN', 'ORCL', 'IBM', 'BA', 'GE', 'CAT', 'HON'
        ]
        
        self.last_rebalance = None
        self.positions_file = 'positions.txt'
        self.state_file = 'trading_state.json'
        
        # Load saved state if exists
        self.load_state()
        
    def is_market_open_day(self):
        """Check if today is a trading day (weekday, not holiday)."""
        now = datetime.now()
        
        # Check if weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check common US market holidays
        year = now.year
        holidays = [
            datetime(year, 1, 1),   # New Year's Day
            datetime(year, 7, 4),   # Independence Day
            datetime(year, 12, 25), # Christmas
        ]
        
        # Move holiday to Friday if it falls on Saturday, Monday if Sunday
        adjusted_holidays = []
        for holiday in holidays:
            if holiday.weekday() == 5:  # Saturday
                adjusted_holidays.append(holiday - timedelta(days=1))
            elif holiday.weekday() == 6:  # Sunday
                adjusted_holidays.append(holiday + timedelta(days=1))
            else:
                adjusted_holidays.append(holiday)
        
        today = now.date()
        return today not in [h.date() for h in adjusted_holidays]
    
    def next_market_open(self):
        """Calculate when the next market day is."""
        now = datetime.now()
        next_day = now + timedelta(days=1)
        
        while not self.is_market_open_day_check(next_day):
            next_day += timedelta(days=1)
        
        return next_day
    
    def is_market_open_day_check(self, check_date):
        """Check if a specific date is a trading day."""
        # Check if weekend
        if check_date.weekday() >= 5:
            return False
        
        # Check common US market holidays
        year = check_date.year
        holidays = [
            datetime(year, 1, 1),
            datetime(year, 7, 4),
            datetime(year, 12, 25),
        ]
        
        adjusted_holidays = []
        for holiday in holidays:
            if holiday.weekday() == 5:
                adjusted_holidays.append(holiday - timedelta(days=1))
            elif holiday.weekday() == 6:
                adjusted_holidays.append(holiday + timedelta(days=1))
            else:
                adjusted_holidays.append(holiday)
        
        check = check_date.date()
        return check not in [h.date() for h in adjusted_holidays]
    
    def save_state(self):
        """Save current strategy state to JSON file."""
        try:
            state = {
                'cash': self.cash,
                'positions': self.positions,
                'last_rebalance': self.last_rebalance.isoformat() if self.last_rebalance else None,
                'initial_capital': self.initial_capital
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def load_state(self):
        """Load strategy state from JSON file if it exists."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.cash = state['cash']
                self.positions = state['positions']
                self.last_rebalance = datetime.fromisoformat(state['last_rebalance']) if state['last_rebalance'] else None
                self.initial_capital = state['initial_capital']
                
                logger.info(f"State loaded from {self.state_file}")
                logger.info(f"Cash: ${self.cash:,.2f}, Positions: {len(self.positions)}")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
    
    def get_current_price(self, symbol):
        """Get current price for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def calculate_portfolio_value(self):
        """Calculate total portfolio value including positions."""
        total_value = self.cash
        
        for symbol, pos in self.positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                if pos['side'] == 'long':
                    # Long position: profit when price goes up
                    position_value = pos['qty'] * current_price
                else:
                    # Short position: profit when price goes down
                    position_value = pos['qty'] * pos['entry_price'] * 2 - pos['qty'] * current_price
                
                total_value += position_value
        
        return total_value
    
    def write_positions_to_file(self):
        """Write current portfolio state to positions.txt."""
        try:
            portfolio_value = self.calculate_portfolio_value()
            
            with open(self.positions_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write(f"PORTFOLIO STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Initial Capital:    ${self.initial_capital:,.2f}\n")
                f.write(f"Current Cash:       ${self.cash:,.2f}\n")
                f.write(f"Portfolio Value:    ${portfolio_value:,.2f}\n")
                f.write(f"Total P&L:          ${portfolio_value - self.initial_capital:,.2f} ")
                f.write(f"({((portfolio_value / self.initial_capital - 1) * 100):.2f}%)\n\n")
                
                if self.positions:
                    f.write("CURRENT POSITIONS:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"{'Symbol':<10} {'Side':<8} {'Qty':<8} {'Entry':<12} {'Current':<12} {'P&L':<15} {'P&L %':<10}\n")
                    f.write("-"*80 + "\n")
                    
                    for symbol, pos in self.positions.items():
                        current_price = self.get_current_price(symbol)
                        if current_price:
                            if pos['side'] == 'long':
                                pnl = pos['qty'] * (current_price - pos['entry_price'])
                                pnl_pct = ((current_price / pos['entry_price']) - 1) * 100
                            else:  # short
                                pnl = pos['qty'] * (pos['entry_price'] - current_price)
                                pnl_pct = ((pos['entry_price'] / current_price) - 1) * 100
                            
                            f.write(f"{symbol:<10} {pos['side']:<8} {pos['qty']:<8} "
                                  f"${pos['entry_price']:<11.2f} ${current_price:<11.2f} "
                                  f"${pnl:<14.2f} {pnl_pct:<9.2f}%\n")
                else:
                    f.write("No open positions\n")
                
                f.write("\n" + "="*80 + "\n")
                
                if self.last_rebalance:
                    f.write(f"Last Rebalance: {self.last_rebalance.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    days_since = (datetime.now() - self.last_rebalance).days
                    next_rebalance_days = max(0, self.rebalance_period - days_since)
                    f.write(f"Next Rebalance: In {next_rebalance_days} market days\n")
                
                f.write(f"Market Status: {'OPEN' if self.is_market_open_day() else 'CLOSED'}\n")
                
            logger.info(f"Portfolio written to {self.positions_file}")
            
        except Exception as e:
            logger.error(f"Error writing positions to file: {e}")
    
    def calculate_momentum(self, symbol, lookback_days):
        """
        Calculate momentum score for a given symbol.
        Momentum = (Current Price / Price N days ago) - 1
        
        Args:
            symbol: Stock ticker symbol
            lookback_days: Number of days to look back
            
        Returns:
            Momentum score as a percentage
        """
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            end = datetime.now()
            start = end - timedelta(days=lookback_days + 30)  # Extra buffer for weekends
            
            data = ticker.history(start=start, end=end)
            
            if len(data) < lookback_days:
                logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Calculate momentum
            current_price = data['Close'].iloc[-1]
            past_price = data['Close'].iloc[-lookback_days]
            momentum = (current_price / past_price - 1) * 100
            
            return momentum
            
        except Exception as e:
            logger.error(f"Error calculating momentum for {symbol}: {e}")
            return None
    
    def rank_stocks_by_momentum(self):
        """
        Rank all stocks in the universe by their momentum scores.
        
        Returns:
            DataFrame with symbols and momentum scores, sorted by momentum
        """
        logger.info("Calculating momentum scores for universe...")
        
        momentum_data = []
        for symbol in self.universe:
            momentum = self.calculate_momentum(symbol, self.lookback_period)
            if momentum is not None:
                momentum_data.append({'symbol': symbol, 'momentum': momentum})
            time.sleep(0.1)  # Be nice to Yahoo Finance
        
        df = pd.DataFrame(momentum_data)
        df = df.sort_values('momentum', ascending=False).reset_index(drop=True)
        
        logger.info(f"\nTop 5 momentum stocks:")
        logger.info(df.head().to_string())
        logger.info(f"\nBottom 5 momentum stocks:")
        logger.info(df.tail().to_string())
        
        return df
    
    def close_all_positions(self):
        """Close all open positions at current market prices."""
        logger.info("Closing all positions...")
        
        for symbol, pos in list(self.positions.items()):
            current_price = self.get_current_price(symbol)
            if current_price:
                if pos['side'] == 'long':
                    # Close long: sell at current price
                    proceeds = pos['qty'] * current_price
                    pnl = proceeds - (pos['qty'] * pos['entry_price'])
                else:
                    # Close short: buy back at current price
                    cost = pos['qty'] * current_price
                    proceeds = pos['qty'] * pos['entry_price']
                    pnl = proceeds - cost
                
                self.cash += proceeds if pos['side'] == 'long' else (2 * proceeds - cost)
                logger.info(f"CLOSE {pos['side'].upper()} {symbol}: {pos['qty']} shares, P&L: ${pnl:.2f}")
        
        self.positions = {}
        logger.info("All positions closed")
    
    def execute_trades(self, long_symbols, short_symbols):
        """
        Execute trades to establish new positions.
        
        Args:
            long_symbols: List of symbols to go long
            short_symbols: List of symbols to go short
        """
        portfolio_value = self.calculate_portfolio_value()
        position_value = portfolio_value * self.position_size
        
        # Execute long positions
        for symbol in long_symbols:
            try:
                current_price = self.get_current_price(symbol)
                if current_price:
                    qty = int(position_value / current_price)
                    
                    if qty > 0:
                        cost = qty * current_price
                        if cost <= self.cash:
                            self.positions[symbol] = {
                                'qty': qty,
                                'entry_price': current_price,
                                'side': 'long'
                            }
                            self.cash -= cost
                            logger.info(f"BUY {qty} shares of {symbol} at ${current_price:.2f}")
                        else:
                            logger.warning(f"Insufficient cash for {symbol}")
            except Exception as e:
                logger.error(f"Error buying {symbol}: {e}")
        
        # Execute short positions
        for symbol in short_symbols:
            try:
                current_price = self.get_current_price(symbol)
                if current_price:
                    qty = int(position_value / current_price)
                    
                    if qty > 0:
                        proceeds = qty * current_price
                        self.positions[symbol] = {
                            'qty': qty,
                            'entry_price': current_price,
                            'side': 'short'
                        }
                        self.cash += proceeds  # Receive cash from short sale
                        logger.info(f"SHORT {qty} shares of {symbol} at ${current_price:.2f}")
            except Exception as e:
                logger.error(f"Error shorting {symbol}: {e}")
    
    def rebalance_portfolio(self):
        """
        Rebalance the portfolio based on current momentum rankings.
        """
        logger.info("\n" + "="*60)
        logger.info("REBALANCING PORTFOLIO")
        logger.info("="*60)
        
        # Get momentum rankings
        ranked_stocks = self.rank_stocks_by_momentum()
        
        # Select top and bottom stocks
        long_symbols = ranked_stocks.head(self.num_long)['symbol'].tolist()
        short_symbols = ranked_stocks.tail(self.num_short)['symbol'].tolist()
        
        logger.info(f"\nTarget Long Positions: {long_symbols}")
        logger.info(f"Target Short Positions: {short_symbols}")
        
        # Close existing positions
        self.close_all_positions()
        
        # Execute new trades
        self.execute_trades(long_symbols, short_symbols)
        
        self.last_rebalance = datetime.now()
        logger.info(f"\nRebalance completed at {self.last_rebalance}")
        logger.info("="*60 + "\n")
        
        # Save state and write positions
        self.save_state()
        self.write_positions_to_file()
    
    def should_rebalance(self):
        """Check if it's time to rebalance."""
        if self.last_rebalance is None:
            return True
        
        days_since_rebalance = (datetime.now() - self.last_rebalance).days
        return days_since_rebalance >= self.rebalance_period
    
    def run_continuous(self):
        """
        Continuous execution loop that handles weekends and holidays.
        """
        logger.info("Starting Momentum Trading Strategy (Continuous Mode)")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Lookback Period: {self.lookback_period} days")
        logger.info(f"Rebalance Period: {self.rebalance_period} days")
        logger.info(f"Long Positions: {self.num_long}")
        logger.info(f"Short Positions: {self.num_short}\n")
        
        while True:
            try:
                now = datetime.now()
                
                # Check if market is open today
                if not self.is_market_open_day():
                    next_open = self.next_market_open()
                    logger.info(f"Market is closed (Weekend/Holiday)")
                    logger.info(f"Next market day: {next_open.strftime('%Y-%m-%d')}")
                    logger.info("Sleeping until next market day...\n")
                    
                    # Update positions file even when market is closed
                    self.write_positions_to_file()
                    
                    # Sleep until next day
                    time.sleep(43200)  # 12 hours
                    continue
                
                # Market is open - check if we should rebalance
                if self.should_rebalance():
                    logger.info("Market is open - executing rebalance...")
                    self.rebalance_portfolio()
                else:
                    days_left = self.rebalance_period - (datetime.now() - self.last_rebalance).days
                    logger.info(f"Market is open - Next rebalance in {days_left} market days")
                    
                    # Update positions file
                    self.write_positions_to_file()
                
                # Check again in 4 hours
                logger.info("Sleeping for 4 hours before next check...\n")
                time.sleep(14400)  # 4 hours
                
            except KeyboardInterrupt:
                logger.info("\nStrategy stopped by user")
                self.save_state()
                self.write_positions_to_file()
                logger.info("State saved. You can restart anytime!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info("Retrying in 5 minutes...")
                time.sleep(300)


def main():
    """
    Main entry point for the trading algorithm.
    No API keys needed - uses yfinance!
    
    Just run this and leave it - it handles everything:
    - Runs immediately if market is open
    - Waits over weekends automatically
    - Saves state so you can stop/restart anytime
    - Updates positions.txt regularly
    """
    
    # Initialize strategy with $100,000 starting capital
    strategy = MomentumTradingStrategy(initial_capital=100000)
    
    # Run continuously
    strategy.run_continuous()


if __name__ == "__main__":
    main()
