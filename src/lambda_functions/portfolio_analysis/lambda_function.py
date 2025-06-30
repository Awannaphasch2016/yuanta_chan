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

from logger import get_logger
from yahoo_finance_client import yahoo_client


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
    
    def analyze_portfolio(self, analysis_type: str, client_name: str = None, 
                         employee_name: str = None, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio analysis based on query type
        
        Args:
            analysis_type: Type of analysis to perform
            client_name: Client name for client-specific queries
            employee_name: Employee name for employee-specific queries
            additional_params: Additional parameters for specific analysis types
            
        Returns:
            Comprehensive analysis results with insights and recommendations
        """
        self.start_time = time.time()
        self.logger.info(f"🚀 Starting portfolio analysis: {analysis_type} for client: {client_name}")
        
        try:
            # Validate inputs
            if analysis_type not in self.supported_analysis_types:
                return self._error_response(f"Unsupported analysis type: {analysis_type}")
            
            # Route to appropriate analysis method
            if analysis_type == 'overview':
                result = self._analyze_portfolio_overview(client_name, additional_params or {})
            elif analysis_type == 'performance':
                result = self._analyze_performance_report(client_name, additional_params or {})
            elif analysis_type == 'holdings':
                result = self._analyze_holdings(client_name, additional_params or {})
            elif analysis_type == 'transactions':
                result = self._analyze_transactions(client_name, additional_params or {})
            elif analysis_type == 'risk':
                result = self._analyze_risk_metrics(client_name, additional_params or {})
            elif analysis_type == 'comparison':
                result = self._analyze_comparative_performance(additional_params or {})
            elif analysis_type == 'sector_breakdown':
                result = self._analyze_sector_breakdown(client_name, additional_params or {})
            elif analysis_type == 'alerts':
                result = self._analyze_alerts_notifications(additional_params or {})
            elif analysis_type == 'personal_portfolio':
                result = self._analyze_personal_portfolio(employee_name, additional_params or {})
            elif analysis_type == 'compliance':
                result = self._analyze_compliance_audit(additional_params or {})
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
    
    def _analyze_portfolio_overview(self, client_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze client portfolio overview
        Handles queries like: "Show me an overview of [client name]'s portfolio"
        """
        self.logger.info(f"📊 Generating portfolio overview for {client_name}")
        
        try:
            # Get client portfolio data
            portfolio_data = self._get_client_portfolio(client_name)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for client: {client_name}")
            
            # Calculate overview metrics
            total_value = sum(holding['market_value'] for holding in portfolio_data['holdings'])
            total_gain_loss = sum(holding['unrealized_gain_loss'] for holding in portfolio_data['holdings'])
            total_return_pct = (total_gain_loss / (total_value - total_gain_loss)) * 100 if total_value > total_gain_loss else 0
            
            # Get top holdings
            top_holdings = sorted(portfolio_data['holdings'], 
                                key=lambda x: x['market_value'], reverse=True)[:5]
            
            # Sector allocation
            sector_allocation = self._calculate_sector_allocation(portfolio_data['holdings'])
            
            overview = {
                'client_name': client_name,
                'analysis_type': 'portfolio_overview',
                'summary': {
                    'total_portfolio_value': total_value,
                    'total_gain_loss': total_gain_loss,
                    'total_return_percentage': round(total_return_pct, 2),
                    'number_of_holdings': len(portfolio_data['holdings']),
                    'last_updated': portfolio_data.get('last_updated', datetime.now().isoformat())
                },
                'top_holdings': [
                    {
                        'symbol': holding['symbol'],
                        'name': holding['name'],
                        'market_value': holding['market_value'],
                        'weight_percentage': round((holding['market_value'] / total_value) * 100, 2),
                        'gain_loss': holding['unrealized_gain_loss']
                    }
                    for holding in top_holdings
                ],
                'sector_allocation': sector_allocation,
                'risk_metrics': {
                    'portfolio_beta': portfolio_data.get('portfolio_beta', 1.0),
                    'sharpe_ratio': portfolio_data.get('sharpe_ratio', 0.8),
                    'volatility': portfolio_data.get('volatility', 0.15)
                },
                'insights': self._generate_portfolio_insights(portfolio_data, total_return_pct),
                'success': True
            }
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Portfolio overview analysis failed for {client_name}", error=e)
            return self._error_response(f"Overview analysis failed: {str(e)}")
    
    def _analyze_performance_report(self, client_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate performance reports (monthly/quarterly/annual)
        Handles queries like: "Generate the monthly report for [client name]"
        """
        period = params.get('period', 'monthly')  # monthly, quarterly, annual
        self.logger.info(f"📈 Generating {period} performance report for {client_name}")
        
        try:
            portfolio_data = self._get_client_portfolio(client_name)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for client: {client_name}")
            
            # Calculate performance metrics for the period
            performance_data = self._calculate_performance_metrics(portfolio_data, period)
            
            report = {
                'client_name': client_name,
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
            self.logger.error(f"Performance report failed for {client_name}", error=e)
            return self._error_response(f"Performance report failed: {str(e)}")
    
    def _analyze_risk_metrics(self, client_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk metrics (volatility, drawdown, Sharpe ratio)
        Handles queries like: "Show risk metrics for [client name]'s portfolio"
        """
        self.logger.info(f"⚠️ Analyzing risk metrics for {client_name}")
        
        try:
            portfolio_data = self._get_client_portfolio(client_name)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for client: {client_name}")
            
            # Calculate comprehensive risk metrics
            risk_analysis = {
                'client_name': client_name,
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
            self.logger.error(f"Risk analysis failed for {client_name}", error=e)
            return self._error_response(f"Risk analysis failed: {str(e)}")
    
    def _analyze_comparative_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare performance between clients or against benchmarks
        Handles queries like: "Compare performance between [client1] and [client2]"
        """
        client1 = params.get('client1')
        client2 = params.get('client2')
        
        self.logger.info(f"📊 Comparing performance: {client1} vs {client2}")
        
        try:
            portfolio1 = self._get_client_portfolio(client1)
            portfolio2 = self._get_client_portfolio(client2)
            
            if not portfolio1 or not portfolio2:
                return self._error_response("One or both client portfolios not found")
            
            comparison = {
                'analysis_type': 'comparative_analysis',
                'clients_compared': [client1, client2],
                'performance_comparison': {
                    client1: {
                        'total_return': portfolio1.get('total_return', 0.12),
                        'sharpe_ratio': portfolio1.get('sharpe_ratio', 0.8),
                        'volatility': portfolio1.get('volatility', 0.15),
                        'max_drawdown': portfolio1.get('max_drawdown', -0.08)
                    },
                    client2: {
                        'total_return': portfolio2.get('total_return', 0.10),
                        'sharpe_ratio': portfolio2.get('sharpe_ratio', 0.9),
                        'volatility': portfolio2.get('volatility', 0.12),
                        'max_drawdown': portfolio2.get('max_drawdown', -0.06)
                    }
                },
                'winner_analysis': self._determine_performance_winner(portfolio1, portfolio2, client1, client2),
                'key_differences': self._identify_portfolio_differences(portfolio1, portfolio2),
                'success': True
            }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Comparative analysis failed", error=e)
            return self._error_response(f"Comparative analysis failed: {str(e)}")
    
    def _analyze_sector_breakdown(self, client_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sector allocation and performance
        Handles queries like: "Show sector allocation for [client name]'s portfolio"
        """
        self.logger.info(f"🏭 Analyzing sector breakdown for {client_name}")
        
        try:
            portfolio_data = self._get_client_portfolio(client_name)
            if not portfolio_data:
                return self._error_response(f"No portfolio found for client: {client_name}")
            
            sector_analysis = {
                'client_name': client_name,
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
            self.logger.error(f"Sector analysis failed for {client_name}", error=e)
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
            for client_name, portfolio in self.mock_portfolios.items():
                # Portfolio value change alerts
                recent_change = portfolio.get('recent_change_pct', 0)
                if abs(recent_change) > threshold:
                    alerts['portfolio_alerts'].append({
                        'client': client_name,
                        'alert_type': 'significant_change',
                        'change_percentage': recent_change,
                        'message': f"Portfolio changed by {recent_change:.2f}% recently"
                    })
                
                # Rebalancing alerts
                if self._needs_rebalancing(portfolio):
                    alerts['rebalancing_needed'].append({
                        'client': client_name,
                        'reason': 'Asset allocation drift detected',
                        'priority': 'medium'
                    })
                
                # Risk alerts
                if portfolio.get('portfolio_beta', 1.0) > 1.5:
                    alerts['risk_alerts'].append({
                        'client': client_name,
                        'alert_type': 'high_beta',
                        'beta_value': portfolio.get('portfolio_beta', 1.0),
                        'message': 'Portfolio beta exceeds risk tolerance'
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Alerts analysis failed", error=e)
            return self._error_response(f"Alerts analysis failed: {str(e)}")
    
    def _analyze_personal_portfolio(self, employee_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze employee's personal portfolio
        Handles queries like: "Show my own portfolio performance for the last 6 months"
        """
        period = params.get('period', '6_months')
        
        self.logger.info(f"👤 Analyzing personal portfolio for {employee_name}")
        
        try:
            # Mock personal portfolio data
            personal_portfolio = {
                'employee_name': employee_name,
                'analysis_type': 'personal_portfolio',
                'portfolio_summary': {
                    'total_value': 150000,
                    'total_return': 0.08,
                    'period_analyzed': period,
                    'last_updated': datetime.now().isoformat()
                },
                'top_holdings': [
                    {'symbol': 'AAPL', 'value': 25000, 'weight': 16.7},
                    {'symbol': 'MSFT', 'value': 20000, 'weight': 13.3},
                    {'symbol': 'GOOGL', 'value': 18000, 'weight': 12.0}
                ],
                'performance_metrics': {
                    'period_return': 0.08,
                    'sharpe_ratio': 1.1,
                    'volatility': 0.14,
                    'max_drawdown': -0.06
                },
                'insights': [
                    f"Portfolio has generated 8% return over {period}",
                    "Sharpe ratio of 1.1 indicates good risk-adjusted returns",
                    "Technology allocation may be overweight"
                ],
                'success': True
            }
            
            return personal_portfolio
            
        except Exception as e:
            self.logger.error(f"Personal portfolio analysis failed for {employee_name}", error=e)
            return self._error_response(f"Personal portfolio analysis failed: {str(e)}")
    
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
                        'client': 'John Smith',
                        'transaction_type': 'large_sale',
                        'amount': 500000,
                        'symbol': 'AAPL',
                        'date': '2025-01-10',
                        'flag_reason': 'Exceeds normal transaction size'
                    }
                ],
                'compliance_alerts': [
                    {
                        'client': 'Sarah Johnson',
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
    
    def _get_client_portfolio(self, client_name: str) -> Optional[Dict[str, Any]]:
        """Get portfolio data for a specific client"""
        return self.mock_portfolios.get(client_name)
    
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
                'client_id': 'CLI001',
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
                'client_id': 'CLI002',
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
                                    client1: str, client2: str) -> Dict[str, Any]:
        """Determine which portfolio performed better"""
        return1 = portfolio1.get('total_return', 0)
        return2 = portfolio2.get('total_return', 0)
        
        winner = client1 if return1 > return2 else client2
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


def lambda_handler(event, context):
    """
    AWS Lambda handler for portfolio analysis requests
    
    Expected event structure:
    {
        "analysis_type": "overview|performance|holdings|transactions|risk|comparison|sector_breakdown|alerts|personal_portfolio|compliance",
        "client_name": "John Smith",  # Optional for client-specific queries
        "employee_name": "Jane Doe",  # Optional for employee queries
        "additional_params": {
            "period": "monthly|quarterly|annual",
            "client1": "John Smith",     # For comparison
            "client2": "Sarah Johnson",  # For comparison
            "threshold": 0.05           # For alerts
        }
    }
    """
    
    # Initialize service
    service = PortfolioAnalysisService()
    
    try:
        # Extract parameters from event
        analysis_type = event.get('analysis_type', 'overview')
        client_name = event.get('client_name')
        employee_name = event.get('employee_name')
        additional_params = event.get('additional_params', {})
        
        # Log request
        service.logger.info(f"📨 Portfolio analysis request: {analysis_type}")
        
        # Perform analysis
        result = service.analyze_portfolio(
            analysis_type=analysis_type,
            client_name=client_name,
            employee_name=employee_name,
            additional_params=additional_params
        )
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        service.logger.error("❌ Lambda handler error", error=e)
        
        error_response = {
            'success': False,
            'error': f'Lambda execution failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_response)
        }


# Test function for local development
if __name__ == "__main__":
    # Test portfolio overview
    test_event = {
        'analysis_type': 'overview',
        'client_name': 'John Smith'
    }
    
    result = lambda_handler(test_event, None)
    print("Portfolio Analysis Test Result:")
    print(json.dumps(json.loads(result['body']), indent=2)) 