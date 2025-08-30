import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.screener import SmallCapScreener


class TestSmallCapScreener:
    
    @pytest.fixture
    def screener(self):
        return SmallCapScreener(max_market_cap=2e9)
    
    @pytest.fixture
    def mock_fundamentals_data(self):
        return [
            {
                'symbol': 'SMALL1',
                'market_cap': 1.5e9,
                'pe_ratio': 12.5,
                'roe': 0.15,
                'debt_to_equity': 0.3,
                'profit_margin': 0.12,
                'revenue_growth': 8.5,
                'revenue': 500e6,
                'sector': 'Healthcare'
            },
            {
                'symbol': 'SMALL2', 
                'market_cap': 1.8e9,
                'pe_ratio': 18.2,
                'roe': 0.18,
                'debt_to_equity': 0.4,
                'profit_margin': 0.10,
                'revenue_growth': 12.3,
                'revenue': 600e6,
                'sector': 'Healthcare'
            },
            {
                'symbol': 'LARGE1',
                'market_cap': 5e9,  # Too large
                'pe_ratio': 15.0,
                'roe': 0.20,
                'debt_to_equity': 0.2,
                'profit_margin': 0.15,
                'revenue_growth': 10.0,
                'revenue': 2e9,
                'sector': 'Healthcare'
            }
        ]

    def test_initialization(self, screener):
        # Test default initialization
        assert screener.max_market_cap == 2e9
        assert hasattr(screener, 'analyzer')
        assert hasattr(screener, 'sector_keywords')
        
        # Test custom initialization
        custom_screener = SmallCapScreener(max_market_cap=1e9)
        assert custom_screener.max_market_cap == 1e9

    def test_sector_keywords_coverage(self, screener):
        # Test that all major sectors are covered
        expected_sectors = [
            'Healthcare', 'Technology', 'Consumer Discretionary',
            'Consumer Staples', 'Financial Services', 'Industrial',
            'Energy', 'Materials', 'Utilities', 'Communication Services'
        ]
        
        for sector in expected_sectors:
            assert sector in screener.sector_keywords
            assert len(screener.sector_keywords[sector]) > 0

    @patch('src.screener.SmallCapScreener._get_sample_symbols_by_sector')
    def test_screen_sector_success(self, mock_get_symbols, screener, mock_fundamentals_data):
        # Setup mocks
        mock_get_symbols.return_value = ['SMALL1', 'SMALL2', 'LARGE1']
        
        def mock_get_fundamentals(symbol):
            for data in mock_fundamentals_data:
                if data['symbol'] == symbol:
                    return data
            return {}
        
        screener.analyzer.get_fundamentals = Mock(side_effect=mock_get_fundamentals)
        
        # Test
        result = screener.screen_sector('Healthcare')
        
        # Assertions
        assert len(result) == 2  # Only SMALL1 and SMALL2 should pass
        assert 'SMALL1' in result
        assert 'SMALL2' in result
        assert 'LARGE1' not in result

    @patch('src.screener.SmallCapScreener._get_sample_symbols_by_sector')
    def test_screen_sector_custom_market_cap(self, mock_get_symbols, screener, mock_fundamentals_data):
        # Setup mocks
        mock_get_symbols.return_value = ['SMALL1', 'SMALL2']
        screener.analyzer.get_fundamentals = Mock(side_effect=lambda s: 
            next((d for d in mock_fundamentals_data if d['symbol'] == s), {}))
        
        # Test with lower market cap limit
        result = screener.screen_sector('Healthcare', max_market_cap=1.6e9)
        
        # Assertions
        assert len(result) == 1  # Only SMALL1 should pass (1.5e9 < 1.6e9)
        assert 'SMALL1' in result
        assert 'SMALL2' not in result

    def test_screen_by_criteria_success(self, screener, mock_fundamentals_data):
        # Setup mock
        screener.screen_sector = Mock(return_value=['SMALL1', 'SMALL2', 'LARGE1'])
        screener.analyzer.get_fundamentals = Mock(side_effect=lambda s:
            next((d for d in mock_fundamentals_data if d['symbol'] == s), {}))
        
        # Define criteria
        criteria = {
            'max_market_cap': 2e9,
            'min_revenue': 400e6,
            'max_pe_ratio': 15,
            'min_roe': 0.12,
            'max_debt_equity': 0.5
        }
        
        # Test
        result = screener.screen_by_criteria('Healthcare', criteria)
        
        # Assertions
        assert len(result) > 0
        assert all(candidate['pe_ratio'] <= 15 for candidate in result)
        assert all(candidate['roe'] >= 0.12 for candidate in result)
        assert 'score' in result[0]  # Check that scoring was applied

    def test_meets_criteria_success(self, screener):
        # Test data that meets all criteria
        fundamentals = {
            'market_cap': 1.5e9,
            'revenue': 500e6,
            'pe_ratio': 12.0,
            'roe': 0.15,
            'debt_to_equity': 0.3
        }
        
        criteria = {
            'max_market_cap': 2e9,
            'min_revenue': 400e6,
            'max_pe_ratio': 15,
            'min_roe': 0.10,
            'max_debt_equity': 0.5
        }
        
        # Test
        result = screener._meets_criteria(fundamentals, criteria)
        
        # Assertions
        assert result == True

    def test_meets_criteria_failure(self, screener):
        # Test data that fails criteria
        fundamentals = {
            'market_cap': 3e9,  # Too large
            'revenue': 200e6,   # Too small
            'pe_ratio': 25.0,   # Too high
            'roe': 0.05,        # Too low
            'debt_to_equity': 0.8  # Too high
        }
        
        criteria = {
            'max_market_cap': 2e9,
            'min_revenue': 400e6,
            'max_pe_ratio': 15,
            'min_roe': 0.10,
            'max_debt_equity': 0.5
        }
        
        # Test
        result = screener._meets_criteria(fundamentals, criteria)
        
        # Assertions
        assert result == False

    def test_calculate_score_high_quality_stock(self, screener):
        # Test high-quality stock fundamentals
        fundamentals = {
            'roe': 0.20,           # 20% ROE = 20 points (capped at 50)
            'pe_ratio': 12.0,      # Good P/E = 16 points (20-12)*2
            'profit_margin': 0.15, # 15% margin = 30 points (capped at 30)
            'revenue_growth': 15.0, # 15% growth = 15 points (capped at 20)
            'debt_to_equity': 0.3   # Low debt = no penalty
        }
        
        criteria = {}
        
        # Test
        score = screener._calculate_score(fundamentals, criteria)
        
        # Assertions
        assert score > 70  # Should be high score
        assert isinstance(score, float)

    def test_calculate_score_poor_quality_stock(self, screener):
        # Test poor-quality stock fundamentals
        fundamentals = {
            'roe': 0.02,           # Low ROE
            'pe_ratio': 35.0,      # High P/E
            'profit_margin': 0.01, # Low margin
            'revenue_growth': -5.0, # Negative growth
            'debt_to_equity': 2.0   # High debt
        }
        
        criteria = {}
        
        # Test
        score = screener._calculate_score(fundamentals, criteria)
        
        # Assertions
        assert score < 20  # Should be low score
        assert score >= 0  # Score should not be negative

    def test_calculate_score_missing_data(self, screener):
        # Test with missing fundamental data
        fundamentals = {}
        criteria = {}
        
        # Test
        score = screener._calculate_score(fundamentals, criteria)
        
        # Assertions
        assert score == 0  # Should handle missing data gracefully

    def test_get_sample_symbols_by_sector_healthcare(self, screener):
        # Test healthcare sector symbols
        symbols = screener._get_sample_symbols_by_sector('Healthcare')
        
        # Assertions
        assert len(symbols) > 0
        assert isinstance(symbols, list)
        assert all(isinstance(symbol, str) for symbol in symbols)

    def test_get_sample_symbols_by_sector_technology(self, screener):
        # Test technology sector symbols
        symbols = screener._get_sample_symbols_by_sector('Technology')
        
        # Assertions
        assert len(symbols) > 0
        assert 'AAPL' in symbols or 'MSFT' in symbols  # Should contain major tech stocks

    def test_get_sample_symbols_by_sector_unknown(self, screener):
        # Test unknown sector
        symbols = screener._get_sample_symbols_by_sector('UnknownSector')
        
        # Assertions
        assert symbols == []

    def test_screen_by_criteria_empty_results(self, screener):
        # Setup mock to return no symbols
        screener.screen_sector = Mock(return_value=[])
        
        criteria = {'max_market_cap': 2e9}
        
        # Test
        result = screener.screen_by_criteria('Healthcare', criteria)
        
        # Assertions
        assert result == []

    def test_screen_by_criteria_sorting(self, screener, mock_fundamentals_data):
        # Setup mock to return multiple candidates
        screener.screen_sector = Mock(return_value=['SMALL1', 'SMALL2'])
        screener.analyzer.get_fundamentals = Mock(side_effect=lambda s:
            next((d for d in mock_fundamentals_data if d['symbol'] == s), {}))
        
        criteria = {
            'max_market_cap': 2e9,
            'min_revenue': 0,
            'max_pe_ratio': 25,
            'min_roe': 0.1,
            'max_debt_equity': 0.5
        }
        
        # Test
        result = screener.screen_by_criteria('Healthcare', criteria)
        
        # Assertions
        assert len(result) >= 2
        # Check that results are sorted by score (descending)
        for i in range(len(result) - 1):
            assert result[i]['score'] >= result[i + 1]['score']

    def test_screen_sector_with_analyzer_errors(self, screener):
        # Setup mock to simulate analyzer errors
        screener._get_sample_symbols_by_sector = Mock(return_value=['INVALID1', 'INVALID2'])
        screener.analyzer.get_fundamentals = Mock(return_value={})  # Empty result
        
        # Test
        result = screener.screen_sector('Healthcare')
        
        # Assertions
        assert result == []  # Should handle errors gracefully

    def test_meets_criteria_with_missing_fields(self, screener):
        # Test criteria checking with missing fundamental fields
        fundamentals = {
            'market_cap': 1e9,
            # Missing other fields
        }
        
        criteria = {
            'max_market_cap': 2e9,
            'min_revenue': 100e6,
            'max_pe_ratio': 15,
            'min_roe': 0.10,
            'max_debt_equity': 0.5
        }
        
        # Test
        result = screener._meets_criteria(fundamentals, criteria)
        
        # Assertions
        assert result == False  # Should fail when required data is missing

    def test_criteria_edge_cases(self, screener):
        # Test edge cases in criteria checking
        fundamentals = {
            'market_cap': 2e9,      # Exactly at limit
            'revenue': 100e6,       # Exactly at limit
            'pe_ratio': 15.0,       # Exactly at limit
            'roe': 0.10,           # Exactly at limit
            'debt_to_equity': 0.5   # Exactly at limit
        }
        
        criteria = {
            'max_market_cap': 2e9,
            'min_revenue': 100e6,
            'max_pe_ratio': 15,
            'min_roe': 0.10,
            'max_debt_equity': 0.5
        }
        
        # Test
        result = screener._meets_criteria(fundamentals, criteria)
        
        # Assertions
        assert result == True  # Should pass when exactly meeting criteria

    def test_score_calculation_components(self, screener):
        # Test individual components of score calculation
        
        # Test ROE component
        fundamentals = {'roe': 0.25, 'pe_ratio': 15, 'profit_margin': 0.1, 
                       'revenue_growth': 0, 'debt_to_equity': 0}
        score = screener._calculate_score(fundamentals, {})
        assert score >= 25  # ROE contributes 25 points
        
        # Test P/E component  
        fundamentals = {'roe': 0, 'pe_ratio': 10, 'profit_margin': 0.1, 
                       'revenue_growth': 0, 'debt_to_equity': 0}
        score = screener._calculate_score(fundamentals, {})
        assert score >= 20  # P/E contributes (20-10)*2 = 20 points
        
        # Test debt penalty
        fundamentals = {'roe': 0, 'pe_ratio': 15, 'profit_margin': 0.1, 
                       'revenue_growth': 0, 'debt_to_equity': 2.0}
        score = screener._calculate_score(fundamentals,