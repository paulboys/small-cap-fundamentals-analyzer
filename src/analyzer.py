import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .utils import calculate_ratios, validate_financial_data

class FundamentalsAnalyzer:
    def __init__(self):
        self.data_cache = {}

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive fundamental data for a single stock symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dict containing fundamental metrics
        """
        if symbol in self.data_cache:
            return self.data_cache[symbol]
            
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            fundamentals = {
                'symbol': symbol,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'revenue': self._get_latest_value(financials, 'Total Revenue'),
                'net_income': self._get_latest_value(financials, 'Net Income'),
                'total_assets': self._get_latest_value(balance_sheet, 'Total Assets'),
                'total_liabilities': self._get_latest_value(balance_sheet, 'Total Liab'),
                'revenue_growth': self._calculate_growth_rate(financials, 'Total Revenue'),
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'roe': info.get('returnOnEquity', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
            
            self.data_cache[symbol] = fundamentals
            return fundamentals
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return {}

    
    def screen_small_caps(self, symbols: List[str], max_market_cap: float = 2e9, 
                        min_roe: float = 0.10, max_pe: float = 15) -> pd.DataFrame:
        """
        Screen for small-cap investment opportunities.
        
        Args:
            symbols: List of stock symbols to screen
            max_market_cap: Maximum market cap for small-cap (default 2B)
            min_roe: Minimum ROE threshold
            max_pe: Maximum P/E ratio
            
        Returns:
            DataFrame of qualified small-cap opportunities
        """
        df = self.analyze_companies(symbols)
        
        if df.empty:
            return df
        
        # Apply screening criteria
        small_caps = df[
            (df['market_cap'] <= max_market_cap) &
            (df['market_cap'] > 0) &
            (df['roe'] >= min_roe) &
            (df['pe_ratio'] <= max_pe) &
            (df['pe_ratio'] > 0) &
            (df['profit_margin'] > 0)  # Must be profitable
        ].copy()
        
        # Calculate a simple opportunity score
        if not small_caps.empty:
            small_caps['opportunity_score'] = (
                (small_caps['roe'] * 100) +  # ROE weight
                ((20 - small_caps['pe_ratio']) * 2) +  # Lower P/E is better
                (small_caps['profit_margin'] * 50) +  # Profit margin weight
                (small_caps['revenue_growth'] * 2)  # Growth weight
            )
            
            small_caps = small_caps.sort_values('opportunity_score', ascending=False)
        
        return small_caps

    def analyze_companies(self, symbols: List[str]) -> pd.DataFrame:
        """
        Analyze multiple companies and return comparison DataFrame.
        
        Args:
            symbols (List[str]): List of stock symbols
            
        Returns:
            DataFrame with fundamental metrics for all companies
        """
        results = []
        for symbol in symbols:
            fundamentals = self.get_fundamentals(symbol)
            if fundamentals:
                results.append(fundamentals)
                
        return pd.DataFrame(results)

    def compare_companies(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Compare fundamental metrics across multiple companies.
        
        Args:
            symbols (List[str]): List of stock symbols to compare
            
        Returns:
            Dict containing comparison metrics and rankings
        """
        df = self.analyze_companies(symbols)
        
        if df.empty:
            return {}
            
        comparison = {
            'summary': df.describe(),
            'rankings': {
                'lowest_pe': df.nsmallest(5, 'pe_ratio')[['symbol', 'pe_ratio']],
                'highest_roe': df.nlargest(5, 'roe')[['symbol', 'roe']],
                'highest_growth': df.nlargest(5, 'revenue_growth')[['symbol', 'revenue_growth']],
                'best_margins': df.nlargest(5, 'profit_margin')[['symbol', 'profit_margin']]
            }
        }
        
        return comparison

    def create_sector_comparison(self, results: pd.DataFrame, sector: str) -> Dict[str, Any]:
        """
        Create sector-specific analysis and comparison.
        
        Args:
            results (DataFrame): Analysis results
            sector (str): Sector to analyze
            
        Returns:
            Dict containing sector analysis
        """
        sector_data = results[results['sector'] == sector] if not results.empty else pd.DataFrame()
        
        if sector_data.empty:
            return {'error': f'No data found for sector: {sector}'}
            
        analysis = {
            'sector': sector,
            'company_count': len(sector_data),
            'avg_pe_ratio': sector_data['pe_ratio'].mean(),
            'avg_roe': sector_data['roe'].mean(),
            'avg_profit_margin': sector_data['profit_margin'].mean(),
            'top_performers': sector_data.nlargest(3, 'roe')[['symbol', 'roe', 'pe_ratio']],
            'undervalued_candidates': sector_data[
                (sector_data['pe_ratio'] < sector_data['pe_ratio'].median()) &
                (sector_data['roe'] > sector_data['roe'].median())
            ][['symbol', 'pe_ratio', 'roe', 'market_cap']]
        }
        
        return analysis

    def _get_latest_value(self, df: pd.DataFrame, column: str) -> float:
        """Get the most recent value from financial statement data."""
        try:
            if df is not None and column in df.index:
                return float(df.loc[column].iloc[0])
            return 0.0
        except (IndexError, ValueError, KeyError):
            return 0.0

    def _calculate_growth_rate(self, df: pd.DataFrame, column: str) -> float:
        """Calculate year-over-year growth rate."""
        try:
            if df is not None and column in df.index and len(df.columns) >= 2:
                current = df.loc[column].iloc[0]
                previous = df.loc[column].iloc[1]
                if previous != 0:
                    return ((current - previous) / abs(previous)) * 100
            return 0.0
        except (IndexError, ValueError, KeyError):
            return 0.0

    # Legacy methods for backward compatibility
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, float]:
        """Legacy method for backward compatibility."""
        metrics = {}
        
        if 'revenue' in stock_data and 'net_income' in stock_data:
            metrics['profit_margin'] = stock_data['net_income'] / stock_data['revenue']
            
        if 'liabilities' in stock_data and 'assets' in stock_data:
            equity = stock_data['assets'] - stock_data['liabilities']
            if equity != 0:
                metrics['debt_to_equity'] = stock_data['liabilities'] / equity
                
        return metrics

    def calculate_price_to_earnings(self, stock_data: Dict[str, Any]) -> float:
        """Legacy method for backward compatibility."""
        if 'price' in stock_data and 'earnings_per_share' in stock_data:
            if stock_data['earnings_per_share'] != 0:
                return stock_data['price'] / stock_data['earnings_per_share']
        return 0.0

    def calculate_debt_to_equity(self, stock_data: Dict[str, Any]) -> float:
        """Legacy method for backward compatibility."""
        if 'total_liabilities' in stock_data and 'shareholder_equity' in stock_data:
            if stock_data['shareholder_equity'] != 0:
                return stock_data['total_liabilities'] / stock_data['shareholder_equity']
        return 0.0
    
    