"""
Unit tests for Financial Data Lambda function.
Tests the various data retrieval and processing capabilities.
"""

import unittest
import json
import sys
import os
from datetime import datetime

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'financial_data'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from lambda_function import FinancialDataService, lambda_handler

class TestFinancialDataService(unittest.TestCase):
    """Test cases for FinancialDataService class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.service = FinancialDataService()
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = FinancialDataService()
        self.assertIsNotNone(service)
    
    def test_get_financial_data_basic(self):
        """Test basic financial data retrieval."""
        result = self.service.get_financial_data("AAPL", "overview")
        
        # Verify result structure
        self.assertIn("ticker", result)
        self.assertEqual(result["ticker"], "AAPL")
        self.assertIn("data_type", result)
        self.assertEqual(result["data_type"], "overview")
        self.assertIn("timestamp", result)


class TestLambdaHandler(unittest.TestCase):
    """Test cases for the Lambda handler function."""
    
    def test_lambda_handler_missing_ticker(self):
        """Test Lambda handler with missing ticker parameter."""
        event = {"data_type": "overview"}
        context = None
        
        result = lambda_handler(event, context)
        
        # Verify error response
        self.assertEqual(result["statusCode"], 400)
        body = json.loads(result["body"])
        self.assertIn("error", body)
    
    def test_lambda_handler_basic_success(self):
        """Test Lambda handler with valid parameters."""
        event = {"ticker": "AAPL", "data_type": "overview"}
        context = None
        
        result = lambda_handler(event, context)
        
        # Should return 200 status
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("body", result)


if __name__ == '__main__':
    unittest.main(verbosity=2) 