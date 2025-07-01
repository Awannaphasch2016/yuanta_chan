"""
Unit tests for Portfolio News Lambda function.
Tests the news retrieval and price data capabilities.
"""

import unittest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Set environment variables BEFORE importing lambda function
os.environ["NEWSAPI_KEY"] = "88c06ae3a76d41b988fd1b6d4468e123"
os.environ["NEWSDATA_API_KEY"] = "pub_e8de0f08568146bfbec24646f3c2b4de"

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "portfolio_news"))

from lambda_function import PortfolioNewsService, lambda_handler


class TestPortfolioNewsService(unittest.TestCase):
    """Test cases for PortfolioNewsService class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.service = PortfolioNewsService()
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = PortfolioNewsService()
        self.assertIsNotNone(service)
        self.assertEqual(service.supported_timeframes, ["24h", "48h", "7d", "30d"])
    
    def test_error_response_format(self):
        """Test error response format."""
        error_msg = "Test error message"
        result = self.service._error_response(error_msg)
        
        self.assertIn("success", result)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], error_msg)
        self.assertIn("timestamp", result)
    
    def test_client_portfolio_lookup(self):
        """Test client portfolio lookup functionality."""
        # Test valid client
        alice_portfolio = self.service.get_client_portfolio("alice")
        self.assertIsNotNone(alice_portfolio)
        self.assertEqual(alice_portfolio["name"], "Alice Johnson")
        self.assertEqual(alice_portfolio["account_type"], "Growth Portfolio")
        self.assertIn("AAPL", alice_portfolio["tickers"])
        
        # Test case insensitive lookup
        alice_upper = self.service.get_client_portfolio("ALICE")
        self.assertEqual(alice_portfolio, alice_upper)
        
        # Test invalid client
        invalid_client = self.service.get_client_portfolio("nonexistent")
        self.assertIsNone(invalid_client)
        
        # Test default client
        default_client = self.service.get_client_portfolio("default")
        self.assertIsNotNone(default_client)
        self.assertEqual(default_client["name"], "Demo Client")
    
    @patch('lambda_function.news_client')
    def test_portfolio_news_with_client_name(self, mock_news_client):
        """Test portfolio news retrieval using client name."""
        # Mock news client responses
        mock_news_client.get_portfolio_news.return_value = []
        mock_news_client.get_portfolio_prices.return_value = [
            {
                "ticker": "AAPL",
                "price": 150.0,
                "change_percent": 1.5,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        ]
        
        # Test with valid client
        result = self.service.get_portfolio_news_and_prices(client_name="alice")
        
        self.assertTrue(result["success"])
        self.assertIn("client", result)
        self.assertEqual(result["client"]["name"], "Alice Johnson")
        self.assertEqual(result["tickers"], ["AAPL", "MSFT", "GOOGL", "TSLA"])
    
    @patch('lambda_function.news_client')
    def test_portfolio_news_with_unknown_client(self, mock_news_client):
        """Test portfolio news retrieval with unknown client (should use default)."""
        # Mock news client responses
        mock_news_client.get_portfolio_news.return_value = []
        mock_news_client.get_portfolio_prices.return_value = [
            {
                "ticker": "AAPL",
                "price": 150.0,
                "change_percent": 1.5,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        ]
        
        # Test with unknown client
        result = self.service.get_portfolio_news_and_prices(client_name="unknown_client")
        
        self.assertTrue(result["success"])
        self.assertIn("client", result)
        self.assertEqual(result["client"]["name"], "Demo Client")
        self.assertEqual(result["tickers"], ["AAPL", "TSLA", "GOOGL"])


class TestLambdaHandler(unittest.TestCase):
    """Test cases for the Lambda handler function."""
    
    def test_lambda_handler_missing_tickers(self):
        """Test Lambda handler with missing tickers parameter."""
        event = {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioNewsActionGroup",
            "function": "getPortfolioNews",
            "parameters": [
                {"name": "timeframe", "value": "24h"}
            ]
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Verify Bedrock Agent response structure
        self.assertIn("messageVersion", result)
        self.assertIn("response", result)
        self.assertIn("functionResponse", result["response"])
        self.assertIn("responseBody", result["response"]["functionResponse"])
        
        # Parse the response body
        response_body = result["response"]["functionResponse"]["responseBody"]
        body_text = response_body["TEXT"]["body"]
        parsed_body = json.loads(body_text)
        
        self.assertIn("success", parsed_body)
        self.assertFalse(parsed_body["success"])
        self.assertIn("error", parsed_body)
    
    @patch('lambda_function.news_client')
    def test_lambda_handler_with_client_name(self, mock_news_client):
        """Test Lambda handler with client_name parameter."""
        # Mock news client responses
        mock_news_client.get_portfolio_news.return_value = []
        mock_news_client.get_portfolio_prices.return_value = [
            {
                "ticker": "AAPL",
                "price": 150.0,
                "change_percent": 1.5,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        ]
        
        event = {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioNewsActionGroup",
            "function": "getPortfolioNews",
            "parameters": [
                {"name": "client_name", "value": "alice"},
                {"name": "timeframe", "value": "24h"}
            ]
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Verify Bedrock Agent response structure
        self.assertIn("messageVersion", result)
        self.assertIn("response", result)
        
        # Parse the response body
        response_body = result["response"]["functionResponse"]["responseBody"]
        body_text = response_body["TEXT"]["body"]
        parsed_body = json.loads(body_text)
        
        self.assertTrue(parsed_body["success"])
        self.assertIn("client", parsed_body)
        self.assertEqual(parsed_body["client"]["name"], "Alice Johnson")
        self.assertEqual(parsed_body["tickers"], ["AAPL", "MSFT", "GOOGL", "TSLA"])
    
    def test_lambda_handler_direct_invocation_with_client(self):
        """Test Lambda handler with direct invocation using client_name."""
        event = {
            "client_name": "bob",
            "timeframe": "48h"
        }
        context = None
        
        # This will use mock data since we're running locally
        result = lambda_handler(event, context)
        
        # Parse the response body
        response_body = result["response"]["functionResponse"]["responseBody"]
        body_text = response_body["TEXT"]["body"]
        parsed_body = json.loads(body_text)
        
        self.assertTrue(parsed_body["success"])
        self.assertIn("client", parsed_body)
        self.assertEqual(parsed_body["client"]["name"], "Bob Smith")
        self.assertEqual(parsed_body["tickers"], ["XOM", "CVX", "JPM", "BAC", "WMT"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
