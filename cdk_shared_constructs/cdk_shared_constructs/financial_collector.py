"""
Financial Collector CDK Construct

Reusable construct for creating Lambda functions that collect financial data.
Encapsulates Lambda function, IAM roles, CloudWatch logs, and related infrastructure.
"""

import os
from pathlib import Path
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Duration,
    CfnOutput,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs,
)


class FinancialCollector(Construct):
    """
    Reusable construct for financial data collection Lambda functions.
    
    Creates:
    - Lambda function with Python 3.12 runtime
    - IAM execution role with appropriate permissions
    - CloudWatch log group with configurable retention
    - Proper asset bundling for dependencies
    
    Usage:
        collector = FinancialCollector(
            self, "FinancialCollector",
            lambda_code_path="../../src/lambda_functions/financial_data",
            environment="prod",
            timeout=Duration.seconds(60),
            memory_size=1024
        )
    """
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str,
        lambda_code_path: str = None,
        environment: str = "dev",
        timeout: Duration = Duration.seconds(30),
        memory_size: int = 512,
        log_retention: logs.RetentionDays = logs.RetentionDays.ONE_WEEK,
        description: str = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id)
        
        # Store configuration
        self.lambda_code_path = lambda_code_path
        self.environment = environment
        self.timeout = timeout
        self.memory_size = memory_size
        self.log_retention = log_retention
        self.description = description or f"Financial data collection Lambda function - {self.environment} environment"
        
        # Get invariant paths (works from any execution context)
        self._setup_paths()
        
        # Create infrastructure components
        self.execution_role = self._create_execution_role()
        self.function = self._create_lambda_function()
        self.log_group = self._create_log_group()
        
    def _setup_paths(self) -> None:
        """Setup invariant paths that work regardless of execution context"""
        if self.lambda_code_path:
            # Use provided relative path, resolved from construct's location
            construct_dir = Path(__file__).parent.absolute()
            self.asset_path = (construct_dir / self.lambda_code_path).resolve()
        else:
            # Default behavior: find project root and use standard path
            current_path = Path(__file__).parent.absolute()
            project_root = current_path
            
            # Walk up until we find pyproject.toml
            while project_root.parent != project_root:
                if (project_root / "pyproject.toml").exists():
                    break
                project_root = project_root.parent
            
            self.project_root = project_root
            self.asset_path = project_root / "src/lambda_functions/financial_data"
        
        # Validate asset path exists
        if not self.asset_path.exists():
            raise ValueError(f"Lambda asset path not found: {self.asset_path}")
    
    def _create_execution_role(self) -> iam.Role:
        """Create IAM role for Lambda execution with comprehensive permissions"""
        return iam.Role(
            self, "ExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
            inline_policies={
                "FinancialCollectorPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream", 
                                "logs:PutLogEvents",
                            ],
                            resources=["*"]
                        ),
                        # Add permissions for external financial data APIs if needed
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "secretsmanager:GetSecretValue"
                            ],
                            resources=["*"],
                            conditions={
                                "StringEquals": {
                                    "secretsmanager:ResourceTag/Purpose": "FinancialData"
                                }
                            }
                        )
                    ]
                )
            }
        )
    
    def _create_lambda_function(self) -> _lambda.Function:
        """Create Lambda function with proper configuration and asset bundling"""
        return _lambda.Function(
            self, "Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                str(self.asset_path),
                bundling=cdk.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                    ]
                )
            ),
            role=self.execution_role,
            timeout=self.timeout,
            memory_size=self.memory_size,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": self.environment,
                "DATA_SOURCE": "yahoo_finance"
            },
            # No function_name - let CDK auto-generate for uniqueness
            description=self.description
        )
    
    def _create_log_group(self) -> logs.LogGroup:
        """Create CloudWatch Log Group for the Lambda function"""
        return logs.LogGroup(
            self, "LogGroup",
            log_group_name=f"/aws/lambda/{self.function.function_name}",
            retention=self.log_retention,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
    
    @property
    def function_arn(self) -> str:
        """Get the Lambda function ARN"""
        return self.function.function_arn
    
    @property 
    def function_name(self) -> str:
        """Get the Lambda function name"""
        return self.function.function_name
    
    def grant_invoke(self, grantee: iam.IGrantable) -> iam.Grant:
        """Grant invoke permissions to another AWS service or role"""
        return self.function.grant_invoke(grantee)
    
    def add_environment_variable(self, key: str, value: str) -> None:
        """Add environment variable to the Lambda function"""
        self.function.add_environment(key, value)
    
    def grant_secrets_access(self, secret_arn: str) -> iam.Grant:
        """Grant access to specific AWS Secrets Manager secret"""
        return iam.Grant.add_to_principal(
            scope=self,
            grantee=self.execution_role,
            actions=["secretsmanager:GetSecretValue"],
            resource_arns=[secret_arn]
        ) 