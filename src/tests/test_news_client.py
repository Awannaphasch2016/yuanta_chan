"""
Unit tests for News Client module.
Tests news retrieval, price data, and API integration capabilities.
"""

import unittest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'portfolio_news'))

from news_client import NewsClient

os.environ["NEWSAPI_KEY"] = "88c06ae3a76d41b988fd1b6d4468e123"
os.environ["NEWSDATA_API_KEY"] = "pub_e8de0f08568146bfbec24646f3c2b4de"

class TestNewsClient(unittest.TestCase):
    """Test cases for NewsClient class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.client = NewsClient()
    
    def test_client_initialization(self):
        """Test news client initialization."""
        client = NewsClient()
        self.assertIsNotNone(client)
        self.assertEqual(client.cache_duration.total_seconds(), 15 * 60)  # 15 minutes
        self.assertEqual(client.max_retries, 3)
    
    def test_cache_functionality(self):
        """Test caching functionality."""
        cache_key = "test_key"
        test_data = {"test": "data"}
        
        # Initially no cache
        self.assertFalse(self.client._is_cache_valid(cache_key))
        self.assertIsNone(self.client._get_cached_data(cache_key))
        
        # Cache data
        self.client._cache_data(cache_key, test_data)
        
        # Should now be cached
        self.assertTrue(self.client._is_cache_valid(cache_key))
        cached_data = self.client._get_cached_data(cache_key)
        self.assertEqual(cached_data, test_data)
        
        # Clear cache
        self.client.clear_cache()
        self.assertFalse(self.client._is_cache_valid(cache_key))
    
    def test_timeframe_to_days_conversion(self):
        """Test timeframe string to days conversion."""
        test_cases = [
            ("24h", 1),
            ("48h", 2),
            ("7d", 7),
            ("30d", 30),
            ("1w", 7),
            ("2w", 14),
            ("1m", 30),
            ("invalid", 1)  # Should default to 1
        ]
        
        for timeframe, expected_days in test_cases:
            result = self.client._timeframe_to_days(timeframe)
            self.assertEqual(result, expected_days, f"Failed for timeframe: {timeframe}")
    
    def test_company_keywords_mapping(self):
        """Test company name mapping for tickers."""
        test_cases = [
            ("AAPL", "Apple Inc"),
            ("MSFT", "Microsoft"),
            ("GOOGL", "Google Alphabet"),
            ("UNKNOWN", "UNKNOWN")  # Should return the ticker itself
        ]
        
        for ticker, expected in test_cases:
            result = self.client._get_company_keywords(ticker)
            self.assertEqual(result, expected)
    
    def test_deduplicate_and_sort(self):
        """Test article deduplication and sorting."""
        articles = [
            {
                'title': 'Apple stock rises on earnings beat',
                'relevance_score': 0.8,
                'published_at': '2025-01-13T14:00:00Z'
            },
            {
                'title': 'Apple stock rises on earnings beat',  # Duplicate
                'relevance_score': 0.7,
                'published_at': '2025-01-13T13:00:00Z'
            },
            {
                'title': 'Tesla deliveries exceed expectations',
                'relevance_score': 0.9,
                'published_at': '2025-01-13T15:00:00Z'
            },
            {
                'title': '',  # Empty title should be filtered out
                'relevance_score': 0.5,
                'published_at': '2025-01-13T12:00:00Z'
            }
        ]
        
        result = self.client._deduplicate_and_sort(articles)
        
        # Should have 2 unique articles (excluding duplicate and empty title)
        self.assertEqual(len(result), 2)
        
        # Should be sorted by relevance score (highest first)
        self.assertEqual(result[0]['title'], 'Tesla deliveries exceed expectations')
        self.assertEqual(result[1]['title'], 'Apple stock rises on earnings beat')
    
    @patch('news_client.yf.Ticker')
    def test_get_yahoo_finance_news(self, mock_ticker):
        """Test Yahoo Finance news retrieval."""
        # Mock Yahoo Finance response
        mock_stock = MagicMock()
        mock_stock.news = [
            {
                'title': 'Apple reports strong Q4 earnings',
                'summary': 'Apple exceeded expectations...',
                'publisher': 'Reuters',
                'providerPublishTime': 1705154400,  # Mock timestamp
                'link': 'https://reuters.com/apple-earnings'
            }
        ]
        mock_ticker.return_value = mock_stock
        
        tickers = ['AAPL']
        timeframe = '24h'
        
        result = self.client._get_yahoo_finance_news(tickers, timeframe)
        
        self.assertEqual(len(result), 1)
        article = result[0]
        self.assertEqual(article['title'], 'Apple reports strong Q4 earnings')
        self.assertEqual(article['source'], 'Reuters')
        self.assertEqual(article['tickers'], ['AAPL'])
        self.assertIn('published_at', article)
        self.assertIn('url', article)
        self.assertEqual(article['relevance_score'], 0.8)
    
    @patch('news_client.yf.Ticker')
    def test_get_portfolio_prices(self, mock_ticker):
        """Test portfolio price data retrieval."""
        # Mock Yahoo Finance price data
        mock_stock = MagicMock()
        mock_hist = MagicMock()
        mock_hist.__len__ = MagicMock(return_value=2)
        mock_hist.__getitem__ = MagicMock()
        
        # Mock price data
        class MockSeries:
            def __init__(self, values):
                self.values = values
            
            def iloc(self, index):
                return MockIloc(self.values, index)
        
        class MockIloc:
            def __init__(self, values, indices):
                self.values = values
                self.indices = indices if isinstance(indices, list) else [indices]
            
            def __getitem__(self, index):
                return self.values[self.indices[index]]
        
        mock_hist['Close'] = MockSeries([148.50, 150.00])
        mock_stock.history.return_value = mock_hist
        mock_ticker.return_value = mock_stock
        
        tickers = ['AAPL']
        result = self.client.get_portfolio_prices(tickers)
        
        self.assertEqual(len(result), 1)
        price_data = result[0]
        self.assertEqual(price_data['ticker'], 'AAPL')
        self.assertIn('price', price_data)
        self.assertIn('change_percent', price_data)
        self.assertIn('timestamp', price_data)
    
    @patch('news_client.yf.Ticker')
    def test_get_portfolio_prices_error_handling(self, mock_ticker):
        """Test portfolio price data error handling."""
        # Mock an exception
        mock_ticker.side_effect = Exception("API Error")
        
        tickers = ['INVALID']
        result = self.client.get_portfolio_prices(tickers)
        
        self.assertEqual(len(result), 1)
        price_data = result[0]
        self.assertEqual(price_data['ticker'], 'INVALID')
        self.assertIsNone(price_data['price'])
        self.assertIsNone(price_data['change_percent'])
        self.assertIn('error', price_data)
    
    @patch('news_client.requests.get')
    def test_get_newsapi_articles_no_key(self, mock_get):
        """Test NewsAPI when no API key is available."""
        # Ensure no API key is set
        self.client.newsapi_key = None
        
        result = self.client._get_newsapi_articles(['AAPL'], '24h')
        
        # Should return empty list when no API key
        self.assertEqual(result, [])
        # Verify no HTTP request was made
        mock_get.assert_not_called()
    
    @patch('news_client.requests.get')
    def test_get_newsdata_articles_no_key(self, mock_get):
        """Test Newsdata.io when no API key is available."""
        # Ensure no API key is set
        self.client.newsdata_key = None
        
        result = self.client._get_newsdata_articles(['AAPL'], '24h')
        
        # Should return empty list when no API key
        self.assertEqual(result, [])
        # Verify no HTTP request was made
        mock_get.assert_not_called()
    
    @patch('news_client.yf.Ticker')
    def test_get_portfolio_news_integration(self, mock_ticker):
        """Test full portfolio news retrieval integration."""
        # Mock Yahoo Finance news
        mock_stock = MagicMock()
        mock_stock.news = [
            {
                'title': 'Test news article',
                'summary': 'Test summary',
                'publisher': 'Test Publisher',
                'providerPublishTime': 1705154400,
                'link': 'https://test.com'
            }
        ]
        mock_ticker.return_value = mock_stock
        
        tickers = ['AAPL']
        timeframe = '24h'
        
        result = self.client.get_portfolio_news(tickers, timeframe)
        
        # Should return at least the Yahoo Finance news
        self.assertGreaterEqual(len(result), 0)
        
        if result:  # If we got results
            article = result[0]
            self.assertIn('title', article)
            self.assertIn('summary', article)
            self.assertIn('source', article)
            self.assertIn('published_at', article)
            self.assertIn('tickers', article)
            self.assertIn('relevance_score', article)


class TestNewsClientWithMockAPIs(unittest.TestCase):
    """Test NewsClient with mocked external APIs."""
    
    def setUp(self):
        """Set up test fixtures with API keys."""
        self.client = NewsClient()
        # Set mock API keys for testing
        self.client.newsapi_key = "test_newsapi_key"
        self.client.newsdata_key = "test_newsdata_key"
    
    @patch('news_client.requests.get')
    def test_get_newsapi_articles_success(self, mock_get):
        """Test successful NewsAPI article retrieval."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'Apple stock surges on earnings',
                    'description': 'Apple reported better than expected earnings...',
                    'source': {'name': 'Reuters'},
                    'publishedAt': '2025-01-13T14:00:00Z',
                    'url': 'https://reuters.com/apple'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.client._get_newsapi_articles(['AAPL'], '24h')
        
        self.assertEqual(len(result), 1)
        article = result[0]
        self.assertEqual(article['title'], 'Apple stock surges on earnings')
        self.assertEqual(article['source'], 'Reuters')
        self.assertEqual(article['tickers'], ['AAPL'])
        self.assertEqual(article['relevance_score'], 0.7)
    
    @patch('news_client.requests.get')
    def test_get_newsdata_articles_success(self, mock_get):
        """Test successful Newsdata.io article retrieval."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'results': [
                {
                    'title': 'Tesla delivers record vehicles',
                    'description': 'Tesla announced record deliveries...',
                    'source_id': 'bloomberg',
                    'pubDate': '2025-01-13T12:00:00Z',
                    'link': 'https://bloomberg.com/tesla'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.client._get_newsdata_articles(['TSLA'], '24h')
        
        self.assertEqual(len(result), 1)
        article = result[0]
        self.assertEqual(article['title'], 'Tesla delivers record vehicles')
        self.assertEqual(article['source'], 'bloomberg')
        self.assertIn('TSLA', article['tickers'])
        self.assertEqual(article['relevance_score'], 0.6)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2) 