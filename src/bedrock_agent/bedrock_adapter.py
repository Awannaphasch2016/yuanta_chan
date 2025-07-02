"""
Bedrock Agent Adapter for Investment Analysis
Converts Bedrock Agent requests to Lambda function calls and provides real LLM integration
"""

import json
import sys
import os
import re
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from investment_analyzer import SequentialInvestmentAnalyzer
from logger import get_logger

class BedrockAgentAdapter:
    """Hybrid adapter integrating Lambda functions with real Bedrock LLM"""
    
    def __init__(self, region: Optional[str] = None):
        self.logger = get_logger("BedrockAgentAdapter")
        self.analyzer = SequentialInvestmentAnalyzer()
        
        # Set region from parameter, environment variable, or default
        self.region = region or os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
        
        # Initialize AWS credentials and clients
        self.bedrock_runtime = None
        # Try multiple Claude Sonnet models in order of preference
        self.model_options = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Latest Claude 3.5 Sonnet v2
            "anthropic.claude-3-5-sonnet-20240620-v1:0",  # Claude 3.5 Sonnet
            "anthropic.claude-3-sonnet-20240229-v1:0",    # Standard Claude 3 Sonnet
            "anthropic.claude-v2:0",                      # Fallback to Claude v2
        ]
        self.model_id = self.model_options[0]  # Start with the best model
        self.credentials_configured = False
        
        # Initialize AWS clients with credential handling
        self._init_aws_credentials()
        self._init_bedrock_client()
    
    def _init_aws_credentials(self):
        """Initialize and validate AWS credentials"""
        try:
            # Check for explicit credentials in environment
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            session_token = os.getenv('AWS_SESSION_TOKEN')
            profile = os.getenv('AWS_PROFILE') or os.getenv('AWS_DEFAULT_PROFILE')
            
            if access_key and secret_key:
                self.logger.info("Using AWS credentials from environment variables")
                self.credentials_configured = True
            elif profile:
                self.logger.info(f"Using AWS profile: {profile}")
                self.credentials_configured = True
            else:
                self.logger.warning("No explicit AWS credentials found in environment")
                # boto3 will try default credential chain (IAM roles, etc.)
                
        except Exception as e:
            self.logger.error(f"Error checking AWS credentials: {str(e)}")
            self.credentials_configured = False
    
    def _init_bedrock_client(self):
        """Initialize Bedrock Runtime client with comprehensive error handling"""
        try:
            # Create session with explicit credentials if available
            session_kwargs = {}
            
            # Add explicit credentials if available
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            session_token = os.getenv('AWS_SESSION_TOKEN')
            profile = os.getenv('AWS_PROFILE') or os.getenv('AWS_DEFAULT_PROFILE')
            
            if access_key and secret_key:
                session_kwargs.update({
                    'aws_access_key_id': access_key,
                    'aws_secret_access_key': secret_key
                })
                if session_token:
                    session_kwargs['aws_session_token'] = session_token
            elif profile:
                session_kwargs['profile_name'] = profile
            
            # Create boto3 session
            session = boto3.Session(**session_kwargs)
            
            # Create Bedrock Runtime client
            self.bedrock_runtime = session.client('bedrock-runtime', region_name=self.region)
            
            # Test credentials by listing models (optional validation)
            self._validate_bedrock_access()
            
            self.logger.info(f"Bedrock Runtime client initialized successfully in region: {self.region}")
            
        except NoCredentialsError:
            self.logger.error("AWS credentials not found. Please configure AWS credentials.")
            self.bedrock_runtime = None
            self.credentials_configured = False
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UnauthorizedOperation':
                self.logger.error("AWS credentials are invalid or insufficient permissions")
            else:
                self.logger.error(f"AWS ClientError: {str(e)}")
            self.bedrock_runtime = None
            self.credentials_configured = False
        except Exception as e:
            self.logger.warning(f"Failed to initialize Bedrock Runtime client: {str(e)}")
            self.bedrock_runtime = None
            self.credentials_configured = False
    
    def _validate_bedrock_access(self):
        """Validate Bedrock access by testing a simple API call"""
        try:
            # Try to list foundation models to validate access
            response = self.bedrock_runtime.list_foundation_models()
            self.logger.info("Bedrock access validated successfully")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'AccessDeniedException':
                self.logger.warning("Bedrock access denied - check IAM permissions")
            elif error_code == 'UnauthorizedOperation':
                self.logger.warning("Unauthorized to access Bedrock - check credentials")
            else:
                self.logger.warning(f"Bedrock validation failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.warning(f"Bedrock validation error: {str(e)}")
            return False
    
    def get_aws_status(self) -> Dict[str, Any]:
        """Get detailed AWS configuration status for debugging"""
        status = {
            "credentials_configured": self.credentials_configured,
            "bedrock_client_available": self.bedrock_runtime is not None,
            "region": self.region,
            "model_id": self.model_id,
            "environment_variables": {
                "AWS_PROFILE": os.getenv('AWS_PROFILE'),
                "AWS_DEFAULT_PROFILE": os.getenv('AWS_DEFAULT_PROFILE'),
                "AWS_REGION": os.getenv('AWS_REGION'),
                "AWS_ACCESS_KEY_ID": "***" if os.getenv('AWS_ACCESS_KEY_ID') else None,
                "AWS_SECRET_ACCESS_KEY": "***" if os.getenv('AWS_SECRET_ACCESS_KEY') else None,
                "AWS_SESSION_TOKEN": "***" if os.getenv('AWS_SESSION_TOKEN') else None,
            }
        }
        return status
    
    def handle_agent_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Bedrock Agent tool request (existing functionality preserved)"""
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
    
    def handle_user_query(self, query: str) -> str:
        """Handle user query with hybrid routing (NEW: Real LLM Integration)"""
        try:
            self.logger.info(f"Processing user query: {query[:50]}...")
            
            # Route query to appropriate handler
            query_type = self._route_query(query)
            
            if query_type == "tool":
                # Use existing tool functionality for investment analysis
                return self._handle_tool_query(query)
            else:
                # Use real LLM for conversational responses
                return self._handle_conversation_query(query)
                
        except Exception as e:
            self.logger.error(f"User query processing failed: {str(e)}")
            return self._handle_api_error(e)
    
    def _route_query(self, query: str) -> str:
        """Route query to appropriate handler based on content"""
        query_lower = query.lower()
        
        # Investment analysis patterns
        investment_patterns = [
            r"analyze .+ stock",
            r"investment analysis",
            r"stock price",
            r"financial data",
            r"company metrics",
            r"P/E ratio",
            r"market cap",
            r"revenue",
            r"earnings"
        ]
        
        # Check for investment-related queries
        for pattern in investment_patterns:
            if re.search(pattern, query_lower):
                return "tool"
        
        # Default to conversation for general queries
        return "conversation"
    
    def _handle_tool_query(self, query: str) -> str:
        """Handle tool queries using existing investment analysis"""
        try:
            # Extract ticker from query
            ticker = self._extract_ticker_from_query(query)
            
            if not ticker:
                return "I couldn't identify a stock ticker in your query. Please specify a company ticker (e.g., AAPL, MSFT, GOOGL)."
            
            # Use existing analyzer
            result = self.analyzer.analyze(ticker, "detailed")
            
            if result.get("success"):
                analysis = result["analysis"]
                return self._format_investment_response(ticker, analysis)
            else:
                return f"❌ Analysis failed for {ticker}: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error(f"Tool query handling failed: {str(e)}")
            return f"I encountered an error analyzing your request. Let me use my local analysis capabilities: {str(e)}"
    
    def _handle_conversation_query(self, query: str) -> str:
        """Handle conversational queries using real Bedrock LLM"""
        if not self.bedrock_runtime:
            return "I'm currently in local mode. For investment analysis, please ask about specific companies (e.g., 'How does Apple make money?')."
        
        try:
            return self._get_llm_response(query)
        except Exception as e:
            self.logger.error(f"LLM conversation failed: {str(e)}")
            return self._handle_api_error(e)
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get real response from Bedrock LLM with model fallback"""
        # Enhance prompt with professional context
        enhanced_prompt = self._add_professional_context(prompt)
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "temperature": 0.7
        })
        
        # Try each model in order of preference
        for i, model_id in enumerate(self.model_options):
            try:
                self.logger.info(f"Attempting LLM call with model: {model_id}")
                
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=body,
                    contentType="application/json"
                )
                
                # If successful, update the current model and return response
                if self.model_id != model_id:
                    self.logger.info(f"Successfully switched to model: {model_id}")
                    self.model_id = model_id
                
                return self._parse_llm_response(response)
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                self.logger.warning(f"Model {model_id} failed with error {error_code}: {str(e)}")
                
                # If this is the last model, raise the exception
                if i == len(self.model_options) - 1:
                    self.logger.error(f"All models failed. Last error: {str(e)}")
                    raise e
                
                # Otherwise, try the next model
                continue
            except Exception as e:
                self.logger.warning(f"Model {model_id} failed with unexpected error: {str(e)}")
                
                # If this is the last model, raise the exception
                if i == len(self.model_options) - 1:
                    self.logger.error(f"All models failed. Last error: {str(e)}")
                    raise e
                
                # Otherwise, try the next model
                continue
        
        # This should never be reached, but just in case
        raise Exception("All available models failed")
    
    def _parse_llm_response(self, response) -> str:
        """Parse Bedrock LLM response"""
        try:
            response_body = json.loads(response.get('body').read())
            content = response_body.get('content', [])
            
            if content and len(content) > 0:
                return content[0].get('text', 'No response generated')
            else:
                return 'No response generated'
                
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {str(e)}")
            return f"I received a response but couldn't parse it properly: {str(e)}"
    
    def _add_professional_context(self, prompt: str) -> str:
        """Add professional context to LLM prompts"""
        context = """You are a professional investment analysis assistant for a brokerage company. 
You help investment consultants and clients with financial questions and analysis. 
Provide accurate, well-structured responses with appropriate financial disclaimers when relevant.
Be conversational but maintain professional standards.

User question: """
        
        return context + prompt
    
    def _extract_ticker_from_query(self, query: str) -> str:
        """Extract stock ticker from user query"""
        # Common ticker patterns
        ticker_patterns = [
            r'\b([A-Z]{1,5})\b',  # 1-5 uppercase letters
            r'ticker\s+([A-Z]{1,5})',  # "ticker AAPL"
            r'stock\s+([A-Z]{1,5})',   # "stock AAPL"
        ]
        
        # Company name to ticker mapping (common ones)
        company_mapping = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'netflix': 'NFLX',
            'nvidia': 'NVDA'
        }
        
        query_lower = query.lower()
        
        # Check company names first
        for company, ticker in company_mapping.items():
            if company in query_lower:
                return ticker
        
        # Check ticker patterns
        for pattern in ticker_patterns:
            match = re.search(pattern, query.upper())
            if match:
                return match.group(1)
        
        return None
    
    def _handle_api_error(self, error: Exception) -> str:
        """Handle Bedrock API errors gracefully"""
        if isinstance(error, ClientError):
            error_code = error.response.get('Error', {}).get('Code', '')
            
            if error_code == 'ThrottlingException':
                return "I'm experiencing high demand right now. Please try again in a moment."
            elif error_code == 'AccessDeniedException':
                return "I don't have access to the AI service right now. For investment analysis, please ask about specific companies."
            elif error_code == 'ValidationException':
                return "There was an issue with your request format. Please try rephrasing your question."
            else:
                return f"I encountered a service issue. For investment analysis, I can still help with specific company questions."
        
        # Fallback message for any other errors
        return "I'm currently in local mode. For investment analysis, please ask about specific companies (e.g., 'How does Apple make money?')."
    
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
