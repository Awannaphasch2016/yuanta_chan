"""
Yahoo Finance API client for financial data retrieval
Implements error handling and fallback mechanisms for reliability
"""

import yfinance as yf
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import time
import pandas as pd

from logger import get_logger


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
    
    def get_historical_data(self, ticker: str, period: str = '1y', start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get historical price data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            start_date: Start date in YYYY-MM-DD format (optional, overrides period)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            Dictionary containing historical price data
        """
        ticker = ticker.upper()
        
        try:
            def _fetch_historical():
                stock = yf.Ticker(ticker)
                
                if start_date and end_date:
                    # Use specific date range
                    hist_data = stock.history(start=start_date, end=end_date)
                elif start_date:
                    # Use start date to today
                    hist_data = stock.history(start=start_date)
                else:
                    # Use period
                    hist_data = stock.history(period=period)
                
                if hist_data is None or hist_data.empty:
                    return {
                        'symbol': ticker,
                        'historical_data': None,
                        'message': 'No historical data available for the specified period'
                    }
                
                # Debug: Log available columns
                self.logger.info(f"Available columns for {ticker}: {hist_data.columns.tolist()}")
                
                # Convert to dictionary format with dates as keys
                hist_dict = {}
                for date, row in hist_data.iterrows():
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # Safely extract values with fallbacks
                    open_price = float(row['Open']) if 'Open' in row and not pd.isna(row['Open']) else None
                    high_price = float(row['High']) if 'High' in row and not pd.isna(row['High']) else None
                    low_price = float(row['Low']) if 'Low' in row and not pd.isna(row['Low']) else None
                    close_price = float(row['Close']) if 'Close' in row and not pd.isna(row['Close']) else None
                    volume = int(row['Volume']) if 'Volume' in row and not pd.isna(row['Volume']) else None
                    
                    # Handle Adj Close - use Close as fallback if Adj Close doesn't exist
                    adj_close_price = None
                    if 'Adj Close' in row and not pd.isna(row['Adj Close']):
                        adj_close_price = float(row['Adj Close'])
                    elif close_price is not None:
                        adj_close_price = close_price  # Use Close as fallback
                    
                    hist_dict[date_str] = {
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': close_price,
                        'volume': volume,
                        'adj_close': adj_close_price
                    }
                
                # Calculate summary statistics
                if hist_dict:
                    prices = [data['close'] for data in hist_dict.values() if data['close'] is not None]
                    if prices:
                        current_price = prices[-1]
                        start_price = prices[0]
                        price_change = current_price - start_price
                        price_change_percent = ((current_price - start_price) / start_price * 100) if start_price != 0 else 0
                        
                        summary = {
                            'current_price': current_price,
                            'start_price': start_price,
                            'price_change': price_change,
                            'price_change_percent': price_change_percent,
                            'highest_price': max(prices),
                            'lowest_price': min(prices),
                            'data_points': len(prices)
                        }
                    else:
                        summary = {'message': 'No valid price data available'}
                else:
                    summary = {'message': 'No historical data available'}
                
                return {
                    'symbol': ticker,
                    'period': period,
                    'start_date': start_date,
                    'end_date': end_date,
                    'historical_data': hist_dict,
                    'summary': summary,
                    'retrieved_at': datetime.now().isoformat()
                }
            
            data = self._retry_request(_fetch_historical)
            self.logger.info(f"Successfully retrieved historical data for {ticker}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve historical data for {ticker}", error=e)
            raise Exception(f"Unable to fetch historical data for {ticker}: {str(e)}")
    
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