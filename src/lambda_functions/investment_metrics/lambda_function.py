"""
Investment Metrics Lambda Function - Sequential Processing Algorithm
Enhanced for AWS Chatbot Board Demonstration
Implements: Essential metrics → Enhanced analysis → Recommendation generation
Designed for Amazon Bedrock Agent integration with <2s response time
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.logger import get_logger
from common.yahoo_finance_client import yahoo_client


class SequentialInvestmentAnalyzer:
    """
    Sequential Processing Algorithm for Investment Analysis
    
    Phase 1: Essential Metrics (always executed, <0.5s)
    Phase 2: Enhanced Analysis (conditional, <1.0s total)
    Phase 3: Recommendation Generation (<1.5s total)
    
    Designed for board demonstration of AWS chatbot capabilities
    """
    
    def __init__(self):
        self.logger = get_logger("InvestmentMetricsLambda")
        self.start_time = None
        self.phase_times = {}
        
        # Essential metrics for Phase 1 (fast, reliable)
        self.essential_metrics = [
            'currentPrice', 'forwardPE', 'returnOnEquity', 
            'debtToEquity', 'profitMargins', 'marketCap'
        ]
        
        # Enhanced metrics for Phase 2 (when time permits)
        self.enhanced_metrics = [
            'beta', 'earningsGrowth', 'revenueGrowth', 'dividendYield',
            'sector', 'industry', 'trailingPE', 'priceToBook'
        ]
    
    def analyze(self, ticker: str, depth: str = "standard") -> Dict[str, Any]:
        """
        Perform sequential investment analysis optimized for board demonstration
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            depth: Analysis depth ('quick', 'standard', 'detailed')
            
        Returns:
            Comprehensive analysis results with performance metrics
        """
        self.start_time = time.time()
        self.logger.info(f"🚀 Starting sequential analysis for {ticker} (depth: {depth})")
        
        try:
            # Phase 1: Essential Metrics (ALWAYS EXECUTED)
            phase1_start = time.time()
            essential_data = self._phase1_essential_metrics(ticker)
            self.phase_times['phase1'] = time.time() - phase1_start
            
            if not essential_data['success']:
                return self._format_error_response(ticker, essential_data['error'])
            
            # Phase 2: Enhanced Analysis (CONDITIONAL)
            phase2_start = time.time()
            enhanced_data = self._phase2_enhanced_analysis(ticker, depth)
            self.phase_times['phase2'] = time.time() - phase2_start
            
            # Phase 3: Recommendation Generation
            phase3_start = time.time()
            recommendation = self._phase3_generate_recommendation(
                essential_data['data'], enhanced_data, ticker
            )
            self.phase_times['phase3'] = time.time() - phase3_start
            
            # Format final response with performance metrics
            total_time = time.time() - self.start_time
            return self._format_success_response(
                ticker, essential_data['data'], enhanced_data, 
                recommendation, total_time
            )
            
        except Exception as e:
            self.logger.error(f"❌ Sequential analysis failed for {ticker}", error=e)
            return self._format_error_response(ticker, str(e))
    
    def _phase1_essential_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        Phase 1: Extract essential financial metrics (target: <0.5s)
        This phase ALWAYS executes and provides core investment data
        """
        self.logger.info(f"📊 Phase 1: Extracting essential metrics for {ticker}")
        
        try:
            # Get core stock data
            stock_data = yahoo_client.get_stock_info(ticker)
            
            if not stock_data:
                return {
                    'success': False,
                    'error': f'No data available for ticker {ticker}'
                }
            
            # Extract essential metrics
            essential_data = {
                'company_name': stock_data.get('longName', ticker),
                'current_price': stock_data.get('currentPrice'),
                'forward_pe': stock_data.get('forwardPE'),
                'return_on_equity': stock_data.get('returnOnEquity'),
                'debt_to_equity': stock_data.get('debtToEquity'),
                'profit_margins': stock_data.get('profitMargins'),
                'market_cap': stock_data.get('marketCap'),
                'currency': stock_data.get('currency', 'USD'),
                'exchange': stock_data.get('exchange'),
                'retrieved_at': datetime.now().isoformat()
            }
            
            # Validate essential data
            data_quality = self._assess_data_quality(essential_data)
            
            self.logger.info(f"✅ Phase 1 completed for {ticker} (quality: {data_quality}%)")
            
            return {
                'success': True,
                'data': essential_data,
                'data_quality': data_quality
            }
            
        except Exception as e:
            self.logger.error(f"❌ Phase 1 failed for {ticker}", error=e)
            return {
                'success': False,
                'error': f'Failed to retrieve essential metrics: {str(e)}'
            }
    
    def _phase2_enhanced_analysis(self, ticker: str, depth: str) -> Dict[str, Any]:
        """
        Phase 2: Enhanced analysis with market context (conditional execution)
        Executes based on depth parameter and available time
        """
        # Skip enhanced analysis for 'quick' depth or if Phase 1 took too long
        elapsed_time = time.time() - self.start_time
        if depth == 'quick' or elapsed_time > 0.8:
            self.logger.info(f"⏭️ Phase 2: Skipped for {ticker} (depth: {depth}, elapsed: {elapsed_time:.2f}s)")
            return {'executed': False, 'reason': 'Skipped for performance'}
        
        self.logger.info(f"🔍 Phase 2: Enhanced analysis for {ticker}")
        
        try:
            # Get additional stock data
            stock_data = yahoo_client.get_stock_info(ticker)
            
            enhanced_data = {
                'sector': stock_data.get('sector'),
                'industry': stock_data.get('industry'),
                'beta': stock_data.get('beta'),
                'earnings_growth': stock_data.get('earningsGrowth'),
                'revenue_growth': stock_data.get('revenueGrowth'),
                'dividend_yield': stock_data.get('dividendYield'),
                'trailing_pe': stock_data.get('trailingPE'),
                'price_to_book': stock_data.get('priceToBook'),
                'fifty_two_week_high': stock_data.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': stock_data.get('fiftyTwoWeekLow')
            }
            
            # Add analytical insights
            enhanced_data['risk_assessment'] = self._assess_risk_profile(stock_data)
            enhanced_data['growth_analysis'] = self._assess_growth_profile(stock_data)
            enhanced_data['valuation_analysis'] = self._assess_valuation(stock_data)
            
            self.logger.info(f"✅ Phase 2 completed for {ticker}")
            
            return {
                'executed': True,
                'data': enhanced_data
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Phase 2 failed for {ticker}", error=e)
            return {
                'executed': False,
                'error': str(e)
            }
    
    def _phase3_generate_recommendation(self, essential_data: Dict[str, Any], 
                                      enhanced_data: Dict[str, Any], 
                                      ticker: str) -> Dict[str, Any]:
        """
        Phase 3: Generate investment recommendation with clear rationale
        Designed for board presentation with professional analysis
        """
        self.logger.info(f"🎯 Phase 3: Generating recommendation for {ticker}")
        
        try:
            # Initialize scoring system
            score = 0
            max_score = 0
            rationale = []
            risk_factors = []
            opportunities = []
            
            # Analyze essential metrics
            valuation_score, valuation_rationale = self._score_valuation(essential_data)
            profitability_score, profitability_rationale = self._score_profitability(essential_data)
            financial_health_score, financial_health_rationale = self._score_financial_health(essential_data)
            
            score += valuation_score + profitability_score + financial_health_score
            max_score += 75  # 25 points each for valuation, profitability, financial health
            
            rationale.extend(valuation_rationale)
            rationale.extend(profitability_rationale)
            rationale.extend(financial_health_rationale)
            
            # Add enhanced analysis if available
            if enhanced_data.get('executed'):
                growth_score, growth_rationale = self._score_growth(enhanced_data['data'])
                score += growth_score
                max_score += 25
                rationale.extend(growth_rationale)
                
                # Extract risk factors and opportunities
                risk_factors = self._identify_risk_factors(enhanced_data['data'])
                opportunities = self._identify_opportunities(enhanced_data['data'])
            
            # Calculate final score and recommendation
            final_score = (score / max_score * 100) if max_score > 0 else 50
            recommendation_data = self._determine_recommendation(final_score, rationale)
            
            # Add board-ready summary
            board_summary = self._generate_board_summary(
                ticker, essential_data, enhanced_data, recommendation_data, final_score
            )
            
            result = {
                'recommendation': recommendation_data['action'],
                'confidence': recommendation_data['confidence'],
                'score': round(final_score, 1),
                'summary': recommendation_data['summary'],
                'detailed_rationale': rationale,
                'risk_factors': risk_factors,
                'opportunities': opportunities,
                'board_summary': board_summary
            }
            
            self.logger.info(f"✅ Phase 3 completed for {ticker} - {recommendation_data['action']}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Phase 3 failed for {ticker}", error=e)
            return {
                'recommendation': 'Unable to analyze',
                'confidence': 'Low',
                'score': 0,
                'summary': f'Analysis failed: {str(e)}',
                'detailed_rationale': [],
                'risk_factors': ['Analysis error'],
                'opportunities': [],
                'board_summary': f'Unable to complete analysis for {ticker} due to technical error.'
            }
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> int:
        """Assess the quality of retrieved data (0-100%)"""
        total_fields = len(self.essential_metrics)
        available_fields = sum(1 for field in self.essential_metrics 
                             if data.get(field.replace('_', '')) is not None)
        return int((available_fields / total_fields) * 100)
    
    def _assess_risk_profile(self, stock_data: Dict[str, Any]) -> str:
        """Assess overall risk profile"""
        beta = stock_data.get('beta')
        debt_to_equity = stock_data.get('debtToEquity')
        
        risk_level = 'Moderate'
        
        if beta is not None and debt_to_equity is not None:
            if beta > 1.5 or debt_to_equity > 100:
                risk_level = 'High'
            elif beta < 0.8 and debt_to_equity < 30:
                risk_level = 'Low'
        
        return risk_level
    
    def _assess_growth_profile(self, stock_data: Dict[str, Any]) -> str:
        """Assess growth profile"""
        earnings_growth = stock_data.get('earningsGrowth')
        revenue_growth = stock_data.get('revenueGrowth')
        
        if earnings_growth is not None and earnings_growth > 0.15:
            return 'High Growth'
        elif earnings_growth is not None and earnings_growth > 0.05:
            return 'Moderate Growth'
        else:
            return 'Stable/Mature'
    
    def _assess_valuation(self, stock_data: Dict[str, Any]) -> str:
        """Assess valuation level"""
        forward_pe = stock_data.get('forwardPE')
        
        if forward_pe is None:
            return 'Unable to assess'
        elif forward_pe < 15:
            return 'Undervalued'
        elif forward_pe < 25:
            return 'Fairly Valued'
        else:
            return 'Overvalued'
    
    def _score_valuation(self, data: Dict[str, Any]) -> tuple:
        """Score valuation metrics"""
        forward_pe = data.get('forward_pe')
        score = 0
        rationale = []
        
        if forward_pe is not None:
            if forward_pe < 15:
                score = 25
                rationale.append(f"Attractive valuation with P/E of {forward_pe:.1f}")
            elif forward_pe < 25:
                score = 15
                rationale.append(f"Reasonable valuation with P/E of {forward_pe:.1f}")
            else:
                score = 5
                rationale.append(f"High valuation with P/E of {forward_pe:.1f}")
        else:
            rationale.append("P/E ratio not available for valuation assessment")
        
        return score, rationale
    
    def _score_profitability(self, data: Dict[str, Any]) -> tuple:
        """Score profitability metrics"""
        roe = data.get('return_on_equity')
        profit_margins = data.get('profit_margins')
        score = 0
        rationale = []
        
        if roe is not None:
            if roe > 0.15:
                score += 15
                rationale.append(f"Excellent ROE of {roe*100:.1f}%")
            elif roe > 0.10:
                score += 10
                rationale.append(f"Good ROE of {roe*100:.1f}%")
            else:
                score += 5
                rationale.append(f"Moderate ROE of {roe*100:.1f}%")
        
        if profit_margins is not None:
            if profit_margins > 0.20:
                score += 10
                rationale.append(f"Excellent profit margins of {profit_margins*100:.1f}%")
            elif profit_margins > 0.10:
                score += 7
                rationale.append(f"Good profit margins of {profit_margins*100:.1f}%")
            else:
                score += 3
                rationale.append(f"Moderate profit margins of {profit_margins*100:.1f}%")
        
        return score, rationale
    
    def _score_financial_health(self, data: Dict[str, Any]) -> tuple:
        """Score financial health metrics"""
        debt_to_equity = data.get('debt_to_equity')
        score = 0
        rationale = []
        
        if debt_to_equity is not None:
            if debt_to_equity < 30:
                score = 25
                rationale.append(f"Conservative debt levels (D/E: {debt_to_equity:.1f})")
            elif debt_to_equity < 60:
                score = 15
                rationale.append(f"Moderate debt levels (D/E: {debt_to_equity:.1f})")
            else:
                score = 5
                rationale.append(f"High debt levels (D/E: {debt_to_equity:.1f})")
        else:
            rationale.append("Debt-to-equity ratio not available")
        
        return score, rationale
    
    def _score_growth(self, enhanced_data: Dict[str, Any]) -> tuple:
        """Score growth metrics"""
        earnings_growth = enhanced_data.get('earnings_growth')
        score = 0
        rationale = []
        
        if earnings_growth is not None:
            if earnings_growth > 0.15:
                score = 25
                rationale.append(f"Strong earnings growth of {earnings_growth*100:.1f}%")
            elif earnings_growth > 0.05:
                score = 15
                rationale.append(f"Moderate earnings growth of {earnings_growth*100:.1f}%")
            else:
                score = 5
                rationale.append(f"Limited earnings growth of {earnings_growth*100:.1f}%")
        
        return score, rationale
    
    def _identify_risk_factors(self, enhanced_data: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        risks = []
        
        beta = enhanced_data.get('beta')
        if beta is not None and beta > 1.5:
            risks.append(f"High volatility (Beta: {beta:.2f})")
        
        sector = enhanced_data.get('sector')
        if sector in ['Technology', 'Biotechnology']:
            risks.append(f"Sector volatility ({sector})")
        
        return risks
    
    def _identify_opportunities(self, enhanced_data: Dict[str, Any]) -> List[str]:
        """Identify key opportunities"""
        opportunities = []
        
        earnings_growth = enhanced_data.get('earnings_growth')
        if earnings_growth is not None and earnings_growth > 0.10:
            opportunities.append(f"Strong earnings growth trajectory ({earnings_growth*100:.1f}%)")
        
        dividend_yield = enhanced_data.get('dividend_yield')
        if dividend_yield is not None and dividend_yield > 0.03:
            opportunities.append(f"Attractive dividend yield ({dividend_yield*100:.1f}%)")
        
        return opportunities
    
    def _determine_recommendation(self, score: float, rationale: List[str]) -> Dict[str, Any]:
        """Determine final investment recommendation"""
        if score >= 80:
            return {
                'action': 'Strong Buy',
                'confidence': 'High',
                'summary': 'Excellent financial metrics with strong fundamentals across multiple indicators'
            }
        elif score >= 65:
            return {
                'action': 'Buy',
                'confidence': 'High',
                'summary': 'Good financial fundamentals with positive investment indicators'
            }
        elif score >= 50:
            return {
                'action': 'Hold',
                'confidence': 'Medium',
                'summary': 'Mixed signals with balanced positive and negative factors'
            }
        elif score >= 35:
            return {
                'action': 'Weak Hold',
                'confidence': 'Medium',
                'summary': 'Below-average fundamentals with some areas of concern'
            }
        else:
            return {
                'action': 'Sell',
                'confidence': 'High',
                'summary': 'Poor financial metrics indicating significant investment risks'
            }
    
    def _generate_board_summary(self, ticker: str, essential_data: Dict[str, Any], 
                              enhanced_data: Dict[str, Any], recommendation_data: Dict[str, Any], 
                              score: float) -> str:
        """Generate executive summary for board presentation"""
        company_name = essential_data.get('company_name', ticker)
        current_price = essential_data.get('current_price')
        
        summary = f"Investment Analysis: {company_name} ({ticker})\n"
        summary += f"Current Price: ${current_price:.2f} | " if current_price else ""
        summary += f"Recommendation: {recommendation_data['action']} | "
        summary += f"Confidence: {recommendation_data['confidence']} | "
        summary += f"Score: {score:.1f}/100\n\n"
        summary += f"Executive Summary: {recommendation_data['summary']}\n\n"
        
        if enhanced_data.get('executed'):
            sector = enhanced_data['data'].get('sector')
            if sector:
                summary += f"Sector: {sector}\n"
        
        summary += "This analysis demonstrates our AWS-powered chatbot's ability to provide "
        summary += "institutional-grade investment analysis in real-time."
        
        return summary
    
    def _format_success_response(self, ticker: str, essential_data: Dict[str, Any], 
                               enhanced_data: Dict[str, Any], recommendation: Dict[str, Any], 
                               total_time: float) -> Dict[str, Any]:
        """Format successful analysis response"""
        return {
            'ticker': ticker,
            'success': True,
            'analysis': {
                'essential_metrics': essential_data,
                'enhanced_analysis': enhanced_data,
                'recommendation': recommendation
            },
            'performance': {
                'total_execution_time': round(total_time, 3),
                'phase_times': {k: round(v, 3) for k, v in self.phase_times.items()},
                'algorithm': 'Sequential Processing',
                'phases_executed': len([k for k, v in self.phase_times.items() if v > 0])
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0-sequential',
                'optimized_for': 'board_demonstration'
            }
        }
    
    def _format_error_response(self, ticker: str, error: str) -> Dict[str, Any]:
        """Format error response"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            'ticker': ticker,
            'success': False,
            'error': error,
            'recommendation': {
                'recommendation': 'Unable to analyze',
                'confidence': 'Low',
                'summary': f'Analysis failed for {ticker}: {error}'
            },
            'performance': {
                'total_execution_time': round(total_time, 3),
                'algorithm': 'Sequential Processing',
                'status': 'Failed'
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0-sequential'
            }
        }


# Lambda handler function
def lambda_handler(event, context):
    """
    AWS Lambda handler for sequential investment analysis
    Optimized for board demonstration of AWS chatbot capabilities
    
    Expected event format:
    {
        "ticker": "AAPL",
        "depth": "standard",  // "quick", "standard", "detailed"
        "requestId": "optional-request-id"
    }
    """
    logger = get_logger("InvestmentMetricsLambda")
    
    try:
        # Extract parameters from event
        ticker = event.get('ticker', '').upper()
        depth = event.get('depth', 'standard')
        request_id = event.get('requestId', f'req-{int(time.time())}')
        
        logger.info(f"🚀 Processing sequential investment analysis", 
                   context={
                       'requestId': request_id, 
                       'ticker': ticker, 
                       'depth': depth,
                       'algorithm': 'Sequential Processing'
                   })
        
        if not ticker:
            raise ValueError("Missing required parameter: ticker")
        
        if depth not in ['quick', 'standard', 'detailed']:
            depth = 'standard'
            logger.warning(f"Invalid depth parameter, defaulting to 'standard'")
        
        # Perform sequential analysis
        analyzer = SequentialInvestmentAnalyzer()
        result = analyzer.analyze(ticker, depth)
        
        # Format response for Bedrock Agent
        response = {
            'statusCode': 200,
            'body': json.dumps(result, default=str),
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': request_id,
                'X-Algorithm': 'Sequential-Processing',
                'X-Execution-Time': str(result.get('performance', {}).get('total_execution_time', 0))
            }
        }
        
        execution_time = result.get('performance', {}).get('total_execution_time', 0)
        logger.info(f"✅ Sequential investment analysis completed successfully", 
                   context={
                       'requestId': request_id, 
                       'ticker': ticker,
                       'executionTime': execution_time,
                       'recommendation': result.get('analysis', {}).get('recommendation', {}).get('recommendation', 'Unknown')
                   })
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Lambda execution failed", 
                    context={'requestId': event.get('requestId', 'unknown')}, 
                    error=e)
        
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'ticker': event.get('ticker', 'unknown'),
                'algorithm': 'Sequential Processing',
                'timestamp': datetime.now().isoformat()
            }),
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': event.get('requestId', 'unknown')
            }
        }
        
        return error_response


# For local testing and board demonstration
if __name__ == "__main__":
    # Test cases for board demonstration
    test_cases = [
        {"ticker": "AAPL", "depth": "detailed", "requestId": "board-demo-001"},
        {"ticker": "MSFT", "depth": "standard", "requestId": "board-demo-002"},
        {"ticker": "GOOGL", "depth": "quick", "requestId": "board-demo-003"}
    ]
    
    print("AWS Chatbot Investment Analysis - Board Demonstration")
    print("=" * 60)
    
    for i, test_event in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_event['ticker']} ({test_event['depth']} analysis)")
        print("-" * 40)
        
        result = lambda_handler(test_event, None)
        
        if result['statusCode'] == 200:
            data = json.loads(result['body'])
            if data['success']:
                analysis = data['analysis']
                perf = data['performance']
                
                print(f"Success: {analysis['recommendation']['recommendation']}")
                print(f"Execution Time: {perf['total_execution_time']}s")
            else:
                print(f"Failed: {data['error']}")
        else:
            print(f"HTTP Error: {result['statusCode']}")
    
    print("=" * 60)
    print("Board Demonstration Complete - AWS Chatbot Ready!")
if __name__ == "__main__":
    # Test cases for board demonstration
    test_cases = [
        {"ticker": "AAPL", "depth": "detailed", "requestId": "board-demo-001"},
        {"ticker": "MSFT", "depth": "standard", "requestId": "board-demo-002"},
        {"ticker": "GOOGL", "depth": "quick", "requestId": "board-demo-003"}
    ]
    
    print("🎯 AWS Chatbot Investment Analysis - Board Demonstration")
    print("=" * 60)
    
    for i, test_event in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {test_event['ticker']} ({test_event['depth']} analysis)")
        print("-" * 40)
        
        result = lambda_handler(test_event, None)
        
        if result['statusCode'] == 200:
            data = json.loads(result['body'])
            if data['success']:
                analysis = data['analysis']
                perf = data['performance']
                
                print(f"✅ Success: {analysis['recommendation']['recommendation']}")
                print(f"⏱️  Execution Time: {perf['total_execution_time']}s")
                print(f"📈 Score: {analysis['recommendation']['score']}/100")
                print(f"🎯 Board Summary:")
                print(analysis['recommendation']['board_summary'])
            else:
                print(f"❌ Failed: {data['error']}")
        else:
            print(f"❌ HTTP Error: {result['statusCode']}")
    
    print("\n" + "=" * 60)
    print("🚀 Board Demonstration Complete - AWS Chatbot Ready!") 