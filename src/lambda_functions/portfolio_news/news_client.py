"""
News API client for portfolio-related news retrieval
Implements error handling and fallback mechanisms for reliability
"""

import requests
import yfinance as yf
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import time
import os
import sys

from logger import get_logger


class NewsClient:
    """
    Client for news API integration with error handling and caching.
    Supports multiple news sources for financial data.
    """
    
    def __init__(self, cache_duration_minutes: int = 15, max_retries: int = 3):
        self.logger = get_logger("NewsClient")
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.max_retries = max_retries
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # API keys (in production, these should come from AWS Secrets Manager)
        self.newsapi_key = os.environ.get('NEWSAPI_KEY')
        self.newsdata_key = os.environ.get('NEWSDATA_API_KEY')
        
        print("DEBUG: NewsAPI key:", self.newsapi_key)
        print("DEBUG: Newsdata.io key:", self.newsdata_key)
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key].get('timestamp')
        if not cache_time:
            return False
            
        return datetime.now() - cache_time < self.cache_duration
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key):
            self.logger.info(f"Using cached data for {cache_key}")
            return self._cache[cache_key]['data']
        return None
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self._cache[cache_key] = {
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
    
    def get_portfolio_news(self, tickers: List[str], timeframe: str = "24h") -> List[Dict[str, Any]]:
        """
        Get news headlines for a list of portfolio tickers
        
        Args:
            tickers: List of stock ticker symbols
            timeframe: Time range for news (24h, 7d, 30d)
            
        Returns:
            List of news articles with metadata
        """
        cache_key = f"news_{'-'.join(sorted(tickers))}_{timeframe}"
        
        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        news_articles = []
        
        try:
            # Try Yahoo Finance news first (free and reliable)
            yf_news = self._get_yahoo_finance_news(tickers, timeframe)
            news_articles.extend(yf_news)
            
            # If we have API keys, supplement with external sources
            if self.newsapi_key:
                newsapi_articles = self._get_newsapi_articles(tickers, timeframe)
                news_articles.extend(newsapi_articles)
            
            if self.newsdata_key:
                newsdata_articles = self._get_newsdata_articles(tickers, timeframe)
                news_articles.extend(newsdata_articles)
            
            # Remove duplicates and sort by recency
            news_articles = self._deduplicate_and_sort(news_articles)
            
            # Limit to most relevant articles
            news_articles = news_articles[:20]  # Top 20 most relevant articles
            
            # Cache the result
            self._cache_data(cache_key, news_articles)
            
            self.logger.info(f"Retrieved {len(news_articles)} news articles for tickers: {tickers}")
            return news_articles
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve news for tickers {tickers}", error=e)
            # Return empty list rather than failing completely
            return []
    
    def _get_yahoo_finance_news(self, tickers: List[str], timeframe: str) -> List[Dict[str, Any]]:
        """Get news from Yahoo Finance for each ticker"""
        articles = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                news = stock.news
                
                for item in news[:5]:  # Top 5 per ticker
                    # Convert timestamp to ISO format
                    published_at = datetime.fromtimestamp(
                        item.get('providerPublishTime', time.time())
                    ).isoformat() + 'Z'
                    
                    article = {
                        'title': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('publisher', 'Yahoo Finance'),
                        'published_at': published_at,
                        'tickers': [ticker],
                        'url': item.get('link', ''),
                        'relevance_score': 0.8  # High relevance for ticker-specific news
                    }
                    articles.append(article)
                    
            except Exception as e:
                self.logger.warning(f"Failed to get Yahoo Finance news for {ticker}", error=e)
                continue
        
        return articles
    
    def _get_newsapi_articles(self, tickers: List[str], timeframe: str) -> List[Dict[str, Any]]:
        """Get news from NewsAPI (requires API key)"""
        if not self.newsapi_key:
            return []
        
        articles = []
        
        try:
            # Convert timeframe to days
            days_back = self._timeframe_to_days(timeframe)
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Search for each ticker
            for ticker in tickers[:3]:  # Limit to avoid API rate limits
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': f'"{ticker}" OR "{self._get_company_keywords(ticker)}"',
                    'from': from_date,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'domains': 'reuters.com,bloomberg.com,cnbc.com,marketwatch.com',
                    'apiKey': self.newsapi_key,
                    'pageSize': 10
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                print("DEBUG: NewsAPI raw response:", data)
                
                for item in data.get('articles', []):
                    article = {
                        'title': item.get('title', ''),
                        'summary': item.get('description', ''),
                        'source': item.get('source', {}).get('name', 'NewsAPI'),
                        'published_at': item.get('publishedAt', ''),
                        'tickers': [ticker],
                        'url': item.get('url', ''),
                        'relevance_score': 0.7
                    }
                    articles.append(article)
                    
        except Exception as e:
            self.logger.warning("Failed to retrieve NewsAPI articles", error=e)
        
        return articles
    
    def _get_newsdata_articles(self, tickers: List[str], timeframe: str) -> List[Dict[str, Any]]:
        """Get news from Newsdata.io (requires API key)"""
        if not self.newsdata_key:
            return []
        
        articles = []
        
        try:
            # Create search query
            query_terms = [f'"{ticker}"' for ticker in tickers[:5]]
            query = ' OR '.join(query_terms)
            
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.newsdata_key,
                'q': query,
                'language': 'en',
                'category': 'business',
                'size': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print("DEBUG: Newsdata.io raw response:", data)
            
            for item in data.get('results', []):
                # Try to identify which tickers are mentioned
                mentioned_tickers = []
                title_content = (item.get('title', '') + ' ' + item.get('content', '')).upper()
                for ticker in tickers:
                    if ticker.upper() in title_content:
                        mentioned_tickers.append(ticker)
                
                if not mentioned_tickers:
                    mentioned_tickers = tickers  # Assume all if unclear
                
                article = {
                    'title': item.get('title', ''),
                    'summary': item.get('description', ''),
                    'source': item.get('source_id', 'Newsdata.io'),
                    'published_at': item.get('pubDate', ''),
                    'tickers': mentioned_tickers,
                    'url': item.get('link', ''),
                    'relevance_score': 0.6
                }
                articles.append(article)
                
        except Exception as e:
            self.logger.warning("Failed to retrieve Newsdata.io articles", error=e)
        
        return articles
    
    def _get_company_keywords(self, ticker: str) -> str:
        """Get company name for better news search"""
        ticker_to_company = {
            'AAPL': 'Apple Inc',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google Alphabet',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'META': 'Meta Facebook',
            'NVDA': 'NVIDIA',
            'JPM': 'JPMorgan Chase',
            'JNJ': 'Johnson Johnson',
            'V': 'Visa',
            'XOM': 'Exxon Mobil',
            'CVX': 'Chevron'
        }
        return ticker_to_company.get(ticker.upper(), ticker)
    
    def _timeframe_to_days(self, timeframe: str) -> int:
        """Convert timeframe string to number of days"""
        try:
            timeframe = timeframe.lower()
            if 'h' in timeframe:
                hours = int(timeframe.replace('h', ''))
                return max(1, hours // 24)
            elif 'd' in timeframe:
                return int(timeframe.replace('d', ''))
            elif 'w' in timeframe:
                return int(timeframe.replace('w', '')) * 7
            elif 'm' in timeframe:
                return int(timeframe.replace('m', '')) * 30
            else:
                return 1  # Default to 1 day
        except (ValueError, TypeError):
            return 1  # Default to 1 day for invalid input
    
    def _deduplicate_and_sort(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles and sort by relevance and recency"""
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_key = article.get('title', '').lower()[:50]  # First 50 chars
            if title_key not in seen_titles and title_key:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        # Sort by relevance score and recency
        unique_articles.sort(
            key=lambda x: (x.get('relevance_score', 0), x.get('published_at', '')),
            reverse=True
        )
        
        return unique_articles
    
    def get_portfolio_prices(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Get current price data for portfolio tickers
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            List of price data for each ticker
        """
        prices = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")  # Get last 2 days for change calculation
                
                if len(hist) >= 1:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
                    
                    change_percent = ((current_price - previous_price) / previous_price * 100) if previous_price != 0 else 0
                    
                    price_data = {
                        'ticker': ticker.upper(),
                        'price': round(float(current_price), 2),
                        'change_percent': round(float(change_percent), 2),
                        'timestamp': datetime.now().isoformat() + 'Z'
                    }
                    prices.append(price_data)
                    
            except Exception as e:
                self.logger.warning(f"Failed to get price data for {ticker}", error=e)
                # Add placeholder data
                prices.append({
                    'ticker': ticker.upper(),
                    'price': None,
                    'change_percent': None,
                    'timestamp': datetime.now().isoformat() + 'Z',
                    'error': str(e)
                })
        
        return prices
    
    def clear_cache(self):
        """Clear the internal cache"""
        self._cache.clear()
        self.logger.info("Cache cleared")


# Global instance for reuse
news_client = NewsClient()