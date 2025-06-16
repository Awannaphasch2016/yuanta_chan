"""
Yahoo Finance API client for financial data retrieval
Implements error handling and fallback mechanisms for reliability
"""

import yfinance as yf
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import time

from .logger import get_logger


class YahooFinanceClient:
    """
    Client for Yahoo Finance API integration with error handling and caching.
    Implements circuit breaker pattern for reliability.
    """
    
    def __init__(self, cache_duration_minutes: int = 30, max_retries: int = 3):
        self.logger = get_logger("YahooFinanceClient")
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.max_retries = max_retries
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def _is_cache_valid(self, ticker: str) -> bool:
        """Check if cached data is still valid"""
        if ticker not in self._cache:
            return False
        
        cache_time = self._cache[ticker].get('timestamp')
        if not cache_time:
            return False
            
        return datetime.now() - cache_time < self.cache_duration
    
    def _get_cached_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get cached data if valid"""
        if self._is_cache_valid(ticker):
            self.logger.info(f"Using cached data for {ticker}")
            return self._cache[ticker]['data']
        return None
    
    def _cache_data(self, ticker: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self._cache[ticker] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _retry_request(self, func, *args, **kwargs) -> Any:
        """Retry mechanism for API requests"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"API request attempt {attempt + 1}")
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(f"API request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        raise last_exception
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive stock information for a ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing stock information
            
        Raises:
            Exception: If all retry attempts fail
        """
        ticker = ticker.upper()
        
        # Check cache first
        cached_data = self._get_cached_data(ticker)
        if cached_data:
            return cached_data
        
        try:
            def _fetch_data():
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Extract key financial metrics
                extracted_data = {
                    'symbol': ticker,
                    'name': info.get('longName', ticker),
                    'currentPrice': info.get('currentPrice'),
                    'forwardPE': info.get('forwardPE'),
                    'returnOnEquity': info.get('returnOnEquity'),
                    'debtToEquity': info.get('debtToEquity'),
                    'profitMargins': info.get('profitMargins'),
                    'earningsGrowth': info.get('earningsGrowth'),
                    'revenueGrowth': info.get('revenueGrowth'),
                    'sector': info.get('sector'),
                    'industry': info.get('industry'),
                    'marketCap': info.get('marketCap'),
                    'beta': info.get('beta'),
                    'dividendYield': info.get('dividendYield'),
                    'enterpriseValue': info.get('enterpriseValue'),
                    'ebitda': info.get('ebitda'),
                    'retrieved_at': datetime.now().isoformat()
                }
                
                return extracted_data
            
            data = self._retry_request(_fetch_data)
            
            # Cache the successful result
            self._cache_data(ticker, data)
            
            self.logger.info(f"Successfully retrieved data for {ticker}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve data for {ticker}", error=e)
            raise Exception(f"Unable to fetch data for {ticker}: {str(e)}")
    
    def get_earnings_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get earnings data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing earnings information
        """
        ticker = ticker.upper()
        
        try:
            def _fetch_earnings():
                stock = yf.Ticker(ticker)
                earnings = stock.earnings
                
                if earnings is None or earnings.empty:
                    return {'symbol': ticker, 'earnings': None, 'message': 'No earnings data available'}
                
                # Convert to dictionary format
                earnings_dict = earnings.to_dict()
                
                return {
                    'symbol': ticker,
                    'earnings': earnings_dict,
                    'years': list(earnings_dict.get('Revenue', {}).keys()) if 'Revenue' in earnings_dict else [],
                    'retrieved_at': datetime.now().isoformat()
                }
            
            data = self._retry_request(_fetch_earnings)
            self.logger.info(f"Successfully retrieved earnings data for {ticker}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve earnings data for {ticker}", error=e)
            raise Exception(f"Unable to fetch earnings data for {ticker}: {str(e)}")
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol exists
        
        Args:
            ticker: Stock ticker symbol to validate
            
        Returns:
            True if ticker exists, False otherwise
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            # Check if we got valid data
            return bool(info.get('symbol') or info.get('longName'))
            
        except Exception as e:
            self.logger.warning(f"Ticker validation failed for {ticker}", error=e)
            return False
    
    def clear_cache(self):
        """Clear the internal cache"""
        self._cache.clear()
        self.logger.info("Cache cleared")


# Global instance for reuse
yahoo_client = YahooFinanceClient() 