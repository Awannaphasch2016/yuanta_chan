"""
Integration tests for Portfolio News Lambda function.
Tests end-to-end functionality including external API integration.
"""

import sys
import os
import json
from datetime import datetime

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'portfolio_news'))

from lambda_function import lambda_handler, PortfolioNewsService
from news_client import NewsClient
from logger import get_logger


def test_portfolio_news_integration():
    """Test portfolio news integration with real functionality."""
    logger = get_logger("TestPortfolioNewsIntegration")
    
    # Test data
    test_tickers = ["AAPL", "TSLA", "MSFT"]
    timeframe = "24h"
    
    logger.info("Starting Portfolio News integration test")
    logger.info(f"Testing with tickers: {test_tickers}")
    logger.info(f"Timeframe: {timeframe}")
    
    # Test 1: Direct service test
    logger.info("--- Test 1: Direct PortfolioNewsService test ---")
    service = PortfolioNewsService()
    
    try:
        result = service.get_portfolio_news_and_prices(test_tickers, timeframe)
        
        # Verify result structure
        assert "success" in result, "Result should have 'success' field"
        assert "tickers" in result, "Result should have 'tickers' field"
        assert "news" in result, "Result should have 'news' field"
        assert "prices" in result, "Result should have 'prices' field"
        assert "summary" in result, "Result should have 'summary' field"
        
        if result["success"]:
            logger.info(f"✅ Service test successful")
            logger.info(f"Retrieved {len(result['news'])} news articles")
            logger.info(f"Retrieved {len(result['prices'])} price quotes")
            
            # Log some sample data
            if result['news']:
                sample_news = result['news'][0]
                logger.info(f"Sample news: {sample_news.get('title', 'No title')[:50]}...")
            
            if result['prices']:
                sample_price = result['prices'][0]
                logger.info(f"Sample price: {sample_price.get('ticker')} = ${sample_price.get('price', 'N/A')}")
        else:
            logger.warning(f"Service test failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Service test failed with exception: {str(e)}")
        raise
    
    # Test 2: Lambda handler with Bedrock Agent format
    logger.info("--- Test 2: Lambda handler (Bedrock Agent format) ---")
    bedrock_event = {
        "messageVersion": "1.0",
        "actionGroup": "PortfolioNewsActionGroup",
        "function": "getPortfolioNews",
        "parameters": [
            {"name": "tickers", "value": test_tickers},
            {"name": "timeframe", "value": timeframe}
        ],
        "sessionId": "test-session-123",
        "invocationId": "test-invocation-123",
        "requestId": "test-req-001"
    }
    
    try:
        lambda_result = lambda_handler(bedrock_event, None)
        
        # Verify Bedrock Agent response structure
        assert "messageVersion" in lambda_result, "Should have messageVersion"
        assert "response" in lambda_result, "Should have response"
        assert "functionResponse" in lambda_result["response"], "Should have functionResponse"
        
        response_body = lambda_result["response"]["functionResponse"]["responseBody"]
        assert "TEXT" in response_body, "Should have TEXT response body"
        assert "body" in response_body["TEXT"], "Should have body in TEXT"
        
        # Parse the JSON response
        parsed_result = json.loads(response_body["TEXT"]["body"])
        
        if parsed_result.get("success"):
            logger.info("✅ Lambda handler (Bedrock format) test successful")
            logger.info(f"Tickers processed: {parsed_result.get('tickers', [])}")
        else:
            logger.warning(f"Lambda handler test failed: {parsed_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Lambda handler test failed with exception: {str(e)}")
        raise
    
    # Test 3: Lambda handler with direct format
    logger.info("--- Test 3: Lambda handler (Direct format) ---")
    direct_event = {
        "tickers": test_tickers,
        "timeframe": timeframe,
        "requestId": "test-req-002"
    }
    
    try:
        lambda_result = lambda_handler(direct_event, None)
        
        response_body = lambda_result["response"]["functionResponse"]["responseBody"]
        parsed_result = json.loads(response_body["TEXT"]["body"])
        
        if parsed_result.get("success"):
            logger.info("✅ Lambda handler (Direct format) test successful")
        else:
            logger.warning(f"Direct format test failed: {parsed_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Direct format test failed with exception: {str(e)}")
        raise
    
    # Test 4: String tickers format
    logger.info("--- Test 4: String tickers format ---")
    string_event = {
        "messageVersion": "1.0",
        "actionGroup": "PortfolioNewsActionGroup",
        "function": "getPortfolioNews",
        "parameters": [
            {"name": "tickers", "value": "AAPL,MSFT"},
            {"name": "timeframe", "value": "48h"}
        ]
    }
    
    try:
        lambda_result = lambda_handler(string_event, None)
        response_body = lambda_result["response"]["functionResponse"]["responseBody"]
        parsed_result = json.loads(response_body["TEXT"]["body"])
        
        if parsed_result.get("success"):
            logger.info("✅ String tickers format test successful")
            expected_tickers = ["AAPL", "MSFT"]
            actual_tickers = parsed_result.get("tickers", [])
            assert actual_tickers == expected_tickers, f"Expected {expected_tickers}, got {actual_tickers}"
        else:
            logger.warning(f"String tickers test failed: {parsed_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"String tickers test failed with exception: {str(e)}")
        raise
    
    # Test 5: Error handling
    logger.info("--- Test 5: Error handling test ---")
    error_event = {
        "messageVersion": "1.0",
        "actionGroup": "PortfolioNewsActionGroup",
        "function": "getPortfolioNews",
        "parameters": [
            {"name": "timeframe", "value": "24h"}
            # Intentionally missing tickers
        ]
    }
    
    try:
        lambda_result = lambda_handler(error_event, None)
        response_body = lambda_result["response"]["functionResponse"]["responseBody"]
        parsed_result = json.loads(response_body["TEXT"]["body"])
        
        # Should get an error response
        assert not parsed_result.get("success", True), "Should return error for missing tickers"
        assert "error" in parsed_result, "Should have error message"
        logger.info("✅ Error handling test successful")
        logger.info(f"Error message: {parsed_result.get('error', 'No error message')}")
    
    except Exception as e:
        logger.error(f"Error handling test failed with exception: {str(e)}")
        raise
    
    logger.info("All integration tests completed successfully! 🎉")


def test_news_client_standalone():
    """Test NewsClient standalone functionality."""
    logger = get_logger("TestNewsClientStandalone")
    
    logger.info("Starting NewsClient standalone test")
    
    # Initialize client
    client = NewsClient()
    logger.info("NewsClient initialized successfully")
    
    # Test portfolio news retrieval
    test_tickers = ["AAPL"]
    timeframe = "24h"
    
    try:
        news_articles = client.get_portfolio_news(test_tickers, timeframe)
        logger.info(f"Retrieved {len(news_articles)} news articles")
        
        if news_articles:
            sample_article = news_articles[0]
            logger.info(f"Sample article title: {sample_article.get('title', 'No title')[:50]}...")
            logger.info(f"Sample article source: {sample_article.get('source', 'No source')}")
        
        # Test price data retrieval
        price_data = client.get_portfolio_prices(test_tickers)
        logger.info(f"Retrieved {len(price_data)} price quotes")
        
        if price_data:
            sample_price = price_data[0]
            logger.info(f"Sample price: {sample_price.get('ticker')} = ${sample_price.get('price', 'N/A')}")
            logger.info(f"Change: {sample_price.get('change_percent', 'N/A')}%")
        
        logger.info("✅ NewsClient standalone test successful")
    
    except Exception as e:
        logger.error(f"NewsClient standalone test failed: {str(e)}")
        raise


def run_performance_test():
    """Run a performance test with multiple tickers."""
    logger = get_logger("TestPortfolioNewsPerformance")
    
    logger.info("Starting performance test")
    
    # Test with larger portfolio
    large_portfolio = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "JNJ"]
    
    start_time = datetime.now()
    
    service = PortfolioNewsService()
    result = service.get_portfolio_news_and_prices(large_portfolio, "24h")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Performance test completed in {duration:.2f} seconds")
    
    if result.get("success"):
        logger.info(f"Processed {len(large_portfolio)} tickers")
        logger.info(f"Retrieved {len(result.get('news', []))} news articles")
        logger.info(f"Retrieved {len(result.get('prices', []))} price quotes")
        
        # Calculate performance metrics
        tickers_per_second = len(large_portfolio) / duration if duration > 0 else 0
        logger.info(f"Performance: {tickers_per_second:.2f} tickers per second")
        
        if duration < 10:  # Should complete within 10 seconds
            logger.info("✅ Performance test passed (< 10 seconds)")
        else:
            logger.warning(f"⚠️ Performance test slow ({duration:.2f} seconds)")
    else:
        logger.error(f"Performance test failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    try:
        print("Portfolio News Lambda - Integration Tests")
        print("=" * 50)
        
        # Run main integration test
        test_portfolio_news_integration()
        print("\n" + "=" * 50)
        
        # Run standalone client test
        test_news_client_standalone()
        print("\n" + "=" * 50)
        
        # Run performance test
        run_performance_test()
        print("\n" + "=" * 50)
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Tests failed: {str(e)}")
        sys.exit(1) 