"""
Bedrock Agent Adapter for Investment Analysis
Converts Bedrock Agent requests to Lambda function calls
"""

import json
import sys
import os
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from lambda_functions.investment_metrics.lambda_function import SequentialInvestmentAnalyzer
from common.logger import get_logger

class BedrockAgentAdapter:
    """Adapter to integrate Lambda functions with Bedrock Agent"""
    
    def __init__(self):
        self.logger = get_logger("BedrockAgentAdapter")
        self.analyzer = SequentialInvestmentAnalyzer()
    
    def handle_agent_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Bedrock Agent tool request"""
        try:
            # Extract parameters from Bedrock Agent format
            action_group = event.get("actionGroup", "")
            function_name = event.get("function", "")
            parameters = event.get("parameters", {})
            
            self.logger.info(f"Processing Bedrock Agent request: {function_name}")
            
            if function_name == "analyze_investment":
                return self._analyze_investment(parameters)
            elif function_name == "get_financial_data":
                return self._get_financial_data(parameters)
            else:
                return self._error_response(f"Unknown function: {function_name}")
                
        except Exception as e:
            self.logger.error(f"Bedrock Agent request failed: {str(e)}")
            return self._error_response(str(e))
    
    def _analyze_investment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze investment using existing Lambda function"""
        ticker = parameters.get("ticker", "").upper()
        depth = parameters.get("depth", "standard")
        
        if not ticker:
            return self._error_response("Missing required parameter: ticker")
        
        # Call existing analyzer
        result = self.analyzer.analyze(ticker, depth)
        
        if result.get("success"):
            # Format for Bedrock Agent consumption
            analysis = result["analysis"]
            recommendation = analysis["recommendation"]
            
            response_text = self._format_investment_response(ticker, analysis)
            
            return {
                "response": {
                    "actionGroup": "InvestmentTools",
                    "function": "analyze_investment",
                    "functionResponse": {
                        "responseBody": {
                            "TEXT": {
                                "body": response_text
                            }
                        }
                    }
                }
            }
        else:
            return self._error_response(result.get("error", "Analysis failed"))
    
    def _format_investment_response(self, ticker: str, analysis: Dict[str, Any]) -> str:
        """Format investment analysis for natural language response"""
        essential = analysis["essential_metrics"]
        recommendation = analysis["recommendation"]
        
        company_name = essential.get("company_name", ticker)
        current_price = essential.get("current_price")
        
        response = f"📊 Investment Analysis: {company_name} ({ticker})\n\n"
        
        if current_price:
            response += f"💰 Current Price: ${current_price:.2f}\n"
        
        response += f"🎯 Recommendation: {recommendation['recommendation']}\n"
        response += f"📈 Investment Score: {recommendation['score']}/100\n"
        response += f"🔍 Confidence: {recommendation['confidence']}\n\n"
        
        response += "📋 Key Insights:\n"
        for rationale in recommendation.get("detailed_rationale", [])[:3]:
            response += f"• {rationale}\n"
        
        if recommendation.get("opportunities"):
            response += "\n🚀 Growth Opportunities:\n"
            for opportunity in recommendation["opportunities"][:2]:
                response += f"• {opportunity}\n"
        
        response += "\n⚠️ Disclaimer: This analysis is for informational purposes only and should not be considered as financial advice."
        
        return response
    
    def _get_financial_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial data (placeholder for future implementation)"""
        ticker = parameters.get("ticker", "").upper()
        
        return {
            "response": {
                "actionGroup": "InvestmentTools", 
                "function": "get_financial_data",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": f"Financial data retrieval for {ticker} - Feature coming soon!"
                        }
                    }
                }
            }
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Format error response for Bedrock Agent"""
        return {
            "response": {
                "actionGroup": "InvestmentTools",
                "function": "error",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": f"❌ Error: {error_message}"
                        }
                    }
                }
            }
        }

def lambda_handler(event, context):
    """Lambda handler for Bedrock Agent integration"""
    adapter = BedrockAgentAdapter()
    return adapter.handle_agent_request(event)
