"""
Financial Data Lambda Function
Handles financial data retrieval for various data types and analysis needs
Designed for Amazon Bedrock Agent integration
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

from logger import get_logger
from yahoo_finance_client import yahoo_client


class FinancialDataService:
    """
    Service for retrieving and processing financial data from various sources.
    Supports multiple data types including overview, earnings, historical data.
    """
    
    def __init__(self):
        self.logger = get_logger("FinancialDataLambda")
        self.supported_data_types = ['overview', 'earnings', 'historical', 'profile', 'metrics']
    
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
            
            # Validate ticker exists
            if not yahoo_client.validate_ticker(ticker):
                return self._error_response(f"Invalid ticker symbol: {ticker}")
            
            # Route to appropriate data retrieval method
            if data_type == 'overview':
                data = self._get_overview_data(ticker)
            elif data_type == 'earnings':
                data = self._get_earnings_data(ticker)
            elif data_type == 'historical':
                data = self._get_historical_data(ticker, additional_params or {})
            elif data_type == 'profile':
                data = self._get_profile_data(ticker)
            elif data_type == 'metrics':
                data = self._get_metrics_data(ticker)
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
    
    def _get_historical_data(self, ticker: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical price data (placeholder for future implementation)"""
        period = params.get('period', '1y')
        
        return {
            'symbol': ticker,
            'period': period,
            'message': 'Historical data retrieval not yet implemented',
            'placeholder': True,
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
    AWS Lambda handler for financial data requests
    
    Expected event format:
    {
        "ticker": "AAPL",
        "data_type": "overview",
        "additional_params": {...}  # optional
    }
    """
    logger = get_logger("FinancialDataHandler")
    
    try:
        logger.info("Financial Data Lambda function invoked", context={"event": event})
        
        # Extract parameters from event
        ticker = event.get('ticker')
        data_type = event.get('data_type', 'overview')
        additional_params = event.get('additional_params')
        
        # Validate required parameters
        if not ticker:
            error_response = {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: ticker',
                    'timestamp': datetime.now().isoformat()
                })
            }
            logger.warning("Missing ticker parameter in request")
            return error_response
        
        # Initialize service and process request
        service = FinancialDataService()
        result = service.get_financial_data(ticker, data_type, additional_params)
        
        # Prepare Lambda response
        if result.get('success', False):
            response = {
                'statusCode': 200,
                'body': json.dumps(result),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
            logger.info(f"Financial data request successful for {ticker}")
        else:
            response = {
                'statusCode': 400,
                'body': json.dumps(result),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
            logger.warning(f"Financial data request failed for {ticker}")
        
        return response
        
    except Exception as e:
        logger.error("Financial Data Lambda handler failed", context=None, error=e)
        
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': f'Internal server error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        return error_response 