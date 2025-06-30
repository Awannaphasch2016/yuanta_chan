"""
Yahoo Finance Client for Portfolio Analysis Lambda Function
Enhanced with portfolio-specific data retrieval capabilities
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests


class YahooFinanceClient:
    """
    Enhanced Yahoo Finance client for portfolio analysis operations
    Supports individual stock data and portfolio-level analytics
    """
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.info_url = "https://query2.finance.yahoo.com/v10/finance/quoteSummary"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive stock information for portfolio analysis
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing stock information and metrics
        """
        try:
            # For demo purposes, return mock data
            # In production, this would make actual API calls to Yahoo Finance
            mock_data = self._get_mock_stock_data(ticker)
            mock_data['retrieved_at'] = datetime.now().isoformat()
            return mock_data
            
        except Exception as e:
            print(f"Error fetching stock info for {ticker}: {e}")
            return self._get_fallback_data(ticker)
    
    def get_earnings_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get earnings data for a specific ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing earnings information
        """
        try:
            # Mock earnings data for demo
            earnings_data = {
                'symbol': ticker,
                'earnings': self._get_mock_earnings(ticker),
                'years': ['2021', '2022', '2023', '2024'],
                'retrieved_at': datetime.now().isoformat()
            }
            return earnings_data
            
        except Exception as e:
            print(f"Error fetching earnings for {ticker}: {e}")
            return {
                'symbol': ticker,
                'earnings': [],
                'error': str(e),
                'retrieved_at': datetime.now().isoformat()
            }
    
    def get_portfolio_metrics(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Get aggregated metrics for a portfolio of stocks
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dictionary containing portfolio-level metrics
        """
        try:
            portfolio_data = {}
            total_market_cap = 0
            weighted_beta = 0
            
            for ticker in tickers:
                stock_data = self.get_stock_info(ticker)
                portfolio_data[ticker] = stock_data
                
                market_cap = stock_data.get('marketCap', 0)
                beta = stock_data.get('beta', 1.0)
                
                total_market_cap += market_cap
                weighted_beta += beta * market_cap
            
            # Calculate portfolio-level metrics
            portfolio_beta = weighted_beta / total_market_cap if total_market_cap > 0 else 1.0
            
            return {
                'portfolio_metrics': {
                    'total_market_cap': total_market_cap,
                    'portfolio_beta': portfolio_beta,
                    'number_of_stocks': len(tickers),
                    'diversification_score': self._calculate_diversification_score(portfolio_data)
                },
                'individual_stocks': portfolio_data,
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating portfolio metrics: {e}")
            return {
                'error': str(e),
                'retrieved_at': datetime.now().isoformat()
            }
    
    def get_sector_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get sector and industry information for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing sector and industry data
        """
        stock_info = self.get_stock_info(ticker)
        return {
            'ticker': ticker,
            'sector': stock_info.get('sector', 'Unknown'),
            'industry': stock_info.get('industry', 'Unknown'),
            'sector_performance': self._get_mock_sector_performance(stock_info.get('sector')),
            'retrieved_at': datetime.now().isoformat()
        }
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol exists
        
        Args:
            ticker: Stock ticker symbol to validate
            
        Returns:
            Boolean indicating if ticker is valid
        """
        # For demo purposes, validate against known tickers
        valid_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL',
            'ADBE', 'NFLX', 'CRM', 'INTC', 'AMD', 'ORCL', 'IBM', 'CSCO'
        ]
        return ticker.upper() in valid_tickers
    
    def _get_mock_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Generate mock stock data for demonstration"""
        
        # Mock data based on ticker
        mock_stocks = {
            'AAPL': {
                'symbol': 'AAPL',
                'longName': 'Apple Inc.',
                'currentPrice': 180.50,
                'marketCap': 2800000000000,
                'beta': 1.2,
                'forwardPE': 28.5,
                'trailingPE': 30.2,
                'returnOnEquity': 0.147,
                'debtToEquity': 1.73,
                'profitMargins': 0.258,
                'earningsGrowth': 0.11,
                'revenueGrowth': 0.08,
                'dividendYield': 0.0044,
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'fiftyTwoWeekHigh': 199.62,
                'fiftyTwoWeekLow': 164.08,
                'priceToBook': 39.4,
                'enterpriseValue': 2750000000000,
                'ebitda': 123000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ'
            },
            'MSFT': {
                'symbol': 'MSFT',
                'longName': 'Microsoft Corporation',
                'currentPrice': 420.15,
                'marketCap': 3100000000000,
                'beta': 0.9,
                'forwardPE': 32.1,
                'trailingPE': 34.5,
                'returnOnEquity': 0.186,
                'debtToEquity': 0.47,
                'profitMargins': 0.369,
                'earningsGrowth': 0.15,
                'revenueGrowth': 0.12,
                'dividendYield': 0.0072,
                'sector': 'Technology',
                'industry': 'Software - Infrastructure',
                'fiftyTwoWeekHigh': 468.35,
                'fiftyTwoWeekLow': 362.90,
                'priceToBook': 13.2,
                'enterpriseValue': 3050000000000,
                'ebitda': 109000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ'
            },
            'GOOGL': {
                'symbol': 'GOOGL',
                'longName': 'Alphabet Inc.',
                'currentPrice': 142.80,
                'marketCap': 1800000000000,
                'beta': 1.1,
                'forwardPE': 22.8,
                'trailingPE': 25.3,
                'returnOnEquity': 0.138,
                'debtToEquity': 0.11,
                'profitMargins': 0.212,
                'earningsGrowth': 0.09,
                'revenueGrowth': 0.07,
                'dividendYield': 0.0,
                'sector': 'Technology',
                'industry': 'Internet Content & Information',
                'fiftyTwoWeekHigh': 193.31,
                'fiftyTwoWeekLow': 129.40,
                'priceToBook': 5.8,
                'enterpriseValue': 1750000000000,
                'ebitda': 89000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ'
            },
            'JNJ': {
                'symbol': 'JNJ',
                'longName': 'Johnson & Johnson',
                'currentPrice': 155.25,
                'marketCap': 410000000000,
                'beta': 0.7,
                'forwardPE': 15.2,
                'trailingPE': 16.8,
                'returnOnEquity': 0.124,
                'debtToEquity': 0.46,
                'profitMargins': 0.178,
                'earningsGrowth': 0.05,
                'revenueGrowth': 0.03,
                'dividendYield': 0.0295,
                'sector': 'Healthcare',
                'industry': 'Drug Manufacturers - General',
                'fiftyTwoWeekHigh': 169.94,
                'fiftyTwoWeekLow': 143.13,
                'priceToBook': 5.1,
                'enterpriseValue': 425000000000,
                'ebitda': 28000000000,
                'currency': 'USD',
                'exchange': 'NYSE'
            },
            'JPM': {
                'symbol': 'JPM',
                'longName': 'JPMorgan Chase & Co.',
                'currentPrice': 185.75,
                'marketCap': 540000000000,
                'beta': 1.1,
                'forwardPE': 11.8,
                'trailingPE': 12.5,
                'returnOnEquity': 0.155,
                'debtToEquity': 1.12,
                'profitMargins': 0.298,
                'earningsGrowth': 0.08,
                'revenueGrowth': 0.06,
                'dividendYield': 0.024,
                'sector': 'Financial Services',
                'industry': 'Banks - Diversified',
                'fiftyTwoWeekHigh': 207.76,
                'fiftyTwoWeekLow': 155.12,
                'priceToBook': 1.8,
                'enterpriseValue': 545000000000,
                'ebitda': 65000000000,
                'currency': 'USD',
                'exchange': 'NYSE'
            }
        }
        
        # Return specific stock data or default
        return mock_stocks.get(ticker.upper(), self._get_default_stock_data(ticker))
    
    def _get_default_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Generate default stock data for unknown tickers"""
        return {
            'symbol': ticker,
            'longName': f'{ticker} Corporation',
            'currentPrice': 100.0,
            'marketCap': 50000000000,
            'beta': 1.0,
            'forwardPE': 20.0,
            'trailingPE': 22.0,
            'returnOnEquity': 0.12,
            'debtToEquity': 0.5,
            'profitMargins': 0.15,
            'earningsGrowth': 0.08,
            'revenueGrowth': 0.06,
            'dividendYield': 0.02,
            'sector': 'Unknown',
            'industry': 'Unknown',
            'fiftyTwoWeekHigh': 120.0,
            'fiftyTwoWeekLow': 80.0,
            'priceToBook': 3.0,
            'enterpriseValue': 48000000000,
            'ebitda': 8000000000,
            'currency': 'USD',
            'exchange': 'NYSE'
        }
    
    def _get_fallback_data(self, ticker: str) -> Dict[str, Any]:
        """Get fallback data when API fails"""
        return {
            'symbol': ticker,
            'error': 'Data retrieval failed',
            'fallback_data': True,
            'retrieved_at': datetime.now().isoformat()
        }
    
    def _get_mock_earnings(self, ticker: str) -> List[Dict[str, Any]]:
        """Generate mock earnings data"""
        return [
            {'year': 2024, 'revenue': 385000000000, 'earnings': 97000000000},
            {'year': 2023, 'revenue': 383000000000, 'earnings': 95000000000},
            {'year': 2022, 'revenue': 365000000000, 'earnings': 89000000000},
            {'year': 2021, 'revenue': 347000000000, 'earnings': 85000000000}
        ]
    
    def _get_mock_sector_performance(self, sector: str) -> Dict[str, Any]:
        """Generate mock sector performance data"""
        sector_performance = {
            'Technology': {'ytd_return': 0.125, 'volatility': 0.18},
            'Healthcare': {'ytd_return': 0.083, 'volatility': 0.12},
            'Financial Services': {'ytd_return': 0.067, 'volatility': 0.15},
            'Consumer Discretionary': {'ytd_return': 0.095, 'volatility': 0.20},
            'Unknown': {'ytd_return': 0.075, 'volatility': 0.16}
        }
        return sector_performance.get(sector, sector_performance['Unknown'])
    
    def _calculate_diversification_score(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate a simple diversification score for the portfolio"""
        sectors = set()
        for ticker, data in portfolio_data.items():
            sectors.add(data.get('sector', 'Unknown'))
        
        # Simple diversification score based on number of sectors
        max_sectors = 11  # GICS has 11 sectors
        return min(len(sectors) / max_sectors, 1.0)


# Create global instance
yahoo_client = YahooFinanceClient() 