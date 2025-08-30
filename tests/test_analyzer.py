import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.analyzer import FundamentalsAnalyzer


class TestFundamentalsAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return FundamentalsAnalyzer()
    
    @pytest.fixture
    def mock_ticker_info(self):
        return {
            'marketCap': 2000000000,
            'trailingPE': 15.5,
            'forwardPE': 14.2,
            'priceToBook': 2.1,
            'priceToSalesTrailing12Months': 3.2,
            'profitMargins': 0.15,
            'operatingMargins': 0.20,
            'returnOnEquity': 0.18,
            'debtToEquity': 0.45,
            'currentRatio': 1.8,
            'sector': 'Technology',
            'industry': 'Software'
        }
    
    @pytest.fixture
    def mock_financials(self):
        data = {
            'Total Revenue': [1000000000, 900000000, 800000000],
            'Net Income': [150000000, 135000000, 120000000]
        }
        return pd.DataFrame(data, index=['Total Revenue', 'Net Income'])
    
    @pytest.fixture
    def mock_balance_sheet(self):
        data = {
            'Total Assets': [2000000000, 1800000000, 1600000000],
            'Total Liab': [800000000, 720000000, 640000000]
        }
        return pd.DataFrame(data, index=['Total Assets', 'Total Liab'])

    @patch('src.analyzer.yf.Ticker')
    def test_get_fundamentals_success(self, mock_ticker, analyzer, mock_ticker_info, 
                                    mock_financials, mock_balance_sheet):
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_ticker_info
        mock_ticker_instance.financials = mock_financials
        mock_ticker_instance.balance_sheet = mock_balance_sheet
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = analyzer.get_fundamentals('AAPL')
        
        # Assertions
        assert result['symbol'] == 'AAPL'
        assert result['market_cap'] == 2000000000
        assert result['pe_ratio'] == 15.5
        assert result['sector'] == 'Technology'
        assert result['revenue'] == 1000000000
        assert abs(result['revenue_growth'] - 11.11) < 0.1  # Approximate growth calculation

    @patch('src.analyzer.yf.Ticker')
    def test_get_fundamentals_api_error(self, mock_ticker, analyzer):
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("API Error")
        
        # Test
        result = analyzer.get_fundamentals('INVALID')
        
        # Assertions
        assert result == {}

    def test_analyze_companies_multiple_symbols(self, analyzer):
        # Mock the get_fundamentals method
        analyzer.get_fundamentals = Mock(side_effect=[
            {'symbol': 'AAPL', 'pe_ratio': 15.5, 'roe': 0.18},
            {'symbol': 'GOOGL', 'pe_ratio': 22.1, 'roe': 0.16},
            {}  # Empty result for third symbol
        ])
        
        # Test
        result = analyzer.analyze_companies(['AAPL', 'GOOGL', 'INVALID'])
        
        # Assertions
        assert len(result) == 2
        assert result.iloc[0]['symbol'] == 'AAPL'
        assert result.iloc[1]['symbol'] == 'GOOGL'

    def test_compare_companies_success(self, analyzer):
        # Setup mock data
        mock_df = pd.DataFrame([
            {'symbol': 'AAPL', 'pe_ratio': 15.5, 'roe': 0.18, 'revenue_growth': 10, 'profit_margin': 0.15},
            {'symbol': 'GOOGL', 'pe_ratio': 22.1, 'roe': 0.16, 'revenue_growth': 8, 'profit_margin': 0.20},
            {'symbol': 'MSFT', 'pe_ratio': 18.2, 'roe': 0.22, 'revenue_growth': 12, 'profit_margin': 0.18}
        ])
        
        analyzer.analyze_companies = Mock(return_value=mock_df)
        
        # Test
        result = analyzer.compare_companies(['AAPL', 'GOOGL', 'MSFT'])
        
        # Assertions
        assert 'summary' in result
        assert 'rankings' in result
        assert 'lowest_pe' in result['rankings']
        assert 'highest_roe' in result['rankings']

    def test_create_sector_comparison_success(self, analyzer):
        # Setup mock data
        mock_df = pd.DataFrame([
            {'symbol': 'AAPL', 'sector': 'Technology', 'pe_ratio': 15.5, 'roe': 0.18, 'profit_margin': 0.15, 'market_cap': 2e12},
            {'symbol': 'GOOGL', 'sector': 'Technology', 'pe_ratio': 22.1, 'roe': 0.16, 'profit_margin': 0.20, 'market_cap': 1.5e12},
            {'symbol': 'JNJ', 'sector': 'Healthcare', 'pe_ratio': 14.2, 'roe': 0.14, 'profit_margin': 0.18, 'market_cap': 400e9}
        ])
        
        # Test
        result = analyzer.create_sector_comparison(mock_df, 'Technology')
        
        # Assertions
        assert result['sector'] == 'Technology'
        assert result['company_count'] == 2
        assert 'avg_pe_ratio' in result
        assert 'top_performers' in result

    def test_create_sector_comparison_no_data(self, analyzer):
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        
        result = analyzer.create_sector_comparison(empty_df, 'Technology')
        
        # Assertions
        assert 'error' in result

    def test_get_latest_value_success(self, analyzer):
        # Setup test data
        df = pd.DataFrame({
            'col1': [100, 90, 80],
            'col2': [200, 180, 160]
        }, index=['Total Revenue', 'Net Income', 'Other'])
        
        # Test
        result = analyzer._get_latest_value(df, 'Total Revenue')
        
        # Assertions
        assert result == 100.0

    def test_get_latest_value_missing_column(self, analyzer):
        # Setup test data
        df = pd.DataFrame({'col1': [100, 90, 80]})
        
        # Test
        result = analyzer._get_latest_value(df, 'Missing Column')
        
        # Assertions
        assert result == 0.0

    def test_calculate_growth_rate_success(self, analyzer):
        # Setup test data
        df = pd.DataFrame({
            'col1': [110, 100, 90],
            'col2': [220, 200, 180]
        }, index=['Total Revenue', 'Net Income', 'Other'])
        
        # Test
        result = analyzer._calculate_growth_rate(df, 'Total Revenue')
        
        # Assertions
        assert result == 10.0  # (110-100)/100 * 100

    def test_calculate_growth_rate_division_by_zero(self, analyzer):
        # Setup test data with zero previous value
        df = pd.DataFrame({
            'col1': [100, 0, 90]
        }, index=['Total Revenue', 'Net Income', 'Other'])
        
        # Test
        result = analyzer._calculate_growth_rate(df, 'Total Revenue')
        
        # Assertions
        assert result == 0.0

    def test_legacy_analyze_stock(self, analyzer):
        # Test legacy method
        stock_data = {
            'revenue': 1000000,
            'net_income': 150000,
            'assets': 2000000,
            'liabilities': 800000
        }
        
        result = analyzer.analyze_stock(stock_data)
        
        # Assertions
        assert result['profit_margin'] == 0.15
        assert result['debt_to_equity'] == 0.8 / 1.2  # 800000 / (2000000 - 800000)

    def test_legacy_calculate_price_to_earnings(self, analyzer):
        # Test legacy method
        stock_data = {
            'price': 150.0,
            'earnings_per_share': 10.0
        }
        
        result = analyzer.calculate_price_to_earnings(stock_data)
        
        # Assertions
        assert result == 15.0

    def test_legacy_calculate_debt_to_equity(self, analyzer):
        # Test legacy method
        stock_data = {
            'total_liabilities': 800000,
            'shareholder_equity': 1000000
        }
        
        result = analyzer.calculate_debt_to_equity(stock_data)
        
        # Assertions
        assert result == 0.8

    def test_data_cache_functionality(self, analyzer):
        # Mock get_fundamentals to use cache
        with patch('src.analyzer.yf.Ticker') as mock_ticker:
            mock_ticker_instance = Mock()
            mock_ticker_instance.info = {'marketCap': 1000000}
            mock_ticker_instance.financials = pd.DataFrame()
            mock_ticker_instance.balance_sheet = pd.DataFrame()
            mock_ticker.return_value = mock_ticker_instance
            
            # First call should hit the API
            result1 = analyzer.get_fundamentals('TEST')
            
            # Second call should use cache
            result2 = analyzer.get_fundamentals('TEST')
            
            # Assertions
            assert result1 == result2
            assert mock_ticker.call_count == 1  # Only called once due to caching

    def test_analyze_companies_empty_list(self, analyzer):
        # Test with empty symbol list
        result = analyzer.analyze_companies([])
        
        # Assertions
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_compare_companies_empty_dataframe(self, analyzer):
        # Mock analyze_companies to return empty DataFrame
        analyzer.analyze_companies = Mock(return_value=pd.DataFrame())
        
        result = analyzer.compare_companies(['INVALID'])
        
        # Assertions
        assert result == {}