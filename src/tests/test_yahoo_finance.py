"""
Test script for Yahoo Finance client to verify integration
Tests basic functionality and error handling
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.yahoo_finance_client import YahooFinanceClient
from common.logger import get_logger


def test_yahoo_finance_integration():
    """Test Yahoo Finance client integration"""
    logger = get_logger("TestYahooFinance")
    
    # Initialize client
    client = YahooFinanceClient()
    logger.info("Yahoo Finance client initialized successfully")
    assert client is not None, "Failed to initialize Yahoo Finance client"
    
    # Test with a well-known ticker
    test_ticker = "AAPL"
    logger.info(f"Testing with ticker: {test_ticker}")
    
    # Test ticker validation
    is_valid = client.validate_ticker(test_ticker)
    logger.info(f"Ticker validation for {test_ticker}: {is_valid}")
    assert is_valid, f"Valid ticker {test_ticker} should be validated successfully"
    
    # Test stock info retrieval
    stock_info = client.get_stock_info(test_ticker)
    logger.info(f"Stock info retrieved for {test_ticker}")
    assert stock_info is not None, "Stock info should not be None"
    assert isinstance(stock_info, dict), "Stock info should be a dictionary"
    
    # Check for some basic info
    logger.info(f"Company name: {stock_info.get('name')}")
    logger.info(f"Current price: {stock_info.get('currentPrice')}")
    logger.info(f"Forward P/E: {stock_info.get('forwardPE')}")
    logger.info(f"ROE: {stock_info.get('returnOnEquity')}")
    
    # Test earnings data retrieval (optional, as it may not always be available)
    try:
        earnings_data = client.get_earnings_data(test_ticker)
        logger.info(f"Earnings data retrieved for {test_ticker}")
        if earnings_data is not None:
            assert isinstance(earnings_data, (dict, list)), "Earnings data should be dict or list"
    except Exception as e:
        logger.warning(f"Earnings data retrieval failed: {str(e)}")
        # This is expected for some tickers, so we don't fail the test
    
    # Test invalid ticker
    invalid_ticker = "INVALID_TICKER_123"
    is_invalid_valid = client.validate_ticker(invalid_ticker)
    logger.info(f"Ticker validation for {invalid_ticker}: {is_invalid_valid}")
    assert not is_invalid_valid, f"Invalid ticker {invalid_ticker} should not be validated"
    
    logger.info("Yahoo Finance integration test completed successfully")


if __name__ == "__main__":
    test_yahoo_finance_integration()
    print("All tests passed!") 