import yfinance as yf
import pandas as pd
from typing import Dict, List, Any
from .analyzer import FundamentalsAnalyzer

class SmallCapScreener:
    def __init__(self, max_market_cap: float = 2e9):
        """
        Initialize the SmallCapScreener.
        
        Args:
            max_market_cap (float): Maximum market cap for small-cap classification
        """
        self.max_market_cap = max_market_cap
        self.analyzer = FundamentalsAnalyzer()
        
        # Sector mappings
        self.sector_keywords = {
            'Healthcare': ['biotech', 'pharma', 'medical', 'health', 'drug'],
            'Technology': ['software', 'semiconductor', 'tech', 'digital', 'internet'],
            'Consumer Discretionary': ['retail', 'automotive', 'leisure', 'restaurant'],
            'Consumer Staples': ['food', 'beverage', 'household', 'grocery'],
            'Financial Services': ['bank', 'insurance', 'real estate', 'finance'],
            'Industrial': ['manufacturing', 'aerospace', 'transportation', 'defense'],
            'Energy': ['oil', 'gas', 'renewable', 'energy', 'petroleum'],
            'Materials': ['chemical', 'metal', 'mining', 'steel', 'aluminum'],
            'Utilities': ['electric', 'gas', 'water', 'utility'],
            'Communication Services': ['telecom', 'media', 'entertainment', 'broadcasting']
        }

    def screen_sector(self, sector: str, max_market_cap: float = None) -> List[str]:
        """
        Screen for small-cap stocks in a specific sector.
        
        Args:
            sector (str): Target sector
            max_market_cap (float): Override default market cap limit
            
        Returns:
            List of stock symbols meeting criteria
        """
        market_cap_limit = max_market_cap or self.max_market_cap
        
        # This is a simplified implementation
        # In practice, you'd use a stock screener API or database
        sample_symbols = self._get_sample_symbols_by_sector(sector)
        
        candidates = []
        for symbol in sample_symbols:
            fundamentals = self.analyzer.get_fundamentals(symbol)
            if (fundamentals and 
                fundamentals.get('market_cap', float('inf')) <= market_cap_limit and
                fundamentals.get('sector', '').lower() == sector.lower()):
                candidates.append(symbol)
                
        return candidates

    def screen_by_criteria(self, sector: str, criteria: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Screen stocks based on multiple fundamental criteria.
        
        Args:
            sector (str): Target sector
            criteria (Dict): Screening criteria
            
        Returns:
            List of candidate stocks with their metrics
        """
        symbols = self.screen_sector(sector, criteria.get('max_market_cap'))
        candidates = []
        
        for symbol in symbols:
            fundamentals = self.analyzer.get_fundamentals(symbol)
            if not fundamentals:
                continue
                
            # Apply screening criteria
            if self._meets_criteria(fundamentals, criteria):
                candidates.append({
                    'symbol': symbol,
                    'market_cap': fundamentals.get('market_cap', 0),
                    'pe_ratio': fundamentals.get('pe_ratio', 0),
                    'roe': fundamentals.get('roe', 0),
                    'debt_to_equity': fundamentals.get('debt_to_equity', 0),
                    'profit_margin': fundamentals.get('profit_margin', 0),
                    'revenue_growth': fundamentals.get('revenue_growth', 0),
                    'score': self._calculate_score(fundamentals, criteria)
                })
        
        # Sort by score (higher is better)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates

    def _meets_criteria(self, fundamentals: Dict[str, Any], criteria: Dict[str, float]) -> bool:
        """Check if a stock meets all screening criteria."""
        checks = [
            fundamentals.get('market_cap', float('inf')) <= criteria.get('max_market_cap', float('inf')),
            fundamentals.get('revenue', 0) >= criteria.get('min_revenue', 0),
            fundamentals.get('pe_ratio', float('inf')) <= criteria.get('max_pe_ratio', float('inf')),
            fundamentals.get('roe', 0) >= criteria.get('min_roe', 0),
            fundamentals.get('debt_to_equity', float('inf')) <= criteria.get('max_debt_equity', float('inf'))
        ]
        return all(checks)

    def _calculate_score(self, fundamentals: Dict[str, Any], criteria: Dict[str, float]) -> float:
        """Calculate a composite score for ranking candidates."""
        score = 0
        
        # ROE score (higher is better)
        roe = fundamentals.get('roe', 0)
        score += min(roe * 100, 50)  # Cap at 50 points
        
        # P/E score (lower is better, up to a point)
        pe_ratio = fundamentals.get('pe_ratio', float('inf'))
        if 5 <= pe_ratio <= 20:
            score += (20 - pe_ratio) * 2
        elif pe_ratio < 5:
            score += 10  # Very low P/E might indicate problems
            
        # Profit margin score
        profit_margin = fundamentals.get('profit_margin', 0)
        score += min(profit_margin * 200, 30)  # Cap at 30 points
        
        # Revenue growth score
        revenue_growth = fundamentals.get('revenue_growth', 0)
        if revenue_growth > 0:
            score += min(revenue_growth, 20)  # Cap at 20 points
            
        # Debt penalty
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        if debt_to_equity > 1:
            score -= (debt_to_equity - 1) * 10
            
        return max(score, 0)  # Ensure non-negative score

    def _get_sample_symbols_by_sector(self, sector: str) -> List[str]:
        """
        Get sample symbols for a sector. In practice, this would query
        a comprehensive database or API.
        """
        sector_samples = {
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'BMY', 'AMGN', 'GILD', 'VRTX'],
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'CRM', 'ORCL'],
            'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD', 'LOW', 'TJX', 'SBUX', 'TGT', 'F'],
            'Financial Services': ['BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'USB', 'PNC'],
            'Industrial': ['BA', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'CAT', 'DE', 'MMM', 'GE'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'BKR'],
            'Materials': ['LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'PPG', 'IFF'],
            'Consumer Staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K', 'HSY'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PEG', 'ED'],
            'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR', 'TMUS', 'ATVI']
        }
        
        return sector_samples.get(sector, [])