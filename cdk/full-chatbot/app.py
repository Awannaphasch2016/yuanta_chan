#!/usr/bin/env python3
"""
Full Chatbot Infrastructure Stack
Comprehensive CDK application using shared constructs for complete chatbot system
"""

import os
import sys
from pathlib import Path
import logging
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnOutput,
    Tags
)
from constructs import Construct

# Add the shared constructs to the path
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
shared_constructs_path = project_root / "cdk_shared_constructs"
sys.path.insert(0, str(shared_constructs_path))

from cdk_shared_constructs import (
    InvestmentProcessor,
    FinancialCollector,
    BedrockAdapter
)

# Configure logging for CDK operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cdk_synthesis.log')
    ]
)
logger = logging.getLogger(__name__)

class ChatbotInfrastructureStack(Stack):
    """Complete chatbot infrastructure with all required Lambda functions"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        logger.info("Starting ChatbotInfrastructureStack initialization with shared constructs...")
        logger.info(f"   Construct ID: {construct_id}")
        logger.info(f"   Script directory: {script_dir}")
        
        # Calculate project root path
        project_root = script_dir.parent.parent
        logger.info(f"   Project root: {project_root}")
        
        logger.info("Creating Lambda functions using shared constructs...")
        
        # Investment Analysis Lambda using InvestmentProcessor
        self.investment_processor = InvestmentProcessor(
            self, "InvestmentProcessor",
            lambda_code_path=str(project_root / "src/lambda_functions/investment_metrics"),
            memory_size=1024,
            timeout_seconds=60,
            environment_variables={
                "FUNCTION_PURPOSE": "chatbot_investment_analysis",
                "DATA_SOURCE": "yahoo_finance"
            }
        )
        logger.info(f"   ✅ Investment Processor created: {self.investment_processor.function_name}")
        
        # Financial Data Collection Lambda using FinancialCollector  
        self.financial_collector = FinancialCollector(
            self, "FinancialCollector",
            lambda_code_path=str(project_root / "src/lambda_functions/financial_data"),
            memory_size=1024,
            timeout_seconds=60,
            environment_variables={
                "FUNCTION_PURPOSE": "chatbot_data_collection",
                "DATA_SOURCE_VERSION": "v2"
            }
        )
        logger.info(f"   ✅ Financial Collector created: {self.financial_collector.function_name}")
        
        # Bedrock Agent Integration Lambda using BedrockAdapter
        lambda_function_names = [
            self.investment_processor.function_name,
            self.financial_collector.function_name
        ]
        
        self.bedrock_adapter = BedrockAdapter(
            self, "BedrockAdapter", 
            lambda_code_path=str(project_root / "src/bedrock_agent"),
            lambda_function_names=lambda_function_names,
            memory_size=1024,
            timeout_seconds=60,
            environment_variables={
                "INVESTMENT_FUNCTION": self.investment_processor.function_name,
                "FINANCIAL_DATA_FUNCTION": self.financial_collector.function_name,
                "FUNCTION_PURPOSE": "chatbot_orchestration"
            }
        )
        logger.info(f"   ✅ Bedrock Adapter created: {self.bedrock_adapter.function_name}")
        
        # Grant Bedrock Adapter permission to invoke other Lambda functions
        self.bedrock_adapter.grant_lambda_invoke(self.investment_processor.function_arn)
        self.bedrock_adapter.grant_lambda_invoke(self.financial_collector.function_arn)

        # Add tags to all resources
        Tags.of(self).add("Project", "YuantaChan-InvestmentChatbot")
        Tags.of(self).add("Environment", "Development") 
        Tags.of(self).add("CostCenter", "AI-Development")
        Tags.of(self).add("Owner", "Engineering-Team")

        # Stack Outputs for easy reference
        CfnOutput(self, "InvestmentProcessorArn", 
                 value=self.investment_processor.function_arn,
                 description="Investment Processor Lambda Function ARN")
        
        CfnOutput(self, "FinancialCollectorArn",
                 value=self.financial_collector.function_arn, 
                 description="Financial Collector Lambda Function ARN")
        
        CfnOutput(self, "BedrockAdapterArn",
                 value=self.bedrock_adapter.function_arn,
                 description="Bedrock Adapter Lambda Function ARN")
        
        CfnOutput(self, "InvestmentProcessorName",
                 value=self.investment_processor.function_name,
                 description="Investment Processor Lambda Function Name")
        
        CfnOutput(self, "FinancialCollectorName", 
                 value=self.financial_collector.function_name,
                 description="Financial Collector Lambda Function Name")
        
        CfnOutput(self, "BedrockAdapterName",
                 value=self.bedrock_adapter.function_name,
                 description="Bedrock Adapter Lambda Function Name")
        
        CfnOutput(self, "InvestmentProcessorRoleArn",
                 value=self.investment_processor.role_arn,
                 description="Investment Processor IAM Role ARN")
        
        CfnOutput(self, "FinancialCollectorRoleArn",
                 value=self.financial_collector.role_arn,
                 description="Financial Collector IAM Role ARN")
        
        CfnOutput(self, "BedrockAdapterRoleArn",
                 value=self.bedrock_adapter.role_arn,
                 description="Bedrock Adapter IAM Role ARN")

class FullChatbotApp(cdk.App):
    """CDK Application for Full Chatbot Infrastructure"""
    
    def __init__(self):
        super().__init__()
        
        logger.info("Creating CDK Application instance...")
        logger.info("Initializing FullChatbotApp with shared constructs...")
        
        # Log the directories being used
        script_dir = Path(__file__).parent.absolute()
        logger.info(f"Script directory: {script_dir}")
        logger.info(f"CDK output directory: {script_dir}/")
        logger.info(f"CDK output directory: {script_dir}/cdk.out")
        
        # Create the main chatbot infrastructure stack
        ChatbotInfrastructureStack(
            self, "ChatbotInfrastructureStack",
            description="Complete chatbot infrastructure with investment analysis, financial data, and Bedrock integration"
        )

def main():
    """Main entry point for CDK synthesis"""
    try:
        logger.info("=" * 79)
        logger.info("=" * 80)
        logger.info("STARTING FULL CHATBOT CDK SYNTHESIS WITH SHARED CONSTRUCTS")
        logger.info("=" * 79)
        logger.info("=" * 80)
        
        app = FullChatbotApp()
        app.synth()
        
        logger.info("=" * 79)
        logger.info("CDK SYNTHESIS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 79)
        
    except Exception as e:
        logger.error("=" * 78)
        logger.error("=" * 80)
        logger.error("CDK SYNTHESIS FAILED!")
        logger.error("=" * 78)
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}")
        logger.error("Stack trace:")
        raise

if __name__ == "__main__":
    main() 