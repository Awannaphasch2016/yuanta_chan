import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import time # Import time for generating request IDs

# Assuming 'logger.py' and 'yahoo_finance_client.py' are available and correct
from logger import get_logger
from yahoo_finance_client import yahoo_client


class FinancialDataService:
    """
    Service for retrieving and processing financial data from various sources.
    Supports multiple data types including overview, earnings, historical data.
    """
    
    def __init__(self):
        self.logger = get_logger("FinancialDataLambda")
        self.supported_data_types = ['overview', 'earnings', 'latesearnings', 'historical', 'profile', 'metrics', 'price']
        self.supported_query_types = ['latestEarnings']  # PRD queryType values
    
    def get_financial_data(self, ticker: str, data_type: str = 'overview', 
                          additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve financial data for a given ticker and data type
        
        Args:
            ticker: Stock ticker symbol
            data_type: Type of data to retrieve (overview, earnings, historical, etc.)
            additional_params: Optional parameters for specific data types
            
        Returns:
            Dictionary containing financial data and metadata
        """
        try:
            ticker = ticker.upper()
            self.logger.info(f"Retrieving {data_type} data for {ticker}")
            
            # Validate inputs
            if not ticker:
                return self._error_response("Ticker symbol is required")
            
            if data_type not in self.supported_data_types:
                return self._error_response(f"Unsupported data type: {data_type}. Supported: {self.supported_data_types}")
            
            # Validate ticker exists - placeholder, assuming yahoo_client handles this
            # if not yahoo_client.validate_ticker(ticker): # This line might cause issues if not implemented
            #    return self._error_response(f"Invalid ticker symbol: {ticker}")
            
            # Route to appropriate data retrieval method
            if data_type == 'overview':
                data = self._get_overview_data(ticker)
            elif data_type == 'earnings':
                data = self._get_earnings_data(ticker)
            elif data_type == 'latesearnings':
                data = self._get_latest_earnings_data(ticker)
            elif data_type == 'historical':
                data = self._get_historical_data(ticker, additional_params or {})
            elif data_type == 'profile':
                data = self._get_profile_data(ticker)
            elif data_type == 'metrics':
                data = self._get_metrics_data(ticker)
            elif data_type == 'price':
                data = self._get_price_data(ticker)
            else:
                return self._error_response(f"Data type handler not implemented: {data_type}")
            
            # Prepare successful response
            result = {
                'ticker': ticker,
                'data_type': data_type,
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'retrieved_at': data.get('retrieved_at') if isinstance(data, dict) else datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully retrieved {data_type} data for {ticker}")
            return result
            
        except Exception as e:
            self.logger.error(f"Financial data retrieval failed for {ticker} ({data_type})", context=None, error=e)
            return self._error_response(f"Data retrieval failed: {str(e)}")
    
    def _get_overview_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive stock overview data"""
        stock_info = yahoo_client.get_stock_info(ticker)
        
        overview = {
            'basic_info': {
                'symbol': stock_info.get('symbol'),
                'name': stock_info.get('name'),
                'sector': stock_info.get('sector'),
                'industry': stock_info.get('industry'),
                'market_cap': stock_info.get('marketCap')
            },
            'price_info': {
                'current_price': stock_info.get('currentPrice'),
                'beta': stock_info.get('beta'),
                'dividend_yield': stock_info.get('dividendYield')
            },
            'financial_ratios': {
                'forward_pe': stock_info.get('forwardPE'),
                'return_on_equity': stock_info.get('returnOnEquity'),
                'debt_to_equity': stock_info.get('debtToEquity'),
                'profit_margins': stock_info.get('profitMargins')
            },
            'growth_metrics': {
                'earnings_growth': stock_info.get('earningsGrowth'),
                'revenue_growth': stock_info.get('revenueGrowth')
            },
            'retrieved_at': stock_info.get('retrieved_at')
        }
        
        return overview
    
    def _get_earnings_data(self, ticker: str) -> Dict[str, Any]:
        """Get earnings-specific data"""
        try:
            earnings_data = yahoo_client.get_earnings_data(ticker)
            
            # Enhanced earnings processing
            processed_earnings = {
                'symbol': earnings_data.get('symbol'),
                'raw_earnings': earnings_data.get('earnings'),
                'available_years': earnings_data.get('years', []),
                'summary': self._summarize_earnings(earnings_data.get('earnings')),
                'retrieved_at': earnings_data.get('retrieved_at')
            }
            
            return processed_earnings
            
        except Exception as e:
            self.logger.warning(f"Earnings data processing failed for {ticker}", context=None)
            return {
                'symbol': ticker,
                'earnings_available': False,
                'error': str(e),
                'retrieved_at': datetime.now().isoformat()
            }
    
    def _get_latest_earnings_data(self, ticker: str) -> Dict[str, Any]:
        """Get latest quarterly earnings data in PRD format"""
        try:
            # Use the new quarterly earnings method
            quarterly_data = yahoo_client.get_quarterly_earnings(ticker)
            
            self.logger.info(f"Successfully retrieved latest earnings for {ticker}")
            return quarterly_data
            
        except Exception as e:
            self.logger.error(f"Latest earnings data retrieval failed for {ticker}", context=None, error=e)
            return {
                'ticker': ticker,
                'error': f"Unable to retrieve latest earnings: {str(e)}",
                'retrieved_at': datetime.now().isoformat()
            }
    
    def _get_historical_data(self, ticker: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical price data using Yahoo Finance API"""
        try:
            period = params.get('period', '1y')
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            
            # Get historical data from Yahoo Finance
            historical_data = yahoo_client.get_historical_data(
                ticker=ticker,
                period=period,
                start_date=start_date,
                end_date=end_date
            )
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Historical data retrieval failed for {ticker}", context=None, error=e)
            return {
                'symbol': ticker,
                'period': period,
                'start_date': start_date,
                'end_date': end_date,
                'historical_data': None,
                'error': str(e),
                'retrieved_at': datetime.now().isoformat()
            }
    
    def _get_profile_data(self, ticker: str) -> Dict[str, Any]:
        """Get company profile data"""
        stock_info = yahoo_client.get_stock_info(ticker)
        
        profile = {
            'company_info': {
                'symbol': stock_info.get('symbol'),
                'name': stock_info.get('name'),
                'sector': stock_info.get('sector'),
                'industry': stock_info.get('industry')
            },
            'business_metrics': {
                'market_cap': stock_info.get('marketCap'),
                'enterprise_value': stock_info.get('enterpriseValue'),
                'ebitda': stock_info.get('ebitda'),
                'beta': stock_info.get('beta')
            },
            'retrieved_at': stock_info.get('retrieved_at')
        }
        
        return profile
    
    def _get_metrics_data(self, ticker: str) -> Dict[str, Any]:
        """Get key financial metrics"""
        stock_info = yahoo_client.get_stock_info(ticker)
        
        metrics = {
            'valuation_metrics': {
                'forward_pe': stock_info.get('forwardPE'),
                'current_price': stock_info.get('currentPrice'),
                'market_cap': stock_info.get('marketCap')
            },
            'profitability_metrics': {
                'return_on_equity': stock_info.get('returnOnEquity'),
                'profit_margins': stock_info.get('profitMargins'),
                'ebitda': stock_info.get('ebitda')
            },
            'financial_health': {
                'debt_to_equity': stock_info.get('debtToEquity'),
                'beta': stock_info.get('beta')
            },
            'growth_metrics': {
                'earnings_growth': stock_info.get('earningsGrowth'),
                'revenue_growth': stock_info.get('revenueGrowth')
            },
            'retrieved_at': stock_info.get('retrieved_at')
        }
        
        return metrics
    
    def _get_price_data(self, ticker: str) -> Dict[str, Any]:
        """Get current price data for a ticker"""
        stock_info = yahoo_client.get_stock_info(ticker)
        
        price_data = {
            'symbol': stock_info.get('symbol'),
            'name': stock_info.get('name'),
            'current_price': stock_info.get('currentPrice'),
            'currency': 'USD',
            'retrieved_at': stock_info.get('retrieved_at')
        }
        
        return price_data
    
    def _summarize_earnings(self, earnings_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize earnings data for easier consumption"""
        if not earnings_data or not isinstance(earnings_data, dict):
            return {'summary_available': False}
        
        summary = {
            'summary_available': True,
            'revenue_trends': 'Analysis not implemented yet',
            'earnings_trends': 'Analysis not implemented yet',
            'years_of_data': len(earnings_data.get('Revenue', {})) if 'Revenue' in earnings_data else 0
        }
        
        return summary
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler for financial data requests,
    optimized for Amazon Bedrock Agent integration.
    """
    logger = get_logger("FinancialDataHandler")
    print(f"DEBUG: Full event received by Lambda: {json.dumps(event, indent=2)}")

    # Extract Bedrock Agent specific metadata
    actionGroup = event.get('actionGroup', 'FinancialDataActionGroup') # Replace with your actual Action Group name
    function = event.get('function', 'getFinancialData') # Replace with your actual Function name
    messageVersion = event.get('messageVersion', '1.0')

    try:
        ticker = ''
        data_type = event.get('data_type', 'overview')
        query_type = event.get('queryType', '')  # PRD parameter
        additional_params = event.get('additional_params')
        request_id = event.get('requestId', f'req-{int(time.time())}')

        # 1. Try to extract 'ticker' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'ticker' and param.get('value') is not None:
                    ticker = str(param['value']).upper()
                    break # Exit loop if found
        
        # 2. If 'ticker' is still not found, try to extract from 'ticker' key directly (for Lambda console testing or other services)
        if not ticker and event.get('ticker') is not None:
            ticker = str(event['ticker']).upper()

        # 3. Try to extract 'queryType' from 'parameters' list (Bedrock Agent format) - PRD parameter
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'queryType' and param.get('value') is not None:
                    query_type = str(param['value']).lower()
                    break

        # 4. If 'queryType' is still not found, try to extract from 'queryType' key directly
        if not query_type and event.get('queryType') is not None:
            query_type = str(event['queryType']).lower()

        # 5. Try to extract 'data_type' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'data_type' and param.get('value') is not None:
                    data_type = str(param['value']).lower()
                    break
        
        # 6. If 'data_type' is still not found, try to extract from 'data_type' key directly
        if event.get('data_type') is not None:
            data_type = str(event['data_type']).lower()

        # 7. Map queryType to data_type for PRD compliance
        if query_type == 'latestearnings':
            data_type = 'latesearnings'
        elif query_type and not data_type:
            data_type = query_type

        # 8. Try to extract 'additional_params' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'additional_params' and param.get('value') is not None:
                    # Handle both string and dict formats
                    if isinstance(param['value'], str):
                        try:
                            additional_params = json.loads(param['value'])
                        except json.JSONDecodeError:
                            additional_params = {'raw_value': param['value']}
                    else:
                        additional_params = param['value']
                    break
        
        # 9. If 'additional_params' is still not found, try to extract from 'additional_params' key directly
        if additional_params is None and event.get('additional_params') is not None:
            additional_params = event['additional_params']


        print(f"DEBUG: Ticker: '{ticker}', Data Type: '{data_type}', Query Type: '{query_type}', Additional Params: '{additional_params}' after extraction.")

        logger.info(f"🚀 Processing financial data request", 
                   context={
                       'requestId': request_id, 
                       'ticker': ticker, 
                       'data_type': data_type,
                       'query_type': query_type
                   })
        
        # Handle cases where 'ticker' is still missing
        if not ticker:
            service = FinancialDataService() # Create instance to use _error_response
            error_details = service._error_response("Missing required parameter: ticker")
            
            # Wrap error details in the Bedrock Agent expected format
            responseBody_for_error = {
                "TEXT": {
                    "body": json.dumps(error_details, default=str)
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
        
        # Initialize service and process request
        service = FinancialDataService()
        result = service.get_financial_data(ticker, data_type, additional_params)
        
        # Prepare Bedrock Agent response
        # The 'result' is already a dict, which will be json.dumps-ed into the 'body'
        responseBody_for_success = {
            "TEXT": {
                "body": json.dumps(result, default=str) # Convert the dictionary result to a string
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
        
        logger.info(f"Financial data request successful for {ticker}")
        print(f"DEBUG: Final Lambda success response: {json.dumps(final_response, indent=2)}")
        return final_response
        
    except Exception as e:
        logger.error(f"❌ Financial Data Lambda handler failed", 
                    context={'requestId': event.get('requestId', 'unknown')}, 
                    error=e)
        
        # Create an instance to generate standardized error response
        service = FinancialDataService()
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
    # Mock yahoo_client for local testing
    class MockYahooClient:
        def get_stock_info(self, ticker):
            if ticker == "AAPL":
                return {
                    'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics',
                    'marketCap': 2800000000000, 'currentPrice': 175.0, 'beta': 1.2, 'dividendYield': 0.005,
                    'forwardPE': 28.0, 'returnOnEquity': 1.5, 'debtToEquity': 1.2, 'profitMargins': 0.25,
                    'earningsGrowth': 0.15, 'revenueGrowth': 0.08, 'retrieved_at': datetime.now().isoformat()
                }
            elif ticker == "MSFT":
                return {
                    'symbol': 'MSFT', 'name': 'Microsoft Corp', 'sector': 'Technology', 'industry': 'Software - Infrastructure',
                    'marketCap': 3100000000000, 'currentPrice': 420.0, 'beta': 0.9, 'dividendYield': 0.007,
                    'forwardPE': 30.0, 'returnOnEquity': 1.8, 'debtToEquity': 0.8, 'profitMargins': 0.30,
                    'earningsGrowth': 0.20, 'revenueGrowth': 0.12, 'retrieved_at': datetime.now().isoformat()
                }
            elif ticker == "GOOGL":
                return {
                    'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Communication Services', 'industry': 'Internet Content & Information',
                    'marketCap': 2200000000000, 'currentPrice': 150.0, 'beta': 1.1, 'dividendYield': 0.0,
                    'forwardPE': 25.0, 'returnOnEquity': 1.3, 'debtToEquity': 0.5, 'profitMargins': 0.22,
                    'earningsGrowth': 0.10, 'revenueGrowth': 0.07, 'retrieved_at': datetime.now().isoformat()
                }
            elif ticker == "TSLA":
                return {
                    'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Auto Manufacturers',
                    'marketCap': 800000000000, 'currentPrice': 250.0, 'beta': 2.3, 'dividendYield': 0.0,
                    'forwardPE': 45.0, 'returnOnEquity': 0.8, 'debtToEquity': 0.3, 'profitMargins': 0.15,
                    'earningsGrowth': 0.25, 'revenueGrowth': 0.20, 'retrieved_at': datetime.now().isoformat()
                }
            else:
                return {} # Or raise an error to simulate validation failure

        def get_earnings_data(self, ticker):
            if ticker == "AAPL":
                return {
                    'symbol': 'AAPL',
                    'earnings': {
                        'Revenue': {'2024': 383000, '2023': 387000, '2022': 394000},
                        'Earnings': {'2024': 95000, '2023': 97000, '2022': 100000}
                    },
                    'years': ['2024', '2023', '2022'],
                    'retrieved_at': datetime.now().isoformat()
                }
            return {}

        def get_quarterly_earnings(self, ticker):
            # Mock quarterly earnings data in PRD format
            if ticker == "AAPL":
                return {
                    'ticker': 'AAPL',
                    'quarter': 'Q1 2025',
                    'reportDate': '2025-01-30',
                    'revenue': 119580000000,  # $119.58B
                    'netIncome': 30687000000,  # $30.69B
                    'EPS': 1.88,
                    'currency': 'USD',
                    'yearAgoRevenue': 117154000000,  # $117.15B
                    'yearAgoEPS': 1.76,
                    'retrieved_at': datetime.now().isoformat()
                }
            elif ticker == "TSLA":
                return {
                    'ticker': 'TSLA',
                    'quarter': 'Q1 2025',
                    'reportDate': '2025-01-24',
                    'revenue': 25167000000,  # $25.17B
                    'netIncome': 2513000000,  # $2.51B
                    'EPS': 0.71,
                    'currency': 'USD',
                    'yearAgoRevenue': 23329000000,  # $23.33B
                    'yearAgoEPS': 0.64,
                    'retrieved_at': datetime.now().isoformat()
                }
            return {
                'ticker': ticker,
                'quarter': 'Q1 2025',
                'reportDate': '2025-01-30',
                'revenue': 10000000000,  # $10B default
                'netIncome': 1000000000,  # $1B default
                'EPS': 1.25,
                'currency': 'USD',
                'yearAgoRevenue': 9500000000,  # $9.5B default
                'yearAgoEPS': 1.18,
                'retrieved_at': datetime.now().isoformat()
            }

        def get_historical_data(self, ticker, period='1y', start_date=None, end_date=None):
            if ticker == "NVDA":
                # Mock historical data for NVDA
                return {
                    'symbol': 'NVDA',
                    'period': period,
                    'start_date': start_date,
                    'end_date': end_date,
                    'historical_data': {
                        '2025-01-01': {
                            'open': 450.0,
                            'high': 455.0,
                            'low': 448.0,
                            'close': 452.0,
                            'volume': 50000000,
                            'adj_close': 452.0
                        },
                        '2025-07-02': {
                            'open': 1250.0,
                            'high': 1260.0,
                            'low': 1240.0,
                            'close': 1255.0,
                            'volume': 60000000,
                            'adj_close': 1255.0
                        }
                    },
                    'summary': {
                        'current_price': 1255.0,
                        'start_price': 452.0,
                        'price_change': 803.0,
                        'price_change_percent': 177.65,
                        'highest_price': 1255.0,
                        'lowest_price': 452.0,
                        'data_points': 2
                    },
                    'retrieved_at': datetime.now().isoformat()
                }
            elif ticker == "AAPL":
                return {
                    'symbol': 'AAPL',
                    'period': period,
                    'start_date': start_date,
                    'end_date': end_date,
                    'historical_data': {
                        '2025-01-01': {
                            'open': 180.0,
                            'high': 182.0,
                            'low': 179.0,
                            'close': 181.0,
                            'volume': 40000000,
                            'adj_close': 181.0
                        },
                        '2025-07-02': {
                            'open': 175.0,
                            'high': 176.0,
                            'low': 174.0,
                            'close': 175.0,
                            'volume': 45000000,
                            'adj_close': 175.0
                        }
                    },
                    'summary': {
                        'current_price': 175.0,
                        'start_price': 181.0,
                        'price_change': -6.0,
                        'price_change_percent': -3.31,
                        'highest_price': 181.0,
                        'lowest_price': 175.0,
                        'data_points': 2
                    },
                    'retrieved_at': datetime.now().isoformat()
                }
            elif ticker == "TSLA":
                return {
                    'symbol': 'TSLA',
                    'period': period,
                    'start_date': start_date,
                    'end_date': end_date,
                    'historical_data': {
                        '2025-01-01': {
                            'open': 200.0,
                            'high': 205.0,
                            'low': 198.0,
                            'close': 202.0,
                            'volume': 80000000,
                            'adj_close': 202.0
                        },
                        '2025-07-02': {
                            'open': 248.0,
                            'high': 252.0,
                            'low': 246.0,
                            'close': 250.0,
                            'volume': 90000000,
                            'adj_close': 250.0
                        }
                    },
                    'summary': {
                        'current_price': 250.0,
                        'start_price': 202.0,
                        'price_change': 48.0,
                        'price_change_percent': 23.76,
                        'highest_price': 250.0,
                        'lowest_price': 202.0,
                        'data_points': 2
                    },
                    'retrieved_at': datetime.now().isoformat()
                }
            return {
                'symbol': ticker,
                'period': period,
                'start_date': start_date,
                'end_date': end_date,
                'historical_data': None,
                'message': 'No historical data available for the specified period',
                'retrieved_at': datetime.now().isoformat()
            }

        def validate_ticker(self, ticker):
            return ticker in ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]

    # Overwrite the actual yahoo_client with the mock for local testing
    yahoo_client = MockYahooClient() 

    print("AWS Chatbot Financial Data - Local Demonstration")
    print("=" * 60)
    
    # Test cases for local demonstration, simulating Bedrock Agent input
    test_events_bedrock_format = [
        # Bedrock Agent style event for overview
        {
            "messageVersion": "1.0",
            "actionGroup": "FinancialDataActionGroup",
            "function": "getFinancialData",
            "parameters": [
                {"name": "ticker", "value": "AAPL"},
                {"name": "data_type", "value": "overview"}
            ],
            "sessionId": "test-session-123",
            "invocationId": "test-invocation-123",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-001"
        },
        # Bedrock Agent style event for earnings
        {
            "messageVersion": "1.0",
            "actionGroup": "FinancialDataActionGroup",
            "function": "getFinancialData",
            "parameters": [
                {"name": "ticker", "value": "MSFT"},
                {"name": "data_type", "value": "earnings"}
            ],
            "sessionId": "test-session-124",
            "invocationId": "test-invocation-124",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-002"
        },
        # PRD format - Latest Earnings with queryType
        {
            "messageVersion": "1.0",
            "actionGroup": "FinancialDataActionGroup",
            "function": "getFinancialData",
            "parameters": [
                {"name": "ticker", "value": "TSLA"},
                {"name": "queryType", "value": "latestEarnings"}
            ],
            "sessionId": "test-session-125",
            "invocationId": "test-invocation-125",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-003"
        },
        # Direct Lambda console test style event
        {"ticker": "GOOGL", "data_type": "metrics", "requestId": "test-req-004"},
        {"ticker": "INVALID", "data_type": "overview", "requestId": "test-req-005"},
        # Historical data test cases
        {
            "messageVersion": "1.0",
            "actionGroup": "FinancialDataActionGroup",
            "function": "getFinancialData",
            "parameters": [
                {"name": "ticker", "value": "NVDA"},
                {"name": "data_type", "value": "historical"},
                {"name": "additional_params", "value": {"period": "6mo"}}
            ],
            "sessionId": "test-session-hist",
            "invocationId": "test-invocation-hist",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-hist"
        },
        # TSLA historical data test case
        {
            "messageVersion": "1.0",
            "actionGroup": "FinancialDataActionGroup",
            "function": "getFinancialData",
            "parameters": [
                {"name": "ticker", "value": "TSLA"},
                {"name": "data_type", "value": "historical"},
                {"name": "additional_params", "value": {"start_date": "2025-01-01"}}
            ],
            "sessionId": "test-session-tsla",
            "invocationId": "test-invocation-tsla",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-tsla"
        },
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
                        print(f"Parsed Data Type: {parsed_body.get('data_type')}, Ticker: {parsed_body.get('ticker')}")
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