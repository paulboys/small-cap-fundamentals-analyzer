import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import time
import requests
from datetime import datetime, timedelta

class DataExtractor:
    def __init__(self, rate_limit_delay: float = 0.1):
        """
        Initialize the DataExtractor.
        
        Args:
            rate_limit_delay (float): Delay between API calls to respect rate limits
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
    def extract_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        Extract comprehensive stock data for a given symbol.
        
        Args:
            symbol (str): Stock symbol
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dict containing stock data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            
            # Get historical data
            hist = ticker.history(period=period)
            
            # Get financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Get additional data
            dividends = ticker.dividends
            splits = ticker.splits
            
            stock_data = {
                'symbol': symbol,
                'info': info,
                'historical_data': hist,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'dividends': dividends,
                'splits': splits,
                'last_updated': datetime.now()
            }
            
            # Add rate limiting
            time.sleep(self.rate_limit_delay)
            
            return stock_data
            
        except Exception as e:
            print(f"Error extracting data for {symbol}: {e}")
            return {}
    
    def extract_multiple_stocks(self, symbols: List[str], period: str = "1y") -> Dict[str, Dict[str, Any]]:
        """
        Extract data for multiple stocks.
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Data period
            
        Returns:
            Dict mapping symbols to their data
        """
        results = {}
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            print(f"Extracting data for {symbol} ({i+1}/{total})")
            data = self.extract_stock_data(symbol, period)
            if data:
                results[symbol] = data
                
        return results
    
    def get_sector_stocks(self, sector: str, max_stocks: int = 50) -> List[str]:
        """
        Get a list of stocks in a specific sector.
        
        Args:
            sector (str): Sector name
            max_stocks (int): Maximum number of stocks to return
            
        Returns:
            List of stock symbols
        """
        # This is a simplified implementation
        # In practice, you would use a comprehensive stock database or API
        sector_mappings = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'CRM', 'ORCL'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'BMY', 'AMGN', 'GILD', 'VRTX'],
            'Financial Services': ['BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'USB', 'PNC'],
            'Consumer Discretionary': ['AMZN', 'HD', 'NKE', 'MCD', 'LOW', 'TJX', 'SBUX', 'TGT', 'F', 'GM'],
            'Industrial': ['BA', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'CAT', 'DE', 'MMM', 'GE']
        }
        
        return sector_mappings.get(sector, [])[:max_stocks]
    
    def extract_financial_ratios(self, symbol: str) -> Dict[str, float]:
        """
        Extract key financial ratios for a stock.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict containing financial ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            ratios = {
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'gross_margin': info.get('grossMargins', 0),
                'beta': info.get('beta', 0),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'ev_revenue': info.get('enterpriseToRevenue', 0),
                'ev_ebitda': info.get('enterpriseToEbitda', 0)
            }
            
            return ratios
            
        except Exception as e:
            print(f"Error extracting ratios for {symbol}: {e}")
            return {}
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data for a stock.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict containing market data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            market_data = {
                'symbol': symbol,
                'current_price': info.get('currentPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'open': info.get('open', 0),
                'day_low': info.get('dayLow', 0),
                'day_high': info.get('dayHigh', 0),
                'volume': info.get('volume', 0),
                'average_volume': info.get('averageVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'ex_dividend_date': info.get('exDividendDate', None),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error extracting market data for {symbol}: {e}")
            return {}
    
    def extract_earnings_data(self, symbol: str) -> Dict[str, Any]:
        """
        Extract earnings-related data for a stock.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict containing earnings data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            earnings_data = {
                'symbol': symbol,
                'earnings': ticker.earnings,
                'quarterly_earnings': ticker.quarterly_earnings,
                'calendar': ticker.calendar,
                'recommendations': ticker.recommendations,
                'analyst_price_target': ticker.info.get('targetMeanPrice', 0),
                'recommendation_key': ticker.info.get('recommendationKey', 'none')
            }
            
            return earnings_data
            
        except Exception as e:
            print(f"Error extracting earnings data for {symbol}: {e}")
            return {}