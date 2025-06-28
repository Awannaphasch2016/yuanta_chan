#!/usr/bin/env python3
"""
Single Lambda CDK Application - Investment Metrics Function Only
Focused infrastructure for testing and development of investment analysis capabilities
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct

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
    """Stack for deploying only the Investment Metrics Lambda function"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        logger.info("STARTING InvestmentMetricsStack initialization...")
        logger.info(f"   Construct ID: {construct_id}")
        logger.info(f"   Current working directory: {os.getcwd()}")
        
        super().__init__(scope, construct_id, **kwargs)

        # PATH VALIDATION GUARDRAIL - Terminate if path is incorrect
        logger.info("Starting path validation...")
        # Use invariant path resolution - works from any directory
        project_root = SCRIPT_DIR.parent.parent  # Go up from cdk/investment-metrics to project root
        asset_path = project_root / "src/lambda_functions/investment_metrics"
        resolved_path = str(asset_path.resolve())
        
        logger.info(f"   Asset path: {asset_path}")
        logger.info(f"   Resolved path: {resolved_path}")
        logger.info(f"   Path exists: {asset_path.exists()}")
        
        if not asset_path.exists():
            logger.error(f"CRITICAL ERROR: Asset path validation FAILED")
            logger.error(f"   Expected path: {resolved_path}")
            logger.error(f"   Current working directory: {os.getcwd()}")
            logger.error(f"   Terminating deployment to prevent CDK errors.")
            exit(1)
        
        logger.info("Path validation successful!")

        # Configuration from environment
        logger.info("Reading environment configuration...")
        self.account_id = os.getenv('AWS_ACCOUNT_ID')
        aws_region = os.getenv('AWS_REGION')
        logger.info(f"   AWS Account ID: {self.account_id}")
        logger.info(f"   AWS Region: {aws_region}")
        
        # Create IAM role for Lambda execution
        logger.info("Creating Lambda execution role...")
        self.lambda_execution_role = self._create_lambda_execution_role()
        logger.info("Lambda execution role created successfully!")
        
        # Create the Investment Metrics Lambda function
        logger.info("Creating Investment Metrics Lambda function...")
        self.investment_metrics_lambda = self._create_investment_metrics_lambda()
        logger.info("Investment Metrics Lambda function created successfully!")
        
        # Create CloudWatch Log Group
        logger.info("Creating CloudWatch Log Groups...")
        self._create_log_groups()
        logger.info("CloudWatch Log Groups created successfully!")
        
        # Create outputs
        logger.info("Creating CloudFormation outputs...")
        self._create_outputs()
        logger.info("CloudFormation outputs created successfully!")
        
        logger.info("InvestmentMetricsStack initialization completed successfully!")

    def _create_lambda_execution_role(self) -> iam.Role:
        """Create IAM role for Lambda execution with comprehensive permissions"""
        logger.info("   Creating IAM role with basic execution permissions...")
        return iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
            inline_policies={
                "InvestmentMetricsLambdaPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream", 
                                "logs:PutLogEvents",
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

    def _create_investment_metrics_lambda(self) -> _lambda.Function:
        """Create Investment Metrics Lambda function"""
        # Use the validated path - invariant resolution
        project_root = SCRIPT_DIR.parent.parent  # Go up from cdk/investment-metrics to project root
        asset_path = project_root / "src/lambda_functions/investment_metrics"
        logger.info(f"   Using asset path: {asset_path}")
        logger.info("   Configuring Lambda function with Python 3.12 runtime...")
        
        return _lambda.Function(
            self, "InvestmentMetricsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                str(asset_path),
                bundling=cdk.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                    ]
                )
            ),
            role=self.lambda_execution_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO"
            },
            # Removed function_name - let CDK auto-generate unique name
            description="Investment analysis and metrics for AI chatbot - Testing deployment"
        )

    def _create_log_groups(self):
        """Create CloudWatch Log Groups for the Lambda function"""
        logger.info(f"   Creating log group: /aws/lambda/{self.investment_metrics_lambda.function_name}")
        logs.LogGroup(
            self, "InvestmentMetricsLogGroup",
            log_group_name=f"/aws/lambda/{self.investment_metrics_lambda.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

    def _create_outputs(self):
        """Create CloudFormation outputs for key resources"""
        logger.info("   Creating CloudFormation outputs for Lambda ARN and name...")
        CfnOutput(
            self, "InvestmentMetricsLambdaArn",
            value=self.investment_metrics_lambda.function_arn,
            description="Investment Metrics Lambda Function ARN"
        )
        
        CfnOutput(
            self, "InvestmentMetricsLambdaName", 
            value=self.investment_metrics_lambda.function_name,
            description="Investment Metrics Lambda Function Name"
        )


class InvestmentMetricsApp(cdk.App):
    """CDK Application for Investment Metrics single Lambda deployment"""
    
    def __init__(self):
        logger.info("Initializing CDK Application...")
        logger.info(f"Script directory: {SCRIPT_DIR}")
        logger.info(f"CDK output directory: {CDK_OUT_DIR}")
        super().__init__(outdir=str(CDK_OUT_DIR))
        
        logger.info("Creating InvestmentMetricsStack...")
        # Create the single Lambda stack
        InvestmentMetricsStack(
            self, "InvestmentMetricsStack",
            env=cdk.Environment(
                account=os.getenv('AWS_ACCOUNT_ID'),
                region=os.getenv('AWS_REGION')
            ),
            description="Investment Metrics Lambda Function - Testing and Development"
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