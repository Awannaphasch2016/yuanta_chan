"""
Investment Metrics Lambda Function
Implements Hybrid Analysis Algorithm: Essential metrics + contextual analysis
Designed for Amazon Bedrock Agent integration
"""

import json
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.logger import get_logger
from common.yahoo_finance_client import yahoo_client
from typing import Dict, Any, Optional


class InvestmentAnalyzer:
    """
    Hybrid investment analysis implementation
    Phase 1: Core metrics (fast, reliable)
    Phase 2: Contextual analysis (when available)
    Phase 3: Generate recommendation
    """
    
    def __init__(self):
        self.logger = get_logger("InvestmentMetricsLambda")
        self.core_metrics = ['forwardPE', 'returnOnEquity', 'debtToEquity', 'profitMargins']
        self.context_sources = ['sector', 'industry', 'beta', 'earningsGrowth']
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Perform hybrid investment analysis on a stock ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing analysis results and recommendation
        """
        try:
            self.logger.info(f"Starting investment analysis for {ticker}")
            
            # Phase 1: Core metrics (fast, reliable)
            core_data = self._extract_core_metrics(ticker)
            if not core_data:
                return {
                    'ticker': ticker,
                    'success': False,
                    'error': 'Unable to retrieve basic stock data',
                    'recommendation': 'Unable to analyze - data unavailable'
                }
            
            # Phase 2: Contextual analysis (when available)
            context_data = self._extract_context(ticker, core_data)
            
            # Phase 3: Generate recommendation
            recommendation = self._generate_recommendation(core_data, context_data)
            
            result = {
                'ticker': ticker,
                'success': True,
                'analysis': {
                    'core_metrics': core_data,
                    'context_analysis': context_data,
                    'recommendation': recommendation
                },
                'timestamp': core_data.get('retrieved_at')
            }
            
            self.logger.info(f"Investment analysis completed for {ticker}")
            return result
            
        except Exception as e:
            self.logger.error(f"Investment analysis failed for {ticker}", error=e)
            return {
                'ticker': ticker,
                'success': False,
                'error': str(e),
                'recommendation': 'Unable to analyze due to error'
            }
    
    def _extract_core_metrics(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Extract essential financial metrics"""
        try:
            stock_data = yahoo_client.get_stock_info(ticker)
            
            core_data = {
                'name': stock_data.get('name'),
                'currentPrice': stock_data.get('currentPrice'),
                'forwardPE': stock_data.get('forwardPE'),
                'returnOnEquity': stock_data.get('returnOnEquity'),
                'debtToEquity': stock_data.get('debtToEquity'),
                'profitMargins': stock_data.get('profitMargins'),
                'retrieved_at': stock_data.get('retrieved_at')
            }
            
            self.logger.info(f"Core metrics extracted for {ticker}")
            return core_data
            
        except Exception as e:
            self.logger.error(f"Core metrics extraction failed for {ticker}", error=e)
            return None
    
    def _extract_context(self, ticker: str, core_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contextual analysis when available"""
        context = {}
        
        try:
            stock_data = yahoo_client.get_stock_info(ticker)
            
            context = {
                'sector': stock_data.get('sector'),
                'industry': stock_data.get('industry'),
                'beta': stock_data.get('beta'),
                'earningsGrowth': stock_data.get('earningsGrowth'),
                'revenueGrowth': stock_data.get('revenueGrowth'),
                'marketCap': stock_data.get('marketCap'),
                'dividendYield': stock_data.get('dividendYield')
            }
            
            # Add contextual insights
            context['risk_assessment'] = self._assess_risk(stock_data)
            context['growth_profile'] = self._assess_growth(stock_data)
            
            self.logger.info(f"Context analysis completed for {ticker}")
            
        except Exception as e:
            self.logger.warning(f"Context analysis failed for {ticker}", error=e)
            context['error'] = 'Contextual data unavailable'
        
        return context
    
    def _assess_risk(self, stock_data: Dict[str, Any]) -> str:
        """Assess risk level based on available metrics"""
        beta = stock_data.get('beta')
        debt_to_equity = stock_data.get('debtToEquity')
        
        if beta is None and debt_to_equity is None:
            return 'Unable to assess risk - insufficient data'
        
        risk_factors = []
        
        if beta is not None:
            if beta > 1.5:
                risk_factors.append('High volatility')
            elif beta > 1.0:
                risk_factors.append('Moderate volatility')
            else:
                risk_factors.append('Low volatility')
        
        if debt_to_equity is not None:
            if debt_to_equity > 100:
                risk_factors.append('High debt levels')
            elif debt_to_equity > 50:
                risk_factors.append('Moderate debt levels')
            else:
                risk_factors.append('Conservative debt levels')
        
        return ', '.join(risk_factors) if risk_factors else 'Moderate risk'
    
    def _assess_growth(self, stock_data: Dict[str, Any]) -> str:
        """Assess growth profile based on available metrics"""
        earnings_growth = stock_data.get('earningsGrowth')
        revenue_growth = stock_data.get('revenueGrowth')
        
        if earnings_growth is None and revenue_growth is None:
            return 'Growth data unavailable'
        
        growth_indicators = []
        
        if earnings_growth is not None:
            if earnings_growth > 0.15:
                growth_indicators.append('Strong earnings growth')
            elif earnings_growth > 0.05:
                growth_indicators.append('Moderate earnings growth')
            else:
                growth_indicators.append('Limited earnings growth')
        
        if revenue_growth is not None:
            if revenue_growth > 0.10:
                growth_indicators.append('Strong revenue growth')
            elif revenue_growth > 0.03:
                growth_indicators.append('Moderate revenue growth')
            else:
                growth_indicators.append('Limited revenue growth')
        
        return ', '.join(growth_indicators) if growth_indicators else 'Stable growth profile'
    
    def _generate_recommendation(self, core_data: Dict[str, Any], 
                               context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendation based on hybrid analysis"""
        
        # Extract key metrics
        forward_pe = core_data.get('forwardPE')
        roe = core_data.get('returnOnEquity')
        debt_to_equity = core_data.get('debtToEquity')
        profit_margins = core_data.get('profitMargins')
        
        # Scoring system
        score = 0
        max_score = 0
        rationale = []
        
        # Forward P/E analysis
        if forward_pe is not None:
            max_score += 25
            if forward_pe < 15:
                score += 25
                rationale.append("Attractive valuation (low P/E)")
            elif forward_pe < 25:
                score += 15
                rationale.append("Reasonable valuation")
            else:
                score += 5
                rationale.append("High valuation (high P/E)")
        
        # ROE analysis
        if roe is not None:
            max_score += 25
            if roe > 0.15:
                score += 25
                rationale.append("Excellent profitability (high ROE)")
            elif roe > 0.10:
                score += 15
                rationale.append("Good profitability")
            else:
                score += 5
                rationale.append("Lower profitability")
        
        # Debt analysis
        if debt_to_equity is not None:
            max_score += 25
            if debt_to_equity < 30:
                score += 25
                rationale.append("Conservative debt levels")
            elif debt_to_equity < 60:
                score += 15
                rationale.append("Moderate debt levels")
            else:
                score += 5
                rationale.append("High debt levels")
        
        # Profit margins analysis
        if profit_margins is not None:
            max_score += 25
            if profit_margins > 0.20:
                score += 25
                rationale.append("Excellent profit margins")
            elif profit_margins > 0.10:
                score += 15
                rationale.append("Good profit margins")
            else:
                score += 5
                rationale.append("Lower profit margins")
        
        # Calculate final score percentage
        if max_score > 0:
            score_percentage = (score / max_score) * 100
        else:
            score_percentage = 50  # Neutral if no data
        
        # Generate recommendation
        if score_percentage >= 80:
            recommendation = "Strong Buy"
            summary = "Excellent financial metrics across multiple indicators"
        elif score_percentage >= 65:
            recommendation = "Buy"
            summary = "Good financial fundamentals with positive indicators"
        elif score_percentage >= 50:
            recommendation = "Hold"
            summary = "Mixed signals with some positive and negative factors"
        elif score_percentage >= 35:
            recommendation = "Weak Hold"
            summary = "Below-average fundamentals with some concerns"
        else:
            recommendation = "Sell"
            summary = "Poor financial metrics across multiple indicators"
        
        # Add contextual insights if available
        if context_data.get('risk_assessment'):
            rationale.append(f"Risk profile: {context_data['risk_assessment']}")
        
        if context_data.get('growth_profile'):
            rationale.append(f"Growth outlook: {context_data['growth_profile']}")
        
        return {
            'recommendation': recommendation,
            'score': round(score_percentage, 1),
            'summary': summary,
            'rationale': rationale,
            'confidence': 'High' if max_score >= 75 else 'Medium' if max_score >= 50 else 'Low'
        }


# Lambda handler function
def lambda_handler(event, context):
    """
    AWS Lambda handler for investment metrics analysis
    
    Expected event format:
    {
        "ticker": "AAPL",
        "requestId": "optional-request-id"
    }
    """
    logger = get_logger("InvestmentMetricsLambda")
    
    try:
        # Extract parameters from event
        ticker = event.get('ticker')
        request_id = event.get('requestId', 'unknown')
        
        logger.info(f"Processing investment analysis request", 
                   context={'requestId': request_id, 'ticker': ticker})
        
        if not ticker:
            raise ValueError("Missing required parameter: ticker")
        
        # Perform analysis
        analyzer = InvestmentAnalyzer()
        result = analyzer.analyze(ticker)
        
        # Format response for Bedrock Agent
        response = {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        logger.info(f"Investment analysis completed successfully", 
                   context={'requestId': request_id, 'ticker': ticker})
        return response
        
    except Exception as e:
        logger.error(f"Lambda execution failed", 
                    context={'requestId': event.get('requestId', 'unknown')}, 
                    error=e)
        
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'ticker': event.get('ticker', 'unknown')
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        return error_response


# For local testing
if __name__ == "__main__":
    test_event = {
        "ticker": "AAPL",
        "requestId": "test-request-001"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2)) 