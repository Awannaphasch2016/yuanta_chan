"""
Unit tests for Portfolio Analysis Lambda function.
Tests comprehensive portfolio analysis capabilities including overview, performance, risk, and comparative analysis.
"""

import unittest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "portfolio_analysis"))

from lambda_function import PortfolioAnalysisService, lambda_handler, extract_param


class TestPortfolioAnalysisService(unittest.TestCase):
    """Test cases for PortfolioAnalysisService class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.service = PortfolioAnalysisService()
    
    def test_service_initialization(self):
        """Test service initialization and supported analysis types."""
        service = PortfolioAnalysisService()
        self.assertIsNotNone(service)
        self.assertIsNotNone(service.logger)
        self.assertIsNotNone(service.mock_portfolios)
        
        # Check supported analysis types
        expected_types = [
            'overview', 'performance', 'holdings', 'transactions', 
            'risk', 'comparison', 'sector_breakdown', 'alerts',
            'personal_portfolio', 'compliance'
        ]
        self.assertEqual(service.supported_analysis_types, expected_types)
    
    def test_error_response_format(self):
        """Test error response format."""
        error_msg = "Test error message"
        result = self.service._error_response(error_msg)
        
        self.assertIn("success", result)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], error_msg)
        self.assertIn("timestamp", result)
        self.assertEqual(result["analysis_type"], "error")
    
    def test_mock_data_initialization(self):
        """Test mock portfolio data initialization."""
        portfolios = self.service.mock_portfolios
        
        # Check that mock data exists
        self.assertIn("John Smith", portfolios)
        self.assertIn("Sarah Johnson", portfolios)
        
        # Check John Smith portfolio structure
        john_portfolio = portfolios["John Smith"]
        self.assertEqual(john_portfolio["client_id"], "CLI001")
        self.assertEqual(john_portfolio["total_value"], 250000)
        self.assertIn("holdings", john_portfolio)
        self.assertGreater(len(john_portfolio["holdings"]), 0)
        
        # Check Sarah Johnson portfolio structure
        sarah_portfolio = portfolios["Sarah Johnson"]
        self.assertEqual(sarah_portfolio["client_id"], "CLI002")
        self.assertEqual(sarah_portfolio["total_value"], 180000)
        self.assertIn("holdings", sarah_portfolio)
        self.assertGreater(len(sarah_portfolio["holdings"]), 0)
    
    def test_get_client_portfolio(self):
        """Test client portfolio retrieval."""
        # Test valid client
        john_portfolio = self.service._get_client_portfolio("John Smith")
        self.assertIsNotNone(john_portfolio)
        self.assertEqual(john_portfolio["client_id"], "CLI001")
        
        # Test invalid client
        invalid_portfolio = self.service._get_client_portfolio("Nonexistent Client")
        self.assertIsNone(invalid_portfolio)
    
    def test_portfolio_overview_analysis(self):
        """Test portfolio overview analysis."""
        result = self.service.analyze_portfolio("overview", "John Smith")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "portfolio_overview")
        self.assertEqual(result["client_name"], "John Smith")
        
        # Check summary data
        self.assertIn("summary", result)
        summary = result["summary"]
        self.assertIn("total_portfolio_value", summary)
        self.assertIn("total_gain_loss", summary)
        self.assertIn("total_return_percentage", summary)
        self.assertIn("number_of_holdings", summary)
        
        # Check top holdings
        self.assertIn("top_holdings", result)
        self.assertGreater(len(result["top_holdings"]), 0)
        
        # Check sector allocation
        self.assertIn("sector_allocation", result)
        
        # Check risk metrics
        self.assertIn("risk_metrics", result)
        
        # Check insights
        self.assertIn("insights", result)
        
        # Check performance metrics
        self.assertIn("performance_metrics", result)
        self.assertIn("analysis_time_seconds", result["performance_metrics"])
    
    def test_portfolio_overview_invalid_client(self):
        """Test portfolio overview with invalid client."""
        result = self.service.analyze_portfolio("overview", "Nonexistent Client")
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("No portfolio found", result["error"])
    
    def test_performance_report_analysis(self):
        """Test performance report analysis."""
        result = self.service.analyze_portfolio("performance", "John Smith", 
                                              additional_params={"period": "monthly"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "performance_report")
        self.assertEqual(result["client_name"], "John Smith")
        self.assertEqual(result["report_period"], "monthly")
        
        # Check performance summary
        self.assertIn("performance_summary", result)
        summary = result["performance_summary"]
        self.assertIn("period_return", summary)
        self.assertIn("period_return_percentage", summary)
        self.assertIn("benchmark_return", summary)
        self.assertIn("alpha", summary)
        self.assertIn("beta", summary)
        self.assertIn("sharpe_ratio", summary)
        self.assertIn("max_drawdown", summary)
        
        # Check asset and sector performance
        self.assertIn("asset_performance", result)
        self.assertIn("sector_performance", result)
        
        # Check insights and recommendations
        self.assertIn("key_insights", result)
        self.assertIn("recommendations", result)
    
    def test_risk_metrics_analysis(self):
        """Test risk metrics analysis."""
        result = self.service.analyze_portfolio("risk", "John Smith")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "risk_analysis")
        self.assertEqual(result["client_name"], "John Smith")
        
        # Check risk metrics
        self.assertIn("risk_metrics", result)
        risk_metrics = result["risk_metrics"]
        self.assertIn("portfolio_beta", risk_metrics)
        self.assertIn("sharpe_ratio", risk_metrics)
        self.assertIn("volatility", risk_metrics)
        self.assertIn("max_drawdown", risk_metrics)
        self.assertIn("var_95", risk_metrics)
        self.assertIn("sortino_ratio", risk_metrics)
        
        # Check risk assessment
        self.assertIn("risk_assessment", result)
        self.assertIn("risk_alerts", result)
        self.assertIn("risk_breakdown_by_asset", result)
    
    def test_comparative_performance_analysis(self):
        """Test comparative performance analysis."""
        params = {
            "client1": "John Smith",
            "client2": "Sarah Johnson"
        }
        result = self.service.analyze_portfolio("comparison", additional_params=params)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "comparative_analysis")
        
        # Check comparison data
        self.assertIn("clients_compared", result)
        self.assertIn("performance_comparison", result)
        self.assertIn("winner_analysis", result)
        self.assertIn("key_differences", result)
    
    def test_sector_breakdown_analysis(self):
        """Test sector breakdown analysis."""
        result = self.service.analyze_portfolio("sector_breakdown", "John Smith")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "sector_breakdown")
        self.assertEqual(result["client_name"], "John Smith")
        
        # Check sector data
        self.assertIn("sector_allocation", result)
        self.assertIn("sector_performance", result)
        self.assertIn("rebalancing_suggestions", result)
        self.assertIn("sector_insights", result)
    
    def test_alerts_notifications_analysis(self):
        """Test alerts and notifications analysis."""
        result = self.service.analyze_portfolio("alerts")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "alerts_notifications")
        
        # Check alerts data
        self.assertIn("portfolio_alerts", result)
        self.assertIn("risk_alerts", result)
        self.assertIn("performance_alerts", result)
        self.assertIn("rebalancing_needed", result)
        self.assertIn("alert_threshold", result)
    
    def test_personal_portfolio_analysis(self):
        """Test personal portfolio analysis."""
        result = self.service.analyze_portfolio("personal_portfolio", employee_name="Jane Doe")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "personal_portfolio")
        self.assertEqual(result["employee_name"], "Jane Doe")
        
        # Check personal portfolio data
        self.assertIn("portfolio_summary", result)
        self.assertIn("top_holdings", result)
        self.assertIn("insights", result)
    
    def test_compliance_audit_analysis(self):
        """Test compliance and audit analysis."""
        result = self.service.analyze_portfolio("compliance")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "compliance_audit")
        
        # Check compliance data
        self.assertIn("audit_period", result)
        self.assertIn("regulatory_checks", result)
        self.assertIn("unusual_transactions", result)
        self.assertIn("compliance_alerts", result)
        self.assertIn("recommendations", result)
    
    def test_unsupported_analysis_type(self):
        """Test unsupported analysis type."""
        result = self.service.analyze_portfolio("unsupported_type", "John Smith")
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("Unsupported analysis type", result["error"])
    
    def test_calculate_sector_allocation(self):
        """Test sector allocation calculation."""
        holdings = [
            {"symbol": "AAPL", "market_value": 10000, "sector": "Technology"},
            {"symbol": "JNJ", "market_value": 5000, "sector": "Healthcare"},
            {"symbol": "JPM", "market_value": 5000, "sector": "Financial"}
        ]
        
        allocation = self.service._calculate_sector_allocation(holdings)
        
        self.assertIn("Technology", allocation)
        self.assertIn("Healthcare", allocation)
        self.assertIn("Financial", allocation)
        
        # Check percentages sum to 100
        total_percentage = sum(allocation.values())
        self.assertAlmostEqual(total_percentage, 100.0, places=1)
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation."""
        portfolio_data = self.service._get_client_portfolio("John Smith")
        metrics = self.service._calculate_performance_metrics(portfolio_data, "monthly")
        
        self.assertIn("period_return", metrics)
        self.assertIn("period_return_pct", metrics)
        self.assertIn("benchmark_return", metrics)
        self.assertIn("alpha", metrics)
        self.assertIn("beta", metrics)
        self.assertIn("sharpe_ratio", metrics)
        self.assertIn("max_drawdown", metrics)
        self.assertIn("volatility", metrics)
        self.assertIn("asset_performance", metrics)
        self.assertIn("sector_performance", metrics)
        self.assertIn("best_performer", metrics)
    
    def test_portfolio_insights_generation(self):
        """Test portfolio insights generation."""
        portfolio_data = self.service._get_client_portfolio("John Smith")
        insights = self.service._generate_portfolio_insights(portfolio_data, 12.0)
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        # Check that insights are strings
        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight), 0)
    
    def test_risk_level_assessment(self):
        """Test portfolio risk level assessment."""
        # Test high risk portfolio
        high_risk_portfolio = {"portfolio_beta": 1.5}
        risk_level = self.service._assess_portfolio_risk_level(high_risk_portfolio)
        self.assertEqual(risk_level, "High Risk")
        
        # Test moderate risk portfolio
        moderate_risk_portfolio = {"portfolio_beta": 1.2}
        risk_level = self.service._assess_portfolio_risk_level(moderate_risk_portfolio)
        self.assertEqual(risk_level, "Moderate Risk")
        
        # Test conservative portfolio
        conservative_portfolio = {"portfolio_beta": 0.8}
        risk_level = self.service._assess_portfolio_risk_level(conservative_portfolio)
        self.assertEqual(risk_level, "Conservative")
    
    def test_risk_alerts_identification(self):
        """Test risk alerts identification."""
        # Test portfolio with high drawdown
        high_drawdown_portfolio = {"max_drawdown": -0.20}
        alerts = self.service._identify_risk_alerts(high_drawdown_portfolio)
        self.assertIn("High maximum drawdown detected", alerts)
        
        # Test portfolio with high volatility
        high_volatility_portfolio = {"volatility": 0.30}
        alerts = self.service._identify_risk_alerts(high_volatility_portfolio)
        self.assertIn("High volatility levels", alerts)
        
        # Test normal portfolio
        normal_portfolio = {"max_drawdown": -0.05, "volatility": 0.15}
        alerts = self.service._identify_risk_alerts(normal_portfolio)
        self.assertEqual(len(alerts), 0)


class TestLambdaHandler(unittest.TestCase):
    """Test cases for the Lambda handler function."""
    
    def test_extract_param_function(self):
        """Test parameter extraction function."""
        # Test direct value
        self.assertEqual(extract_param("test_value"), "test_value")
        
        # Test dict with value
        self.assertEqual(extract_param({"value": "test_value"}), "test_value")
        
        # Test None
        self.assertIsNone(extract_param(None))
    
    def test_lambda_handler_portfolio_overview(self):
        """Test Lambda handler with portfolio overview request."""
        event = {
            "analysis_type": "overview",
            "client_name": "John Smith"
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check response structure
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("headers", result)
        self.assertIn("body", result)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertTrue(body["success"])
        self.assertEqual(body["analysis_type"], "portfolio_overview")
        self.assertEqual(body["client_name"], "John Smith")
    
    def test_lambda_handler_performance_report(self):
        """Test Lambda handler with performance report request."""
        event = {
            "analysis_type": "performance",
            "client_name": "John Smith",
            "additional_params": {
                "period": "monthly"
            }
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check response structure
        self.assertEqual(result["statusCode"], 200)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertTrue(body["success"])
        self.assertEqual(body["analysis_type"], "performance_report")
        self.assertEqual(body["report_period"], "monthly")
    
    def test_lambda_handler_missing_client_name(self):
        """Test Lambda handler with missing client name for client-specific analysis."""
        event = {
            "analysis_type": "overview"
            # Missing client_name
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check error response
        self.assertEqual(result["statusCode"], 400)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertFalse(body["success"])
        self.assertIn("error", body)
        self.assertIn("Missing required parameter", body["error"])
    
    def test_lambda_handler_unsupported_analysis_type(self):
        """Test Lambda handler with unsupported analysis type."""
        event = {
            "analysis_type": "unsupported_type",
            "client_name": "John Smith"
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check error response
        self.assertEqual(result["statusCode"], 500)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertFalse(body["success"])
        self.assertIn("error", body)
        self.assertIn("Unsupported analysis type", body["error"])
    
    def test_lambda_handler_comparative_analysis(self):
        """Test Lambda handler with comparative analysis request."""
        event = {
            "analysis_type": "comparison",
            "additional_params": {
                "client1": "John Smith",
                "client2": "Sarah Johnson"
            }
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check response structure
        self.assertEqual(result["statusCode"], 200)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertTrue(body["success"])
        self.assertEqual(body["analysis_type"], "comparative_analysis")
    
    def test_lambda_handler_alerts_analysis(self):
        """Test Lambda handler with alerts analysis request."""
        event = {
            "analysis_type": "alerts"
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check response structure
        self.assertEqual(result["statusCode"], 200)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertTrue(body["success"])
        self.assertEqual(body["analysis_type"], "alerts_notifications")
    
    def test_lambda_handler_personal_portfolio(self):
        """Test Lambda handler with personal portfolio analysis request."""
        event = {
            "analysis_type": "personal_portfolio",
            "employee_name": "Jane Doe"
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check response structure
        self.assertEqual(result["statusCode"], 200)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertTrue(body["success"])
        self.assertEqual(body["analysis_type"], "personal_portfolio")
        self.assertEqual(body["employee_name"], "Jane Doe")
    
    def test_lambda_handler_compliance_analysis(self):
        """Test Lambda handler with compliance analysis request."""
        event = {
            "analysis_type": "compliance"
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check response structure
        self.assertEqual(result["statusCode"], 200)
        
        # Parse response body
        body = json.loads(result["body"])
        self.assertTrue(body["success"])
        self.assertEqual(body["analysis_type"], "compliance_audit")
    
    def test_lambda_handler_cors_headers(self):
        """Test Lambda handler CORS headers."""
        event = {
            "analysis_type": "overview",
            "client_name": "John Smith"
        }
        context = None
        
        result = lambda_handler(event, context)
        
        # Check CORS headers
        headers = result["headers"]
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertIn("Access-Control-Allow-Origin", headers)
        self.assertEqual(headers["Access-Control-Allow-Origin"], "*")
    
    def test_lambda_handler_exception_handling(self):
        """Test Lambda handler exception handling."""
        # Create an event that will cause an exception
        event = {
            "analysis_type": "overview",
            "client_name": "John Smith",
            "additional_params": None  # This might cause issues in some cases
        }
        context = None
        
        # This should not raise an exception
        result = lambda_handler(event, context)
        
        # Should return a valid response
        self.assertIn("statusCode", result)
        self.assertIn("body", result)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for portfolio analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = PortfolioAnalysisService()
    
    def test_full_portfolio_analysis_workflow(self):
        """Test complete portfolio analysis workflow for a client."""
        client_name = "John Smith"
        
        # 1. Portfolio Overview
        overview = self.service.analyze_portfolio("overview", client_name)
        self.assertTrue(overview["success"])
        
        # 2. Performance Report
        performance = self.service.analyze_portfolio("performance", client_name, 
                                                   additional_params={"period": "monthly"})
        self.assertTrue(performance["success"])
        
        # 3. Risk Analysis
        risk = self.service.analyze_portfolio("risk", client_name)
        self.assertTrue(risk["success"])
        
        # 4. Sector Breakdown
        sector = self.service.analyze_portfolio("sector_breakdown", client_name)
        self.assertTrue(sector["success"])
        
        # Verify consistency across analyses
        self.assertEqual(overview["client_name"], performance["client_name"])
        self.assertEqual(overview["client_name"], risk["client_name"])
        self.assertEqual(overview["client_name"], sector["client_name"])
    
    def test_multiple_clients_comparison_workflow(self):
        """Test workflow for comparing multiple clients."""
        # 1. Individual client analyses
        john_overview = self.service.analyze_portfolio("overview", "John Smith")
        sarah_overview = self.service.analyze_portfolio("overview", "Sarah Johnson")
        
        self.assertTrue(john_overview["success"])
        self.assertTrue(sarah_overview["success"])
        
        # 2. Comparative analysis
        comparison = self.service.analyze_portfolio("comparison", 
                                                  additional_params={
                                                      "client1": "John Smith",
                                                      "client2": "Sarah Johnson"
                                                  })
        self.assertTrue(comparison["success"])
        
        # Verify comparison includes both clients
        self.assertIn("clients_compared", comparison)
        self.assertIn("performance_comparison", comparison)
    
    def test_error_recovery_scenarios(self):
        """Test error recovery and fallback scenarios."""
        # Test with invalid client
        invalid_result = self.service.analyze_portfolio("overview", "Invalid Client")
        self.assertFalse(invalid_result["success"])
        
        # Test with valid client after invalid
        valid_result = self.service.analyze_portfolio("overview", "John Smith")
        self.assertTrue(valid_result["success"])
        
        # Test with unsupported analysis type
        unsupported_result = self.service.analyze_portfolio("unsupported", "John Smith")
        self.assertFalse(unsupported_result["success"])
        
        # Test with valid analysis type after unsupported
        valid_result2 = self.service.analyze_portfolio("risk", "John Smith")
        self.assertTrue(valid_result2["success"])


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
