import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import time  # Import time for generating request IDs

# Import local modules
from logger import get_logger
from news_client import news_client


class PortfolioNewsService:
    """
    Service for retrieving portfolio-related news and price data.
    Supports news headlines and current price information for multiple tickers.
    """
    
    def __init__(self):
        self.logger = get_logger("PortfolioNewsLambda")
        self.supported_timeframes = ['24h', '48h', '7d', '30d']
        
        # Mock client portfolio database
        self.mock_client_portfolios = {
            'alice': {
                'name': 'Alice Johnson',
                'tickers': ['AAPL', 'MSFT', 'GOOGL', 'TSLA'],
                'account_type': 'Growth Portfolio',
                'last_updated': '2025-01-13'
            },
            'bob': {
                'name': 'Bob Smith',
                'tickers': ['XOM', 'CVX', 'JPM', 'BAC', 'WMT'],
                'account_type': 'Conservative Portfolio',
                'last_updated': '2025-01-12'
            },
            'charlie': {
                'name': 'Charlie Davis',
                'tickers': ['NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO'],
                'account_type': 'Tech Portfolio',
                'last_updated': '2025-01-13'
            },
            'diana': {
                'name': 'Diana Wilson',
                'tickers': ['SPY', 'QQQ', 'VTI', 'VXUS', 'BND'],
                'account_type': 'Diversified ETF Portfolio',
                'last_updated': '2025-01-11'
            },
            'default': {
                'name': 'Demo Client',
                'tickers': ['AAPL', 'TSLA', 'GOOGL'],
                'account_type': 'Demo Portfolio',
                'last_updated': '2025-01-13'
            }
                 }
    
    def get_client_portfolio(self, client_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve mock client portfolio data by client name
        
        Args:
            client_name: Client identifier (case-insensitive)
            
        Returns:
            Dictionary containing client portfolio information or None if not found
        """
        client_key = client_name.lower().strip() if client_name else 'default'
        return self.mock_client_portfolios.get(client_key)
    
    def get_portfolio_news_and_prices(self, tickers: List[str] = None, timeframe: str = '24h', client_name: str = None) -> Dict[str, Any]:
        """
        Retrieve news headlines and price data for a portfolio of tickers
        
        Args:
            tickers: List of stock ticker symbols (optional if client_name provided)
            timeframe: Time range for news (24h, 48h, 7d, 30d)
            client_name: Client identifier to lookup portfolio (optional)
            
        Returns:
            Dictionary containing news articles and price data
        """
        try:
            client_info = None
            
            # If client_name is provided, try to get their portfolio
            if client_name:
                client_info = self.get_client_portfolio(client_name)
                if client_info:
                    tickers = client_info['tickers']
                    self.logger.info(f"Retrieved portfolio for client '{client_info['name']}': {tickers}")
                else:
                    self.logger.warning(f"Client '{client_name}' not found, using default portfolio")
                    # Fall back to default portfolio if client not found
                    client_info = self.get_client_portfolio('default')
                    if client_info:
                        tickers = client_info['tickers']
                        self.logger.info(f"Using default portfolio: {tickers}")
            
            # Validate inputs
            if not tickers or not isinstance(tickers, list):
                return self._error_response("Tickers list is required and must be a non-empty array. Provide either 'tickers' parameter or a valid 'client_name'.")
            
            # Clean and validate tickers
            valid_tickers = [ticker.upper().strip() for ticker in tickers if ticker and isinstance(ticker, str)]
            if not valid_tickers:
                return self._error_response("No valid ticker symbols provided")
            
            # Validate timeframe
            if timeframe not in self.supported_timeframes:
                self.logger.warning(f"Unsupported timeframe: {timeframe}, using default 24h")
                timeframe = '24h'
            
            self.logger.info(f"Retrieving portfolio data for {len(valid_tickers)} tickers: {valid_tickers}")
            
            # Get news and price data concurrently
            news_articles = self._get_news_data(valid_tickers, timeframe)
            price_data = self._get_price_data(valid_tickers)
            
            # Prepare successful response
            result = {
                'success': True,
                'tickers': valid_tickers,
                'timeframe': timeframe,
                'news': news_articles,
                'prices': price_data,
                'summary': self._generate_summary(news_articles, price_data),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add client information if available
            if client_info:
                result['client'] = {
                    'name': client_info['name'],
                    'account_type': client_info['account_type'],
                    'last_updated': client_info['last_updated']
                }
            
            self.logger.info(f"Successfully retrieved portfolio data: {len(news_articles)} news articles, {len(price_data)} price quotes")
            return result
            
        except Exception as e:
            self.logger.error(f"Portfolio data retrieval failed for tickers {tickers}", error=e)
            return self._error_response(f"Data retrieval failed: {str(e)}")
    
    def _get_news_data(self, tickers: List[str], timeframe: str) -> List[Dict[str, Any]]:
        """Get news articles for the portfolio tickers"""
        try:
            articles = news_client.get_portfolio_news(tickers, timeframe)
            
            # Filter and enhance articles
            processed_articles = []
            for article in articles:
                # Ensure all required fields are present
                processed_article = {
                    'title': article.get('title', 'No title available'),
                    'summary': article.get('summary', article.get('description', 'No summary available')),
                    'source': article.get('source', 'Unknown'),
                    'published_at': article.get('published_at', datetime.now().isoformat() + 'Z'),
                    'tickers': article.get('tickers', []),
                    'url': article.get('url', ''),
                    'relevance_score': article.get('relevance_score', 0.5)
                }
                processed_articles.append(processed_article)
            
            return processed_articles
            
        except Exception as e:
            self.logger.error("Failed to retrieve news data", error=e)
            return []
    
    def _get_price_data(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Get current price data for the portfolio tickers"""
        try:
            return news_client.get_portfolio_prices(tickers)
        except Exception as e:
            self.logger.error("Failed to retrieve price data", error=e)
            return [{'ticker': ticker, 'price': None, 'change_percent': None, 
                    'timestamp': datetime.now().isoformat() + 'Z', 'error': str(e)} 
                   for ticker in tickers]
    
    def _generate_summary(self, news_articles: List[Dict[str, Any]], 
                         price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of the portfolio news and price changes"""
        try:
            # Count news by source
            news_sources = {}
            for article in news_articles:
                source = article.get('source', 'Unknown')
                news_sources[source] = news_sources.get(source, 0) + 1
            
            # Calculate price change statistics
            price_changes = [p.get('change_percent', 0) for p in price_data 
                           if p.get('change_percent') is not None]
            
            avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
            positive_changes = sum(1 for change in price_changes if change > 0)
            negative_changes = sum(1 for change in price_changes if change < 0)
            
            summary = {
                'total_news_articles': len(news_articles),
                'news_sources': news_sources,
                'total_tickers': len(price_data),
                'price_summary': {
                    'average_change_percent': round(avg_change, 2),
                    'tickers_up': positive_changes,
                    'tickers_down': negative_changes,
                    'tickers_unchanged': len(price_changes) - positive_changes - negative_changes
                },
                'top_news_topics': self._extract_top_topics(news_articles)
            }
            
            return summary
            
        except Exception as e:
            self.logger.warning("Failed to generate summary", error=e)
            return {'summary_available': False, 'error': str(e)}
    
    def _extract_top_topics(self, news_articles: List[Dict[str, Any]]) -> List[str]:
        """Extract common topics/keywords from news articles"""
        try:
            # Simple keyword extraction from titles
            keywords = {}
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}
            
            for article in news_articles:
                title = article.get('title', '').lower()
                words = [word.strip('.,!?:;()[]{}"\'-') for word in title.split()]
                for word in words:
                    if len(word) > 3 and word not in common_words and word.isalpha():
                        keywords[word] = keywords.get(word, 0) + 1
            
            # Return top 5 keywords
            top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
            return [keyword for keyword, count in top_keywords]
            
        except Exception as e:
            self.logger.warning("Failed to extract topics", error=e)
            return []
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler for portfolio news requests,
    optimized for Amazon Bedrock Agent integration.
    """
    logger = get_logger("PortfolioNewsHandler")
    print(f"DEBUG: Full event received by Lambda: {json.dumps(event, indent=2)}")

    # Extract Bedrock Agent specific metadata
    actionGroup = event.get('actionGroup', 'PortfolioNewsActionGroup')
    function = event.get('function', 'getPortfolioNews')
    messageVersion = event.get('messageVersion', '1.0')

    try:
        tickers = []
        timeframe = '24h'  # Default timeframe
        client_name = None
        request_id = event.get('requestId', f'req-{int(time.time())}')

        # 1. Try to extract 'tickers' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'tickers' and param.get('value') is not None:
                    param_value = param['value']
                    
                    # Handle different input formats
                    if isinstance(param_value, str):
                        # Parse JSON string or comma-separated list
                        try:
                            if param_value.startswith('[') and param_value.endswith(']'):
                                tickers = json.loads(param_value)
                            else:
                                tickers = [ticker.strip() for ticker in param_value.split(',')]
                        except json.JSONDecodeError:
                            tickers = [ticker.strip() for ticker in param_value.split(',')]
                    elif isinstance(param_value, list):
                        tickers = param_value
                    break
        
        # 2. If 'tickers' is still not found, try to extract from direct key
        if not tickers and event.get('tickers') is not None:
            param_value = event['tickers']
            if isinstance(param_value, str):
                try:
                    if param_value.startswith('[') and param_value.endswith(']'):
                        tickers = json.loads(param_value)
                    else:
                        tickers = [ticker.strip() for ticker in param_value.split(',')]
                except json.JSONDecodeError:
                    tickers = [ticker.strip() for ticker in param_value.split(',')]
            elif isinstance(param_value, list):
                tickers = param_value

        # 3. Try to extract 'timeframe' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'timeframe' and param.get('value') is not None:
                    timeframe = str(param['value']).lower()
                    break
        
        # 4. If 'timeframe' is still not found, try to extract from direct key
        if event.get('timeframe') is not None:
            timeframe = str(event['timeframe']).lower()

        # 5. Try to extract 'client_name' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'client_name' and param.get('value') is not None:
                    client_name = str(param['value']).strip()
                    break
        
        # 6. If 'client_name' is still not found, try to extract from direct key
        if event.get('client_name') is not None:
            client_name = str(event['client_name']).strip()

        print(f"DEBUG: Tickers: {tickers}, Timeframe: '{timeframe}', Client: '{client_name}' after extraction.")

        logger.info(f"🚀 Processing portfolio news request", 
                   context={
                       'requestId': request_id, 
                       'tickers': tickers, 
                       'timeframe': timeframe,
                       'client_name': client_name
                   })
        
        # Initialize service and process request
        service = PortfolioNewsService()
        result = service.get_portfolio_news_and_prices(tickers, timeframe, client_name)
        
        # Handle cases where the result indicates an error (e.g., no valid tickers found)
        if not result.get('success', False):
            # Wrap error details in the Bedrock Agent expected format
            responseBody_for_error = {
                "TEXT": {
                    "body": json.dumps(result, default=str)
                }
            }
            return {
                'messageVersion': messageVersion,
                'response': {
                    'actionGroup': actionGroup,
                    'function': function,
                    'functionResponse': {
                        'responseBody': responseBody_for_error
                    }
                }
            }
        
        # Prepare Bedrock Agent response
        responseBody_for_success = {
            "TEXT": {
                "body": json.dumps(result, default=str)
            }
        }
        
        action_response = {
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody_for_success
            }
        }

        final_response = {
            'messageVersion': messageVersion,
            'response': action_response
        }
        
        logger.info(f"Portfolio news request successful for {len(tickers)} tickers: {tickers}")
        print(f"DEBUG: Final Lambda success response: {json.dumps(final_response, indent=2)}")
        return final_response
        
    except Exception as e:
        logger.error(f"❌ Portfolio News Lambda handler failed", 
                    context={'requestId': event.get('requestId', 'unknown')}, 
                    error=e)
        
        # Create an instance to generate standardized error response
        service = PortfolioNewsService()
        error_details = service._error_response(f"Internal server error: {str(e)}")
        
        responseBody_for_error = {
            "TEXT": {
                "body": json.dumps(error_details, default=str)
            }
        }
        
        error_action_response = {
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody_for_error
            }
        }
        
        final_error_response = {
            'messageVersion': messageVersion,
            'response': error_action_response
        }
        
        print(f"DEBUG: Final Lambda error response: {json.dumps(final_error_response, indent=2)}")
        return final_error_response


# For local testing
if __name__ == "__main__":
    # Mock news_client for local testing
    class MockNewsClient:
        def get_portfolio_news(self, tickers, timeframe):
            # Mock news data
            return [
                {
                    'title': 'Fed Holds Rates Steady, Markets Rally',
                    'summary': 'The Federal Reserve left interest rates unchanged, boosting equities across all sectors.',
                    'source': 'Reuters',
                    'published_at': '2025-01-13T14:00:00Z',
                    'tickers': ['AAPL', 'MSFT', 'GOOGL'],
                    'url': 'https://reuters.com/example',
                    'relevance_score': 0.9
                },
                {
                    'title': 'Oil Prices Spike Amid Middle East Conflict',
                    'summary': 'Crude futures surged 7% on geopolitical fears affecting energy sector.',
                    'source': 'Bloomberg',
                    'published_at': '2025-01-13T12:30:00Z',
                    'tickers': ['XOM', 'CVX'],
                    'url': 'https://bloomberg.com/example',
                    'relevance_score': 0.8
                },
                {
                    'title': 'Tesla Stock Volatility Continues',
                    'summary': 'Tesla shares down 14% then recovered 4% amid ongoing market uncertainty.',
                    'source': 'MarketWatch',
                    'published_at': '2025-01-13T10:15:00Z',
                    'tickers': ['TSLA'],
                    'url': 'https://marketwatch.com/example',
                    'relevance_score': 0.7
                }
            ]

        def get_portfolio_prices(self, tickers):
            # Mock price data
            mock_prices = {
                'AAPL': {'price': 196.33, 'change': 1.27},
                'TSLA': {'price': 192.01, 'change': 4.23},
                'XOM': {'price': 123.45, 'change': 7.2},
                'MSFT': {'price': 420.75, 'change': -0.5},
                'GOOGL': {'price': 151.30, 'change': 2.1}
            }
            
            prices = []
            for ticker in tickers:
                if ticker in mock_prices:
                    prices.append({
                        'ticker': ticker,
                        'price': mock_prices[ticker]['price'],
                        'change_percent': mock_prices[ticker]['change'],
                        'timestamp': datetime.now().isoformat() + 'Z'
                    })
                else:
                    prices.append({
                        'ticker': ticker,
                        'price': 100.0,
                        'change_percent': 0.0,
                        'timestamp': datetime.now().isoformat() + 'Z'
                    })
            return prices

    # Overwrite the actual news_client with the mock for local testing
    news_client = MockNewsClient()

    print("AWS Chatbot Portfolio News Tool - Local Demonstration")
    print("=" * 60)
    
    # Test cases for local demonstration, simulating Bedrock Agent input
    test_events_bedrock_format = [
        # Bedrock Agent style event for portfolio news
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioNewsActionGroup",
            "function": "getPortfolioNews",
            "parameters": [
                {"name": "tickers", "value": ["AAPL", "TSLA", "XOM"]},
                {"name": "timeframe", "value": "24h"}
            ],
            "sessionId": "test-session-123",
            "invocationId": "test-invocation-123",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-001"
        },
        # Bedrock Agent style event with client lookup
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioNewsActionGroup",
            "function": "getPortfolioNews",
            "parameters": [
                {"name": "client_name", "value": "alice"},
                {"name": "timeframe", "value": "48h"}
            ],
            "sessionId": "test-session-456",
            "invocationId": "test-invocation-456",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-002"
        },
        # Bedrock Agent style event with another client
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioNewsActionGroup",
            "function": "getPortfolioNews",
            "parameters": [
                {"name": "client_name", "value": "charlie"},
                {"name": "timeframe", "value": "7d"}
            ],
            "sessionId": "test-session-789",
            "invocationId": "test-invocation-789",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-003"
        },
        # Bedrock Agent style event with missing client (should use default)
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioNewsActionGroup",
            "function": "getPortfolioNews",
            "parameters": [
                {"name": "client_name", "value": "unknown_client"},
                {"name": "timeframe", "value": "24h"}
            ],
            "sessionId": "test-session-999",
            "invocationId": "test-invocation-999",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-004"
        },
        # Direct Lambda console test style event with client
        {"client_name": "bob", "timeframe": "30d", "requestId": "test-req-005"},
        {"tickers": "AAPL", "requestId": "test-req-006"},  # Single ticker as string
    ]
    
    for i, test_event in enumerate(test_events_bedrock_format, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input Event: {json.dumps(test_event, indent=2)}")
        
        result = lambda_handler(test_event, None)
        
        print(f"\nOutput Response: {json.dumps(result, indent=2)}")
        
        # Verify response structure and content
        if 'response' in result and 'functionResponse' in result['response']:
            response_body = result['response']['functionResponse'].get('responseBody')
            if response_body and 'TEXT' in response_body and 'body' in response_body['TEXT']:
                try:
                    parsed_body = json.loads(response_body['TEXT']['body'])
                    print(f"Parsed Response Body Success: {parsed_body.get('success', 'N/A')}")
                    if parsed_body.get('success'):
                        print(f"News Articles: {len(parsed_body.get('news', []))}")
                        print(f"Price Quotes: {len(parsed_body.get('prices', []))}")
                        print(f"Tickers: {parsed_body.get('tickers', [])}")
                        if 'client' in parsed_body:
                            client_info = parsed_body['client']
                            print(f"Client: {client_info.get('name')} ({client_info.get('account_type')})")
                    else:
                        print(f"Parsed Error: {parsed_body.get('error')}")
                except json.JSONDecodeError:
                    print(f"Failed to parse response body as JSON: {response_body['TEXT']['body']}")
            else:
                print("Response body not in expected 'TEXT' format.")
        else:
            print("Response not in expected Bedrock Agent format.")
    
    print("\n" + "=" * 60)
    print("Local Demonstration Complete!") 