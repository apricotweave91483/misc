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
                    f.write(f"Next Rebalance: In {self.rebalance_period - days_since} days\n")
                
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
        
        # Write positions to file
        self.write_positions_to_file()
    
    def should_rebalance(self):
        """Check if it's time to rebalance."""
        if self.last_rebalance is None:
            return True
        
        days_since_rebalance = (datetime.now() - self.last_rebalance).days
        return days_since_rebalance >= self.rebalance_period
    
    def run(self, single_run=False):
        """
        Main execution loop.
        
        Args:
            single_run: If True, run once and exit. If False, run continuously.
        """
        logger.info("Starting Momentum Trading Strategy")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Lookback Period: {self.lookback_period} days")
        logger.info(f"Rebalance Period: {self.rebalance_period} days")
        logger.info(f"Long Positions: {self.num_long}")
        logger.info(f"Short Positions: {self.num_short}\n")
        
        if single_run:
            # Run once and exit
            self.rebalance_portfolio()
            
            # Show final portfolio
            portfolio_value = self.calculate_portfolio_value()
            logger.info(f"\nFinal Portfolio Value: ${portfolio_value:,.2f}")
            logger.info(f"Total P&L: ${portfolio_value - self.initial_capital:,.2f} "
                       f"({((portfolio_value / self.initial_capital - 1) * 100):.2f}%)")
        else:
            # Continuous execution
            while True:
                try:
                    if self.should_rebalance():
                        self.rebalance_portfolio()
                    else:
                        days_left = self.rebalance_period - (datetime.now() - self.last_rebalance).days
                        logger.info(f"Next rebalance in {days_left} days")
                        
                        # Update positions file even when not rebalancing
                        self.write_positions_to_file()
                    
                    # Wait before next check (1 day)
                    logger.info("Waiting for next check...\n")
                    time.sleep(86400)  # 24 hours
                    
                except KeyboardInterrupt:
                    logger.info("Strategy stopped by user")
                    self.write_positions_to_file()
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(60)


def main():
    """
    Main entry point for the trading algorithm.
    No API keys needed - uses yfinance!
    """
    
    # Initialize strategy with $100,000 starting capital
    strategy = MomentumTradingStrategy(initial_capital=100000)
    
    # Run once for testing (set to False for continuous operation)
    strategy.run(single_run=True)


if __name__ == "__main__":
    main()
