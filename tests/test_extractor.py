import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.data_extractor import DataExtractor


class TestDataExtractor:
    
    @pytest.fixture
    def extractor(self):
        return DataExtractor()
    
    @pytest.fixture
    def mock_ticker_data(self):
        return {
            'info': {
                'marketCap': 2000000000,
                'trailingPE': 15.5,
                'forwardPE': 14.2,
                'priceToBook': 2.1,
                'sector': 'Technology',
                'industry': 'Software',
                'shortName': 'Apple Inc.'
            },
            'history': pd.DataFrame({
                'Close': [150.0, 152.0, 148.0, 151.0, 153.0],
                'Volume': [1000000, 1100000, 950000, 1050000, 1200000]
            }),
            'financials': pd.DataFrame({
                '2023-12-31': [1000000000, 150000000],
                '2022-12-31': [900000000, 135000000]
            }, index=['Total Revenue', 'Net Income']),
            'balance_sheet': pd.DataFrame({
                '2023-12-31': [2000000000, 800000000],
                '2022-12-31': [1800000000, 720000000]
            }, index=['Total Assets', 'Total Liab'])
        }

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_stock_data_success(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_ticker_data['info']
        mock_ticker_instance.history.return_value = mock_ticker_data['history']
        mock_ticker_instance.financials = mock_ticker_data['financials']
        mock_ticker_instance.balance_sheet = mock_ticker_data['balance_sheet']
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = extractor.extract_stock_data('AAPL')
        
        # Assertions
        assert result['symbol'] == 'AAPL'
        assert result['market_cap'] == 2000000000
        assert result['pe_ratio'] == 15.5
        assert result['sector'] == 'Technology'
        assert len(result['price_history']) == 5

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_stock_data_api_error(self, mock_ticker, extractor):
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("API connection failed")
        
        # Test
        result = extractor.extract_stock_data('INVALID')
        
        # Assertions
        assert result is None

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_batch_data_success(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock for multiple symbols
        def mock_ticker_side_effect(symbol):
            mock_instance = Mock()
            mock_instance.info = mock_ticker_data['info'].copy()
            mock_instance.info['symbol'] = symbol
            mock_instance.history.return_value = mock_ticker_data['history']
            mock_instance.financials = mock_ticker_data['financials']
            mock_instance.balance_sheet = mock_ticker_data['balance_sheet']
            return mock_instance
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        # Test
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        results = extractor.extract_batch_data(symbols)
        
        # Assertions
        assert len(results) == 3
        assert all('symbol' in result for result in results)
        assert results[0]['symbol'] == 'AAPL'

    def test_extract_batch_data_empty_list(self, extractor):
        # Test with empty symbol list
        results = extractor.extract_batch_data([])
        
        # Assertions
        assert results == []

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_batch_data_partial_failure(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock where some symbols fail
        def mock_ticker_side_effect(symbol):
            if symbol == 'INVALID':
                raise Exception("Invalid symbol")
            
            mock_instance = Mock()
            mock_instance.info = mock_ticker_data['info'].copy()
            mock_instance.info['symbol'] = symbol
            mock_instance.history.return_value = mock_ticker_data['history']
            mock_instance.financials = mock_ticker_data['financials']
            mock_instance.balance_sheet = mock_ticker_data['balance_sheet']
            return mock_instance
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        # Test
        symbols = ['AAPL', 'INVALID', 'GOOGL']
        results = extractor.extract_batch_data(symbols)
        
        # Assertions
        assert len(results) == 2  # Only successful extractions
        assert all(result['symbol'] != 'INVALID' for result in results)

    @patch('src.data_extractor.yf.Ticker')
    def test_get_historical_prices_success(self, mock_ticker, extractor):
        # Setup mock
        mock_ticker_instance = Mock()
        mock_history = pd.DataFrame({
            'Close': [100, 102, 98, 105, 103],
            'Volume': [1000000, 1100000, 950000, 1200000, 1050000]
        }, index=pd.date_range('2023-01-01', periods=5))
        mock_ticker_instance.history.return_value = mock_history
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = extractor.get_historical_prices('AAPL', period='5d')
        
        # Assertions
        assert len(result) == 5
        assert result.iloc[0]['Close'] == 100
        assert 'Volume' in result.columns

    @patch('src.data_extractor.yf.Ticker')
    def test_get_financial_statements_success(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.financials = mock_ticker_data['financials']
        mock_ticker_instance.balance_sheet = mock_ticker_data['balance_sheet']
        mock_ticker_instance.cashflow = pd.DataFrame({
            '2023-12-31': [200000000],
            '2022-12-31': [180000000]
        }, index=['Operating Cash Flow'])
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = extractor.get_financial_statements('AAPL')
        
        # Assertions
        assert 'income_statement' in result
        assert 'balance_sheet' in result
        assert 'cash_flow' in result
        assert len(result['income_statement']) > 0
        assert len(result['balance_sheet']) > 0

    @patch('src.data_extractor.yf.Ticker')
    def test_get_company_info_success(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_ticker_data['info']
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = extractor.get_company_info('AAPL')
        
        # Assertions
        assert result['market_cap'] == 2000000000
        assert result['pe_ratio'] == 15.5
        assert result['sector'] == 'Technology'
        assert result['company_name'] == 'Apple Inc.'

    @patch('src.data_extractor.yf.Ticker')
    def test_get_company_info_missing_fields(self, mock_ticker, extractor):
        # Setup mock with minimal info
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = {'shortName': 'Test Company'}
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = extractor.get_company_info('TEST')
        
        # Assertions
        assert result['market_cap'] == 0  # Default value
        assert result['pe_ratio'] == 0    # Default value
        assert result['sector'] == 'Unknown'  # Default value
        assert result['company_name'] == 'Test Company'

    def test_validate_symbol_valid(self, extractor):
        # Test valid symbols
        assert extractor.validate_symbol('AAPL') == True
        assert extractor.validate_symbol('GOOGL') == True
        assert extractor.validate_symbol('BRK-B') == True

    def test_validate_symbol_invalid(self, extractor):
        # Test invalid symbols
        assert extractor.validate_symbol('') == False
        assert extractor.validate_symbol(None) == False
        assert extractor.validate_symbol('123') == False
        assert extractor.validate_symbol('invalid_symbol_too_long') == False

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_with_retry_success_on_first_try(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock to succeed on first try
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_ticker_data['info']
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        result = extractor.extract_with_retry('AAPL', max_retries=3)
        
        # Assertions
        assert result is not None
        assert mock_ticker.call_count == 1

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_with_retry_success_on_second_try(self, mock_ticker, extractor, mock_ticker_data):
        # Setup mock to fail first, succeed second
        call_count = 0
        def mock_ticker_side_effect(symbol):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary failure")
            
            mock_instance = Mock()
            mock_instance.info = mock_ticker_data['info']
            return mock_instance
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        # Test
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = extractor.extract_with_retry('AAPL', max_retries=3)
        
        # Assertions
        assert result is not None
        assert call_count == 2

    @patch('src.data_extractor.yf.Ticker')
    def test_extract_with_retry_all_attempts_fail(self, mock_ticker, extractor):
        # Setup mock to always fail
        mock_ticker.side_effect = Exception("Persistent failure")
        
        # Test
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = extractor.extract_with_retry('AAPL', max_retries=2)
        
        # Assertions
        assert result is None
        assert mock_ticker.call_count == 2

    def test_format_financial_data_success(self, extractor):
        # Setup test data
        raw_data = {
            'info': {
                'marketCap': 2000000000,
                'trailingPE': 15.5,
                'sector': 'Technology'
            },
            'financials': pd.DataFrame({
                '2023-12-31': [1000000000, 150000000]
            }, index=['Total Revenue', 'Net Income'])
        }
        
        # Test
        result = extractor.format_financial_data('AAPL', raw_data)
        
        # Assertions
        assert result['symbol'] == 'AAPL'
        assert result['market_cap'] == 2000000000
        assert result['pe_ratio'] == 15.5
        assert result['sector'] == 'Technology'

    def test_format_financial_data_missing_data(self, extractor):
        # Setup test data with missing fields
        raw_data = {
            'info': {},
            'financials': pd.DataFrame()
        }
        
        # Test
        result = extractor.format_financial_data('TEST', raw_data)
        
        # Assertions
        assert result['symbol'] == 'TEST'
        assert result['market_cap'] == 0
        assert result['pe_ratio'] == 0
        assert result['sector'] == 'Unknown'

    @patch('src.data_extractor.yf.download')
    def test_bulk_download_success(self, mock_download, extractor):
        # Setup mock
        mock_data = pd.DataFrame({
            'AAPL': [150, 152, 148],
            'GOOGL': [2800, 2850, 2750]
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_download.return_value = mock_data
        
        # Test
        result = extractor.bulk_download(['AAPL', 'GOOGL'], period='5d')
        
        # Assertions
        assert len(result) == 3
        assert 'AAPL' in result.columns
        assert 'GOOGL' in result.columns

    def test_cache_functionality(self, extractor):
        # Test that extractor has cache functionality
        assert hasattr(extractor, 'cache_data')
        assert hasattr(extractor, 'get_cached_data')
        assert hasattr(extractor, 'clear_cache')
        
        # Test cache operations
        test_data = {'symbol': 'TEST', 'data': 'cached_value'}
        extractor.cache_data('TEST', test_data)
        
        cached = extractor.get_cached_data('TEST')
        assert cached == test_data
        
        extractor.clear_cache()
        cached_after_clear = extractor.get_cached_data('TEST')
        assert cached_after_clear is None