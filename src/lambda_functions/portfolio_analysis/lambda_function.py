"""
Portfolio Analysis Lambda Function
Enhanced for PortfolioBot: AI Chatbot for Portfolio Analysis

Handles comprehensive portfolio analysis queries including:
- Client portfolio overview
- Performance reports (monthly/quarterly/annual)
- Holdings and transactions analysis
- Risk and analytics metrics
- Comparative analysis between clients
- Asset and sector breakdown
- Alerts and notifications
- Employee personal portfolio analysis
- Compliance and audit reports

Designed for Amazon Bedrock Agent integration with <3s response time
"""

import json
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid
import logging
import csv

from logger import get_logger
from yahoo_finance_client import yahoo_client

logging.basicConfig(level=logging.INFO)

class PortfolioAnalysisService:
    """
    Comprehensive Portfolio Analysis Service for Investment Consultants
    
    Supports all PRD-specified query types:
    1. Client Portfolio Overview
    2. Performance Reports
    3. Holdings and Transactions
    4. Risk and Analytics
    5. Comparative Analysis
    6. Asset and Sector Breakdown
    7. Alerts and Notifications
    8. Employee Personal Portfolio
    9. Compliance and Audit
    """
    
    def __init__(self):
        self.logger = get_logger("PortfolioAnalysisLambda")
        self.start_time = None
        
        # Supported analysis types
        self.supported_analysis_types = [
            'overview', 'performance', 'holdings', 'transactions', 
            'risk', 'comparison', 'sector_breakdown', 'alerts',
            'personal_portfolio', 'compliance'
        ]
        
        # Mock portfolio data for demonstration
        self.mock_portfolios = self._initialize_mock_data()
    
    def analyze_portfolio(self, analysis_type: str, user_id: str = None, 
                         employee_name: str = None, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio analysis based on query type
        
        Args:
            analysis_type: Type of analysis to perform
            user_id: User ID for user-specific queries
            employee_name: Employee name for employee-specific queries
            additional_params: Additional parameters for specific analysis types
            
        Returns:
            Comprehensive analysis results with insights and recommendations
        """
        self.start_time = time.time()
        self.logger.info(f"🚀 Starting portfolio analysis: {analysis_type} for user_id: {user_id}")
        
        try:
            # Validate inputs
            if analysis_type not in self.supported_analysis_types:
                return self._error_response(f"Unsupported analysis type: {analysis_type}")
            
            # Route to appropriate analysis method
            if analysis_type == 'overview':
                result = self._analyze_portfolio_overview(user_id, additional_params or {})
            elif analysis_type == 'performance':
                result = self._analyze_performance_report(user_id, additional_params or {})
            elif analysis_type == 'holdings':
                result = self._analyze_holdings(user_id, additional_params or {})
            elif analysis_type == 'transactions':
                result = self._analyze_transactions(user_id, additional_params or {})
            elif analysis_type == 'risk':
                result = self._analyze_risk_metrics(user_id, additional_params or {})
            elif analysis_type == 'comparison':
                result = self._analyze_comparative_performance(additional_params or {})
            elif analysis_type == 'sector_breakdown':
                result = self._analyze_sector_breakdown(user_id, additional_params or {})
            elif analysis_type == 'alerts':
                result = self._analyze_alerts_notifications(additional_params or {})
            elif analysis_type == 'personal_portfolio':
                result = self._analyze_personal_portfolio(user_id, additional_params or {})
            elif analysis_type == 'compliance':
                result = self._analyze_compliance_audit(additional_params or {})
            elif analysis_type == 'user_portfolio':
                if not user_id:
                    return self._error_response("Missing required parameter 'user_id' for user_portfolio analysis_type")
                holdings = self.get_user_portfolio_from_csv(user_id)
                return {
                    'user_id': user_id,
                    'analysis_type': 'user_portfolio',
                    'holdings': holdings,
                    'success': True
                }
            else:
                return self._error_response(f"Analysis handler not implemented: {analysis_type}")
            
            # Add performance metrics
            total_time = time.time() - self.start_time
            result['performance_metrics'] = {
                'analysis_time_seconds': round(total_time, 3),
                'timestamp': datetime.now().isoformat(),
                'analysis_type': analysis_type
            }
            
            self.logger.info(f"✅ Portfolio analysis completed in {total_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Portfolio analysis failed: {analysis_type}", error=e)
            return self._error_response(f"Analysis failed: {str(e)}")
    
    def _analyze_portfolio_overview(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze client portfolio overview using real data from customer_database.csv
        """
        self.logger.info(f"📊 Generating portfolio overview for {user_id} (real data)")
        try:
            portfolio_data = self._get_client_portfolio(user_id)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for user_id: {user_id}")
            holdings = portfolio_data['holdings']
            total_value = sum(h['QuotedValue'] for h in holdings)
            num_holdings = len(holdings)
            # Top holdings by QuotedValue
            top_holdings = sorted(holdings, key=lambda x: x['QuotedValue'], reverse=True)[:5]
            overview = {
                'user_id': user_id,
                'analysis_type': 'portfolio_overview',
                'summary': {
                    'total_portfolio_value': total_value,
                    'number_of_holdings': num_holdings,
                    'last_updated': portfolio_data.get('last_updated')
                },
                'top_holdings': top_holdings,
                'success': True
            }
            return overview
        except Exception as e:
            self.logger.error(f"Portfolio overview analysis failed for {user_id}", error=e)
            return self._error_response(f"Overview analysis failed: {str(e)}")
    
    def _analyze_performance_report(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate performance reports (monthly/quarterly/annual)
        Handles queries like: "Generate the monthly report for [user_id]"
        """
        period = params.get('period', 'monthly')  # monthly, quarterly, annual
        self.logger.info(f"📈 Generating {period} performance report for {user_id}")
        
        try:
            portfolio_data = self._get_client_portfolio(user_id)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for user_id: {user_id}")
            
            # Calculate performance metrics for the period
            performance_data = self._calculate_performance_metrics(portfolio_data, period)
            
            report = {
                'user_id': user_id,
                'analysis_type': 'performance_report',
                'report_period': period,
                'performance_summary': {
                    'period_return': performance_data['period_return'],
                    'period_return_percentage': performance_data['period_return_pct'],
                    'benchmark_return': performance_data['benchmark_return'],
                    'alpha': performance_data['alpha'],
                    'beta': performance_data['beta'],
                    'sharpe_ratio': performance_data['sharpe_ratio'],
                    'max_drawdown': performance_data['max_drawdown']
                },
                'asset_performance': performance_data['asset_performance'],
                'sector_performance': performance_data['sector_performance'],
                'key_insights': [
                    f"Portfolio outperformed benchmark by {performance_data['alpha']:.2f}%",
                    f"Best performing asset: {performance_data['best_performer']['symbol']} (+{performance_data['best_performer']['return']:.2f}%)",
                    f"Portfolio volatility: {performance_data['volatility']:.2f}%",
                    f"Risk-adjusted return (Sharpe): {performance_data['sharpe_ratio']:.2f}"
                ],
                'recommendations': self._generate_performance_recommendations(performance_data),
                'success': True
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Performance report failed for {user_id}", error=e)
            return self._error_response(f"Performance report failed: {str(e)}")
    
    def _analyze_risk_metrics(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk metrics (volatility, drawdown, Sharpe ratio)
        Handles queries like: "Show risk metrics for [user_id]'s portfolio"
        """
        self.logger.info(f"⚠️ Analyzing risk metrics for {user_id}")
        
        try:
            portfolio_data = self._get_client_portfolio(user_id)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for user_id: {user_id}")
            
            # Calculate comprehensive risk metrics
            risk_analysis = {
                'user_id': user_id,
                'analysis_type': 'risk_analysis',
                'risk_metrics': {
                    'portfolio_beta': portfolio_data.get('portfolio_beta', 1.0),
                    'sharpe_ratio': portfolio_data.get('sharpe_ratio', 0.8),
                    'volatility': portfolio_data.get('volatility', 0.15),
                    'max_drawdown': portfolio_data.get('max_drawdown', -0.08),
                    'var_95': portfolio_data.get('var_95', -0.05),  # Value at Risk
                    'sortino_ratio': portfolio_data.get('sortino_ratio', 1.2)
                },
                'risk_breakdown_by_asset': self._calculate_asset_risk_contribution(portfolio_data),
                'risk_assessment': self._assess_portfolio_risk_level(portfolio_data),
                'risk_alerts': self._identify_risk_alerts(portfolio_data),
                'recommendations': [
                    "Consider rebalancing if any single position exceeds 10% of portfolio",
                    "Monitor high-beta positions during market volatility",
                    "Review correlation between major holdings"
                ],
                'success': True
            }
            
            return risk_analysis
            
        except Exception as e:
            self.logger.error(f"Risk analysis failed for {user_id}", error=e)
            return self._error_response(f"Risk analysis failed: {str(e)}")
    
    def _analyze_comparative_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare performance between clients or against benchmarks
        Handles queries like: "Compare performance between [user_id1] and [user_id2]"
        """
        user_id1 = params.get('user_id1')
        user_id2 = params.get('user_id2')
        
        self.logger.info(f"📊 Comparing performance: {user_id1} vs {user_id2}")
        
        try:
            portfolio1 = self._get_client_portfolio(user_id1)
            portfolio2 = self._get_client_portfolio(user_id2)
            
            if not portfolio1 or not portfolio2:
                return self._error_response("One or both client portfolios not found")
            
            comparison = {
                'analysis_type': 'comparative_analysis',
                'clients_compared': [user_id1, user_id2],
                'performance_comparison': {
                    user_id1: {
                        'total_return': portfolio1.get('total_return', 0.12),
                        'sharpe_ratio': portfolio1.get('sharpe_ratio', 0.8),
                        'volatility': portfolio1.get('volatility', 0.15),
                        'max_drawdown': portfolio1.get('max_drawdown', -0.08)
                    },
                    user_id2: {
                        'total_return': portfolio2.get('total_return', 0.10),
                        'sharpe_ratio': portfolio2.get('sharpe_ratio', 0.9),
                        'volatility': portfolio2.get('volatility', 0.12),
                        'max_drawdown': portfolio2.get('max_drawdown', -0.06)
                    }
                },
                'winner_analysis': self._determine_performance_winner(portfolio1, portfolio2, user_id1, user_id2),
                'key_differences': self._identify_portfolio_differences(portfolio1, portfolio2),
                'success': True
            }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Comparative analysis failed", error=e)
            return self._error_response(f"Comparative analysis failed: {str(e)}")
    
    def _analyze_sector_breakdown(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sector allocation and performance
        Handles queries like: "Show sector allocation for [user_id]'s portfolio"
        """
        self.logger.info(f"🏭 Analyzing sector breakdown for {user_id}")
        
        try:
            portfolio_data = self._get_client_portfolio(user_id)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for user_id: {user_id}")
            
            sector_analysis = {
                'user_id': user_id,
                'analysis_type': 'sector_breakdown',
                'sector_allocation': self._calculate_sector_allocation(portfolio_data['holdings']),
                'sector_performance': self._calculate_sector_performance(portfolio_data['holdings']),
                'sector_insights': [
                    "Technology sector represents largest allocation",
                    "Healthcare showing strongest year-to-date performance",
                    "Consider reducing concentration in any sector >25%"
                ],
                'rebalancing_suggestions': self._generate_sector_rebalancing_suggestions(portfolio_data),
                'success': True
            }
            
            return sector_analysis
            
        except Exception as e:
            self.logger.error(f"Sector analysis failed for {user_id}", error=e)
            return self._error_response(f"Sector analysis failed: {str(e)}")
    
    def _analyze_alerts_notifications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate alerts and notifications for portfolio monitoring
        Handles queries like: "Which clients need portfolio rebalancing?"
        """
        threshold = params.get('threshold', 0.05)  # 5% default threshold
        
        self.logger.info(f"🚨 Generating portfolio alerts with {threshold*100}% threshold")
        
        try:
            alerts = {
                'analysis_type': 'alerts_notifications',
                'alert_threshold': threshold,
                'portfolio_alerts': [],
                'rebalancing_needed': [],
                'risk_alerts': [],
                'performance_alerts': [],
                'generated_at': datetime.now().isoformat(),
                'success': True
            }
            
            # Check all mock portfolios for alerts
            for user_id, portfolio in self.mock_portfolios.items():
                # Portfolio value change alerts
                recent_change = portfolio.get('recent_change_pct', 0)
                if abs(recent_change) > threshold:
                    alerts['portfolio_alerts'].append({
                        'user_id': user_id,
                        'alert_type': 'significant_change',
                        'change_percentage': recent_change,
                        'message': f"Portfolio changed by {recent_change:.2f}% recently"
                    })
                
                # Rebalancing alerts
                if self._needs_rebalancing(portfolio):
                    alerts['rebalancing_needed'].append({
                        'user_id': user_id,
                        'reason': 'Asset allocation drift detected',
                        'priority': 'medium'
                    })
                
                # Risk alerts
                if portfolio.get('portfolio_beta', 1.0) > 1.5:
                    alerts['risk_alerts'].append({
                        'user_id': user_id,
                        'alert_type': 'high_beta',
                        'beta_value': portfolio.get('portfolio_beta', 1.0),
                        'message': 'Portfolio beta exceeds risk tolerance'
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Alerts analysis failed", error=e)
            return self._error_response(f"Alerts analysis failed: {str(e)}")
    
    def _analyze_personal_portfolio(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query customer_database.csv for the user's holdings and return Instrument, Amount, Price, QuotedValue.
        """
        self.logger.info(f"🔍 Querying personal portfolio for {user_id} (real data)")
        try:
            portfolio_data = self._get_client_portfolio(user_id)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for user_id: {user_id}")
            holdings = portfolio_data['holdings']
            return {
                'user_id': user_id,
                'analysis_type': 'personal_portfolio',
                'holdings': holdings,
                'success': True
            }
        except Exception as e:
            self.logger.error(f"Personal portfolio query failed for {user_id}", error=e)
            return self._error_response(f"Personal portfolio query failed: {str(e)}")
    
    def _analyze_compliance_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate compliance and audit reports
        Handles queries like: "List any unusual transactions in client portfolios this month"
        """
        period = params.get('period', 'monthly')
        
        self.logger.info(f"🔍 Generating compliance audit for {period} period")
        
        try:
            compliance_report = {
                'analysis_type': 'compliance_audit',
                'audit_period': period,
                'unusual_transactions': [
                    {
                        'user_id': 'John Smith',
                        'transaction_type': 'large_sale',
                        'amount': 500000,
                        'symbol': 'AAPL',
                        'date': '2025-01-10',
                        'flag_reason': 'Exceeds normal transaction size'
                    }
                ],
                'compliance_alerts': [
                    {
                        'user_id': 'Sarah Johnson',
                        'alert_type': 'concentration_risk',
                        'description': 'Single position exceeds 15% of portfolio'
                    }
                ],
                'regulatory_checks': {
                    'position_limits': 'All within limits',
                    'insider_trading_flags': 'None detected',
                    'wash_sale_violations': 'None detected'
                },
                'recommendations': [
                    "Review large transactions with clients",
                    "Monitor concentration risks monthly",
                    "Update compliance procedures for new regulations"
                ],
                'success': True
            }
            
            return compliance_report
            
        except Exception as e:
            self.logger.error(f"Compliance audit failed", error=e)
            return self._error_response(f"Compliance audit failed: {str(e)}")
    
    # Helper methods for calculations and data processing
    
    def _get_client_portfolio(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get portfolio data for a specific user_id from customer_database.csv.
        Returns a dict with 'holdings' (list of holdings) and summary info.
        """
        csv_path = os.path.join(os.path.dirname(__file__), 'database', 'customer_database.csv')
        holdings = []
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if str(row['user_id']).strip() == str(user_id).strip():
                        holdings.append({
                            'Instrument': row['Instrument'].strip(),
                            'Amount': float(row['Amount']),
                            'Price': float(row['Price']),
                            'QuotedValue': float(row['QuotedValue'])
                        })
            if not holdings:
                return None
            return {
                'user_id': user_id,
                'holdings': holdings,
                'last_updated': holdings[0].get('ReportingDate', None) if holdings else None
            }
        except Exception as e:
            self.logger.error(f"Error reading customer_database.csv for user_id {user_id}", error=e)
            return None
    
    def _calculate_sector_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sector allocation percentages"""
        sector_values = {}
        total_value = sum(holding['market_value'] for holding in holdings)
        
        for holding in holdings:
            sector = holding.get('sector', 'Other')
            sector_values[sector] = sector_values.get(sector, 0) + holding['market_value']
        
        return {sector: round((value / total_value) * 100, 2) 
                for sector, value in sector_values.items()}
    
    def _calculate_performance_metrics(self, portfolio_data: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Calculate performance metrics for a given period"""
        return {
            'period_return': 12500,
            'period_return_pct': 8.5,
            'benchmark_return': 7.2,
            'alpha': 1.3,
            'beta': portfolio_data.get('portfolio_beta', 1.0),
            'sharpe_ratio': portfolio_data.get('sharpe_ratio', 0.8),
            'max_drawdown': portfolio_data.get('max_drawdown', -0.08),
            'volatility': portfolio_data.get('volatility', 0.15),
            'asset_performance': [],
            'sector_performance': {},
            'best_performer': {'symbol': 'AAPL', 'return': 15.2}
        }
    
    def _generate_portfolio_insights(self, portfolio_data: Dict[str, Any], total_return_pct: float) -> List[str]:
        """Generate actionable insights for portfolio"""
        insights = []
        
        if total_return_pct > 10:
            insights.append("Portfolio is performing well above market average")
        elif total_return_pct < 0:
            insights.append("Portfolio is experiencing losses - consider reviewing allocation")
        
        if portfolio_data.get('portfolio_beta', 1.0) > 1.2:
            insights.append("Portfolio has high market sensitivity - consider defensive positions")
        
        insights.append("Regular rebalancing recommended to maintain target allocation")
        
        return insights
    
    def _initialize_mock_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mock portfolio data for demonstration"""
        return {
            'John Smith': {
                'user_id': 'CLI001',
                'total_value': 250000,
                'portfolio_beta': 1.1,
                'sharpe_ratio': 0.85,
                'volatility': 0.16,
                'max_drawdown': -0.09,
                'total_return': 0.12,
                'recent_change_pct': 0.03,
                'holdings': [
                    {
                        'symbol': 'AAPL',
                        'name': 'Apple Inc.',
                        'shares': 100,
                        'market_value': 18000,
                        'unrealized_gain_loss': 2000,
                        'sector': 'Technology'
                    },
                    {
                        'symbol': 'MSFT',
                        'name': 'Microsoft Corp.',
                        'shares': 50,
                        'market_value': 15000,
                        'unrealized_gain_loss': 1500,
                        'sector': 'Technology'
                    },
                    {
                        'symbol': 'JNJ',
                        'name': 'Johnson & Johnson',
                        'shares': 80,
                        'market_value': 12000,
                        'unrealized_gain_loss': 800,
                        'sector': 'Healthcare'
                    }
                ],
                'last_updated': datetime.now().isoformat()
            },
            'Sarah Johnson': {
                'user_id': 'CLI002',
                'total_value': 180000,
                'portfolio_beta': 0.9,
                'sharpe_ratio': 1.1,
                'volatility': 0.12,
                'max_drawdown': -0.06,
                'total_return': 0.10,
                'recent_change_pct': -0.02,
                'holdings': [
                    {
                        'symbol': 'GOOGL',
                        'name': 'Alphabet Inc.',
                        'shares': 25,
                        'market_value': 35000,
                        'unrealized_gain_loss': 3000,
                        'sector': 'Technology'
                    },
                    {
                        'symbol': 'JPM',
                        'name': 'JPMorgan Chase',
                        'shares': 60,
                        'market_value': 8000,
                        'unrealized_gain_loss': 500,
                        'sector': 'Financial'
                    }
                ],
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'error'
        }
    
    # Additional helper methods for specific calculations
    def _calculate_asset_risk_contribution(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate risk contribution by asset"""
        return [
            {'symbol': 'AAPL', 'risk_contribution': 0.25, 'beta': 1.2},
            {'symbol': 'MSFT', 'risk_contribution': 0.20, 'beta': 0.9}
        ]
    
    def _assess_portfolio_risk_level(self, portfolio_data: Dict[str, Any]) -> str:
        """Assess overall portfolio risk level"""
        beta = portfolio_data.get('portfolio_beta', 1.0)
        if beta > 1.3:
            return 'High Risk'
        elif beta > 1.1:
            return 'Moderate Risk'
        else:
            return 'Conservative'
    
    def _identify_risk_alerts(self, portfolio_data: Dict[str, Any]) -> List[str]:
        """Identify specific risk alerts"""
        alerts = []
        if portfolio_data.get('max_drawdown', 0) < -0.15:
            alerts.append('High maximum drawdown detected')
        if portfolio_data.get('volatility', 0) > 0.25:
            alerts.append('High volatility levels')
        return alerts
    
    def _needs_rebalancing(self, portfolio: Dict[str, Any]) -> bool:
        """Check if portfolio needs rebalancing"""
        # Simple check - in real implementation would compare to target allocation
        return portfolio.get('total_value', 0) > 200000  # Mock logic
    
    def _calculate_sector_performance(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance by sector"""
        return {
            'Technology': 12.5,
            'Healthcare': 8.3,
            'Financial': 6.7
        }
    
    def _generate_sector_rebalancing_suggestions(self, portfolio_data: Dict[str, Any]) -> List[str]:
        """Generate sector rebalancing suggestions"""
        return [
            "Consider reducing Technology allocation from 65% to 50%",
            "Increase Healthcare exposure to 20%",
            "Add defensive sectors like Utilities"
        ]
    
    def _determine_performance_winner(self, portfolio1: Dict, portfolio2: Dict, 
                                    user_id1: str, user_id2: str) -> Dict[str, Any]:
        """Determine which portfolio performed better"""
        return1 = portfolio1.get('total_return', 0)
        return2 = portfolio2.get('total_return', 0)
        
        winner = user_id1 if return1 > return2 else user_id2
        return {
            'winner': winner,
            'margin': abs(return1 - return2),
            'reason': f'Higher total return: {max(return1, return2):.2f}%'
        }
    
    def _identify_portfolio_differences(self, portfolio1: Dict, portfolio2: Dict) -> List[str]:
        """Identify key differences between portfolios"""
        return [
            "Portfolio 1 has higher technology allocation",
            "Portfolio 2 shows lower volatility",
            "Different risk profiles: aggressive vs conservative"
        ]
    
    def _generate_performance_recommendations(self, performance_data: Dict[str, Any]) -> List[str]:
        """Generate performance-based recommendations"""
        return [
            "Continue current strategy - performance is strong",
            "Consider taking profits on best performers",
            "Monitor market conditions for rebalancing opportunities"
        ]

    def get_user_portfolio_from_csv(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Query customer_database.csv for all holdings of a given user_id.
        Returns a list of dicts with Instrument, Amount, Price, QuotedValue.
        """
        csv_path = os.path.join(os.path.dirname(__file__), 'database', 'customer_database.csv')
        results = []
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if str(row['user_id']).strip() == str(user_id).strip():
                        results.append({
                            'Instrument': row['Instrument'].strip(),
                            'Amount': float(row['Amount']),
                            'Price': float(row['Price']),
                            'QuotedValue': float(row['QuotedValue'])
                        })
            return results
        except Exception as e:
            self.logger.error(f"Error reading customer_database.csv for user_id {user_id}", error=e)
            return []


def extract_param(param):
    if isinstance(param, dict) and "value" in param:
        return param["value"]
    return param


def lambda_handler(event, context):
    """
    AWS Lambda handler for portfolio analysis requests,
    optimized for Amazon Bedrock Agent integration.
    """
    logger = get_logger("PortfolioAnalysisHandler")
    print(f"DEBUG: Full event received by Lambda: {json.dumps(event, indent=2)}")

    # Extract Bedrock Agent specific metadata
    actionGroup = event.get('actionGroup', 'PortfolioAnalysisActionGroup')
    function = event.get('function', 'analyzePortfolio')
    messageVersion = event.get('messageVersion', '1.0')

    try:
        analysis_type = 'overview'  # Default analysis type
        user_id = None
        employee_name = None
        additional_params = {}
        request_id = event.get('requestId', f'req-{int(time.time())}')

        # 1. Try to extract 'analysis_type' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'analysis_type' and param.get('value') is not None:
                    analysis_type = str(param['value']).lower().strip()
                    break
        
        # 2. If 'analysis_type' is still not found, try to extract from direct key
        if event.get('analysis_type') is not None:
            analysis_type = str(event['analysis_type']).lower().strip()

        # 3. Try to extract 'user_id' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'user_id' and param.get('value') is not None:
                    user_id = str(param['value']).strip()
                    break
        
        # 4. If 'user_id' is still not found, try to extract from direct key
        if event.get('user_id') is not None:
            user_id = str(event['user_id']).strip()

        # 5. Try to extract 'employee_name' from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                if param.get('name') == 'employee_name' and param.get('value') is not None:
                    employee_name = str(param['value']).strip()
                    break
        
        # 6. If 'employee_name' is still not found, try to extract from direct key
        if event.get('employee_name') is not None:
            employee_name = str(event['employee_name']).strip()

        # 7. Try to extract additional parameters from 'parameters' list (Bedrock Agent format)
        if 'parameters' in event and isinstance(event['parameters'], list):
            for param in event['parameters']:
                param_name = param.get('name')
                param_value = param.get('value')
                
                if param_name and param_value is not None:
                    if param_name in ['period', 'user_id1', 'user_id2', 'threshold']:
                        additional_params[param_name] = param_value
                    elif param_name == 'threshold':
                        # Convert threshold to float if it's a number
                        try:
                            additional_params[param_name] = float(param_value)
                        except (ValueError, TypeError):
                            additional_params[param_name] = param_value

        # 8. If additional_params is still empty, try to extract from direct key
        if event.get('additional_params') is not None:
            additional_params.update(event['additional_params'])

        print(f"DEBUG: Analysis Type: '{analysis_type}', User_id: '{user_id}', Employee: '{employee_name}', Additional Params: {additional_params}")

        logger.info(f"🚀 Processing portfolio analysis request", 
                   context={
                       'requestId': request_id, 
                       'analysis_type': analysis_type, 
                       'user_id': user_id,
                       'employee_name': employee_name
                   })
        
        # Initialize service
        service = PortfolioAnalysisService()
        
        # Simple validation: user_id required for most analysis types
        client_required_types = ['overview', 'performance', 'holdings', 'transactions', 'risk', 'sector_breakdown']
        
        if analysis_type in client_required_types and not user_id:
            error_msg = f"Missing required parameter 'user_id' for analysis_type '{analysis_type}'"
            logger.error(f"LAMBDA ERROR: {error_msg}")
            
            error_response = {
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
            
            # Wrap error details in the Bedrock Agent expected format
            responseBody_for_error = {
                "TEXT": {
                    "body": json.dumps(error_response, default=str)
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

        # Perform analysis
        result = service.analyze_portfolio(
            analysis_type=analysis_type,
            user_id=user_id,
            employee_name=employee_name,
            additional_params=additional_params
        )
        
        # Log the outgoing response for debugging
        logger.info("LAMBDA RESPONSE: %s", json.dumps(result))
        
        # Handle cases where the result indicates an error
        if not result.get("success", True):
            logger.error("LAMBDA ERROR: %s", json.dumps(result))
            
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
        
        logger.info(f"Portfolio analysis request successful: {analysis_type}")
        print(f"DEBUG: Final Lambda success response: {json.dumps(final_response, indent=2)}")
        return final_response
        
    except Exception as e:
        logger.error(f"❌ Portfolio Analysis Lambda handler failed", 
                    context={'requestId': event.get('requestId', 'unknown')}, 
                    error=e)
        
        # Create an instance to generate standardized error response
        service = PortfolioAnalysisService()
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


# Test function for local development
if __name__ == "__main__":
    print("AWS Chatbot Portfolio Analysis Tool - Local Demonstration")
    print("=" * 60)
    
    # Test cases for local demonstration, simulating Bedrock Agent input
    test_events_bedrock_format = [
        # Bedrock Agent style event for portfolio overview
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioAnalysisActionGroup",
            "function": "analyzePortfolio",
            "parameters": [
                {"name": "analysis_type", "value": "overview"},
                {"name": "user_id", "value": "CLI001"}
            ],
            "sessionId": "test-session-123",
            "invocationId": "test-invocation-123",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-001"
        },
        # Bedrock Agent style event for performance analysis
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioAnalysisActionGroup",
            "function": "analyzePortfolio",
            "parameters": [
                {"name": "analysis_type", "value": "performance"},
                {"name": "user_id", "value": "CLI002"},
                {"name": "period", "value": "monthly"}
            ],
            "sessionId": "test-session-456",
            "invocationId": "test-invocation-456",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-002"
        },
        # Bedrock Agent style event for risk analysis
        {
            "messageVersion": "1.0",
            "actionGroup": "PortfolioAnalysisActionGroup",
            "function": "analyzePortfolio",
            "parameters": [
                {"name": "analysis_type", "value": "risk"},
                {"name": "user_id", "value": "CLI001"}
            ],
            "sessionId": "test-session-789",
            "invocationId": "test-invocation-789",
            "apiPath": "/",
            "httpMethod": "POST",
            "requestId": "test-req-003"
        },
        # Direct Lambda console test style event
        {"analysis_type": "overview", "user_id": "CLI001", "requestId": "test-req-004"},
        {"analysis_type": "sector_breakdown", "user_id": "CLI002", "requestId": "test-req-005"},
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
                        print(f"Analysis Type: {parsed_body.get('analysis_type', 'N/A')}")
                        if 'user_id' in parsed_body:
                            print(f"User_id: {parsed_body.get('user_id')}")
                        if 'summary' in parsed_body:
                            summary = parsed_body['summary']
                            print(f"Portfolio Value: ${summary.get('total_portfolio_value', 'N/A'):,}")
                            print(f"Total Return: {summary.get('total_return_percentage', 'N/A')}%")
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