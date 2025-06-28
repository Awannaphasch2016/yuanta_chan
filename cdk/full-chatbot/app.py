#!/usr/bin/env python3
"""
CDK Application for InHouse AI Chatbot Infrastructure - Full Stack
Complete chatbot infrastructure with all Lambda functions and Bedrock integration
"""

import os
import sys
import logging
from pathlib import Path
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
        logging.FileHandler('cdk_full_chatbot_synthesis.log', mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Get the directory where this script is located (invariant behavior)
SCRIPT_DIR = Path(__file__).parent.absolute()
CDK_OUT_DIR = SCRIPT_DIR / "cdk.out"

class ChatbotInfrastructureStack(Stack):
    """Main stack for AI Chatbot infrastructure"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        logger.info("Starting ChatbotInfrastructureStack initialization...")
        logger.info(f"   Construct ID: {construct_id}")
        logger.info(f"   Current working directory: {os.getcwd()}")
        logger.info(f"   Script directory: {SCRIPT_DIR}")
        
        super().__init__(scope, construct_id, **kwargs)

        # PATH VALIDATION GUARDRAIL - Terminate if any asset path is incorrect
        logger.info("Starting path validation...")
        required_paths = [
            "src/lambda_functions/investment_metrics",
            "src/lambda_functions/financial_data", 
            "src/lambda_functions/ticket_creation",
            "src/bedrock_agent"
        ]
        
        for asset_path in required_paths:
            # Use invariant path resolution relative to project root
            project_root = SCRIPT_DIR.parent.parent
            resolved_path = project_root / asset_path
            
            logger.info(f"   Checking path: {asset_path}")
            logger.info(f"   Resolved to: {resolved_path}")
            logger.info(f"   Path exists: {resolved_path.exists()}")
            
            if not resolved_path.exists():
                logger.error("CRITICAL ERROR: Asset path validation FAILED")
                logger.error(f"   Missing path: {resolved_path}")
                logger.error(f"   Expected structure:")
                logger.error(f"     Project root: {project_root}")
                logger.error(f"     Required path: {asset_path}")
                logger.error("   Terminating deployment to prevent CDK errors.")
                sys.exit(1)

        logger.info("Path validation completed successfully!")

        # Configuration from environment
        logger.info("Loading environment configuration...")
        self.account_id = os.getenv('AWS_ACCOUNT_ID')
        self.region = self.region
        
        logger.info(f"   AWS Account ID: {self.account_id}")
        logger.info(f"   AWS Region: {self.region}")
        
        # Create IAM roles first
        logger.info("Creating IAM roles...")
        self.lambda_execution_role = self._create_lambda_execution_role()
        self.bedrock_agent_role = self._create_bedrock_agent_role()
        logger.info("IAM roles created successfully!")
        
        # Create Lambda functions
        logger.info("Creating Lambda functions...")
        self.investment_metrics_lambda = self._create_investment_metrics_lambda()
        self.financial_data_lambda = self._create_financial_data_lambda()
        self.ticket_creation_lambda = self._create_ticket_creation_lambda()
        self.bedrock_adapter_lambda = self._create_bedrock_adapter_lambda()
        logger.info("Lambda functions created successfully!")
        
        # Create CloudWatch Log Groups
        logger.info("Creating CloudWatch Log Groups...")
        self._create_log_groups()
        logger.info("CloudWatch Log Groups created successfully!")
        
        # Create outputs
        logger.info("Creating CloudFormation outputs...")
        self._create_outputs()
        logger.info("CloudFormation outputs created successfully!")
        
        logger.info("ChatbotInfrastructureStack initialization completed!")

    def _create_lambda_execution_role(self) -> iam.Role:
        """Create IAM role for Lambda execution with comprehensive permissions"""
        logger.info("   Creating Lambda execution role...")
        role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess"),
            ],
            inline_policies={
                "ChatbotLambdaPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream", 
                                "logs:PutLogEvents",
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream",
                                "bedrock:ListFoundationModels",
                                "sts:GetCallerIdentity",
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )
        logger.info(f"   Lambda execution role created: {role.role_name}")
        return role

    def _create_bedrock_agent_role(self) -> iam.Role:
        """Create IAM role for Bedrock Agent"""
        logger.info("   Creating Bedrock agent role...")
        role = iam.Role(
            self, "BedrockAgentRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "BedrockAgentPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "lambda:InvokeFunction"
                            ],
                            resources=[
                                f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                                f"arn:aws:lambda:{self.region}:{self.account_id}:function:*"
                            ]
                        )
                    ]
                )
            }
        )
        logger.info(f"   Bedrock agent role created: {role.role_name}")
        return role

    def _create_investment_metrics_lambda(self) -> _lambda.Function:
        """Create Investment Metrics Lambda function"""
        logger.info("   Creating Investment Metrics Lambda...")
        # Use invariant path resolution
        project_root = SCRIPT_DIR.parent.parent
        asset_path = str(project_root / "src/lambda_functions/investment_metrics")
        
        function = _lambda.Function(
            self, "InvestmentMetricsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                asset_path,
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
            function_name="ChatbotInvestmentMetrics",
            description="Investment analysis and metrics for AI chatbot"
        )
        logger.info(f"   Investment Metrics Lambda created: {function.function_name}")
        return function

    def _create_financial_data_lambda(self) -> _lambda.Function:
        """Create Financial Data Lambda function"""
        logger.info("   Creating Financial Data Lambda...")
        # Use invariant path resolution
        project_root = SCRIPT_DIR.parent.parent
        asset_path = str(project_root / "src/lambda_functions/financial_data")
        
        function = _lambda.Function(
            self, "FinancialDataFunction", 
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                asset_path,
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
            function_name="ChatbotFinancialData",
            description="Financial data retrieval service for AI chatbot"
        )
        logger.info(f"   Financial Data Lambda created: {function.function_name}")
        return function

    def _create_ticket_creation_lambda(self) -> _lambda.Function:
        """Create Ticket Creation Lambda function"""
        logger.info("   Creating Ticket Creation Lambda...")
        # Use invariant path resolution
        project_root = SCRIPT_DIR.parent.parent
        asset_path = str(project_root / "src/lambda_functions/ticket_creation")
        
        function = _lambda.Function(
            self, "TicketCreationFunction",
            runtime=_lambda.Runtime.PYTHON_3_12, 
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                asset_path,
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
            function_name="ChatbotTicketCreation",
            description="Internal ticketing system integration for AI chatbot"
        )
        logger.info(f"   Ticket Creation Lambda created: {function.function_name}")
        return function

    def _create_bedrock_adapter_lambda(self) -> _lambda.Function:
        """Create Bedrock Agent Adapter Lambda function"""
        logger.info("   Creating Bedrock Adapter Lambda...")
        # Use invariant path resolution
        project_root = SCRIPT_DIR.parent.parent
        asset_path = str(project_root / "src/bedrock_agent")
        
        function = _lambda.Function(
            self, "BedrockAdapterFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="bedrock_adapter.lambda_handler", 
            code=_lambda.Code.from_asset(
                asset_path,
                bundling=cdk.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                    ]
                )
            ),
            role=self.lambda_execution_role,
            timeout=Duration.seconds(60),
            memory_size=1024,
            environment={
                "LOG_LEVEL": "INFO",
                "INVESTMENT_METRICS_FUNCTION": self.investment_metrics_lambda.function_name,
                "FINANCIAL_DATA_FUNCTION": self.financial_data_lambda.function_name,
                "TICKET_CREATION_FUNCTION": self.ticket_creation_lambda.function_name
            },
            function_name="ChatbotBedrockAdapter",
            description="Bedrock Agent adapter with real LLM integration"
        )
        logger.info(f"   Bedrock Adapter Lambda created: {function.function_name}")
        return function

    def _create_log_groups(self):
        """Create CloudWatch Log Groups for all Lambda functions"""
        logger.info("   Creating CloudWatch Log Groups...")
        functions = [
            ("InvestmentMetricsLogGroup", self.investment_metrics_lambda),
            ("FinancialDataLogGroup", self.financial_data_lambda), 
            ("TicketCreationLogGroup", self.ticket_creation_lambda),
            ("BedrockAdapterLogGroup", self.bedrock_adapter_lambda)
        ]
        
        for log_group_id, lambda_function in functions:
            log_group = logs.LogGroup(
                self, log_group_id,
                log_group_name=f"/aws/lambda/{lambda_function.function_name}",
                retention=logs.RetentionDays.ONE_WEEK,
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            logger.info(f"     Log group created: {log_group.log_group_name}")

    def _create_outputs(self):
        """Create CloudFormation outputs for key resources"""
        logger.info("   Creating CloudFormation outputs...")
        
        outputs = [
            ("InvestmentMetricsLambdaArn", self.investment_metrics_lambda.function_arn, "Investment Metrics Lambda Function ARN"),
            ("FinancialDataLambdaArn", self.financial_data_lambda.function_arn, "Financial Data Lambda Function ARN"),
            ("TicketCreationLambdaArn", self.ticket_creation_lambda.function_arn, "Ticket Creation Lambda Function ARN"),
            ("BedrockAdapterLambdaArn", self.bedrock_adapter_lambda.function_arn, "Bedrock Adapter Lambda Function ARN"),
            ("BedrockAgentRoleArn", self.bedrock_agent_role.role_arn, "Bedrock Agent IAM Role ARN")
        ]
        
        for output_id, value, description in outputs:
            CfnOutput(self, output_id, value=value, description=description)
            logger.info(f"     Output created: {output_id}")


class FullChatbotApp(cdk.App):
    """CDK Application for Full AI Chatbot Infrastructure"""
    
    def __init__(self):
        logger.info("Initializing FullChatbotApp...")
        logger.info(f"Script directory: {SCRIPT_DIR}")
        logger.info(f"CDK output directory: {CDK_OUT_DIR}")
        super().__init__(outdir=str(CDK_OUT_DIR))
        
        logger.info("Creating ChatbotInfrastructureStack...")
        # Create the main infrastructure stack
        ChatbotInfrastructureStack(
            self, "ChatbotInfrastructureStack",
            env=cdk.Environment(
                account=os.getenv('AWS_ACCOUNT_ID'),
                region=os.getenv('AWS_REGION')
            ),
            description="InHouse AI Chatbot Infrastructure - Full Stack with Bedrock Agent and Lambda Tools"
        )
        logger.info("FullChatbotApp initialization completed!")


def main():
    """Main function to create and synthesize the CDK app"""
    logger.info("=" * 60)
    logger.info("STARTING FULL CHATBOT CDK SYNTHESIS PROCESS")
    logger.info("=" * 60)
    
    try:
        logger.info("Creating CDK Application instance...")
        app = FullChatbotApp()
        
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
        logger.info("FULL CHATBOT CDK SYNTHESIS PROCESS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("CDK SYNTHESIS FAILED!")
        logger.error("=" * 60)
        logger.error(f"Error: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 