#!/usr/bin/env python3
"""
Investment Metrics CDK Application - Refactored with Shared Constructs
Clean, maintainable infrastructure using reusable CDK constructs
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import aws_cdk as cdk
from aws_cdk import Stack, CfnOutput
from constructs import Construct
from cdk_shared_constructs import InvestmentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cdk_synthesis.log', mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file at project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)
logger.info(f"Loading environment variables from: {ENV_FILE}")

# Get the directory where this script is located (invariant behavior)
SCRIPT_DIR = Path(__file__).parent.absolute()
CDK_OUT_DIR = SCRIPT_DIR / "cdk.out"


class InvestmentMetricsStack(Stack):
    """Stack for deploying Investment Metrics Lambda using shared constructs"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        logger.info("STARTING InvestmentMetricsStack initialization...")
        logger.info(f"   Construct ID: {construct_id}")
        logger.info(f"   Current working directory: {os.getcwd()}")
        
        super().__init__(scope, construct_id, **kwargs)

        # Configuration from environment
        logger.info("Reading environment configuration...")
        account_id = os.getenv('AWS_ACCOUNT_ID')
        aws_region = os.getenv('AWS_REGION')
        logger.info(f"   AWS Account ID: {account_id}")
        logger.info(f"   AWS Region: {aws_region}")
        
        # Create Investment Processor using shared construct
        logger.info("Creating Investment Processor using shared construct...")
        self.investment_processor = InvestmentProcessor(
            self, "InvestmentProcessor",
            lambda_code_path="../../src/lambda_functions/investment_metrics",
            description="Investment analysis and metrics for AI chatbot - Refactored with shared constructs"
        )
        logger.info("Investment Processor created successfully!")
        
        # Create outputs using the construct's Lambda function
        logger.info("Creating CloudFormation outputs...")
        CfnOutput(
            self, "InvestmentMetricsLambdaArn",
            value=self.investment_processor.function_arn,
            description="Investment Metrics Lambda Function ARN"
        )
        
        CfnOutput(
            self, "InvestmentMetricsLambdaName", 
            value=self.investment_processor.function_name,
            description="Investment Metrics Lambda Function Name"
        )
        logger.info("CloudFormation outputs created successfully!")
        
        logger.info("InvestmentMetricsStack initialization completed successfully!")


class InvestmentMetricsApp(cdk.App):
    """CDK Application for Investment Metrics using shared constructs"""
    
    def __init__(self):
        logger.info("Initializing CDK Application...")
        logger.info(f"Script directory: {SCRIPT_DIR}")
        logger.info(f"CDK output directory: {CDK_OUT_DIR}")
        super().__init__(outdir=str(CDK_OUT_DIR))
        
        logger.info("Creating InvestmentMetricsStack...")
        InvestmentMetricsStack(
            self, "InvestmentMetricsStack",
            env=cdk.Environment(
                account=os.getenv('AWS_ACCOUNT_ID'),
                region=os.getenv('AWS_REGION')
            ),
            description="Investment Metrics Lambda Function - Refactored with Shared Constructs"
        )
        logger.info("CDK Application initialization completed!")


def main():
    """Main function to create and synthesize the CDK app"""
    logger.info("=" * 60)
    logger.info("STARTING CDK SYNTHESIS PROCESS")
    logger.info("=" * 60)
    
    try:
        logger.info("Creating CDK Application instance...")
app = InvestmentMetricsApp()
        
        logger.info("Starting synthesis process...")
        result = app.synth()
        
        logger.info("CDK synthesis completed successfully!")
        logger.info(f"Output directory: {result.directory}")
        
        # List generated files
        if os.path.exists(result.directory):
            logger.info("Generated files:")
            for root, dirs, files in os.walk(result.directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    logger.info(f"   - {file_path}")
        
        logger.info("=" * 60)
        logger.info("CDK SYNTHESIS PROCESS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("CDK SYNTHESIS PROCESS FAILED!")
        logger.error("=" * 60)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main() 