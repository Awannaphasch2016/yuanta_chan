"""
CDK Construct for Bedrock Agent Adapter Lambda Function
Provides reusable infrastructure for Bedrock Agent integration with real LLM capabilities
"""

from typing import Optional, Dict, Any, List
from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs,
    RemovalPolicy,
    BundlingOptions
)
from constructs import Construct


class BedrockAdapter(Construct):
    """
    CDK Construct for deploying Bedrock Agent adapter Lambda functions with proper IAM roles,
    CloudWatch logging, Bedrock permissions, and Lambda invocation capabilities.
    
    This construct encapsulates all the infrastructure needed for Bedrock Agent integration
    with other Lambda functions and real LLM capabilities.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_code_path: str,
        lambda_function_names: Optional[List[str]] = None,
        memory_size: int = 1024,
        timeout_seconds: int = 60,
        log_retention_days: int = 7,
        environment_variables: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize the BedrockAdapter construct.

        Args:
            scope: The scope in which to define this construct
            construct_id: The scoped construct ID
            lambda_code_path: Path to the Lambda function source code
            lambda_function_names: List of Lambda function names this adapter can invoke
            memory_size: Memory allocation for the Lambda function (default: 1024 MB)
            timeout_seconds: Timeout for the Lambda function (default: 60 seconds)
            log_retention_days: CloudWatch log retention period (default: 7 days)
            environment_variables: Additional environment variables for the Lambda
            **kwargs: Additional keyword arguments
        """
        super().__init__(scope, construct_id, **kwargs)

        # Set default environment variables
        default_env_vars = {
            "LOG_LEVEL": "INFO",
            "ENVIRONMENT": "prod",
            "AWS_REGION": "us-east-1",
            "BEDROCK_MODEL": "anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
        
        # Add Lambda function names to environment if provided
        if lambda_function_names:
            for i, function_name in enumerate(lambda_function_names):
                default_env_vars[f"LAMBDA_FUNCTION_{i+1}"] = function_name
        
        # Merge with provided environment variables
        if environment_variables:
            default_env_vars.update(environment_variables)

        # Create IAM execution role with Bedrock and Lambda permissions
        self.execution_role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonBedrockFullAccess"
                )
            ],
            inline_policies={
                "BedrockAdapterPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=["*"]
                        ),
                        # Bedrock permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream",
                                "bedrock:ListFoundationModels",
                                "bedrock:GetFoundationModel"
                            ],
                            resources=["*"]
                        ),
                        # Lambda invocation permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "lambda:InvokeFunction"
                            ],
                            resources=["*"],
                            conditions={
                                "StringLike": {
                                    "lambda:FunctionName": [
                                        "*InvestmentMetrics*",
                                        "*FinancialData*"
                                    ]
                                }
                            }
                        ),
                        # Additional permissions for agent operations
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sts:GetCallerIdentity"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

        # Create Lambda function
        self.lambda_function = _lambda.Function(
            self,
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="bedrock_adapter.lambda_handler",
            code=_lambda.Code.from_asset(
                lambda_code_path,
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                    ]
                )
            ),
            role=self.execution_role,
            timeout=Duration.seconds(timeout_seconds),
            memory_size=memory_size,
            environment=default_env_vars,
            description="Bedrock Agent adapter with real LLM integration for investment analysis platform"
        )

        # Create CloudWatch Log Group
        retention_mapping = {
            1: logs.RetentionDays.ONE_DAY,
            3: logs.RetentionDays.THREE_DAYS,
            5: logs.RetentionDays.FIVE_DAYS,
            7: logs.RetentionDays.ONE_WEEK,
            14: logs.RetentionDays.TWO_WEEKS,
            30: logs.RetentionDays.ONE_MONTH
        }
        
        retention = retention_mapping.get(log_retention_days, logs.RetentionDays.ONE_WEEK)
        
        self.log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/{self.lambda_function.function_name}",
            retention=retention,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Bedrock Agent execution role for agent operations
        self.bedrock_agent_role = iam.Role(
            self,
            "BedrockAgentRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "BedrockAgentExecutionPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel"
                            ],
                            resources=[
                                f"arn:aws:bedrock:*::foundation-model/anthropic.*"
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "lambda:InvokeFunction"
                            ],
                            resources=[
                                self.lambda_function.function_arn
                            ]
                        )
                    ]
                )
            }
        )

    @property
    def function_arn(self) -> str:
        """Return the ARN of the Lambda function."""
        return self.lambda_function.function_arn

    @property 
    def function_name(self) -> str:
        """Return the name of the Lambda function."""
        return self.lambda_function.function_name

    @property
    def role_arn(self) -> str:
        """Return the ARN of the execution role."""
        return self.execution_role.role_arn

    @property
    def bedrock_agent_role_arn(self) -> str:
        """Return the ARN of the Bedrock Agent role."""
        return self.bedrock_agent_role.role_arn

    def grant_invoke(self, grantee: iam.IGrantable) -> iam.Grant:
        """
        Grant the given identity permissions to invoke this Lambda function.
        
        Args:
            grantee: The principal to grant invoke permissions to
            
        Returns:
            Grant object representing the permission
        """
        return self.lambda_function.grant_invoke(grantee)

    def grant_lambda_invoke(self, target_function_arn: str) -> None:
        """
        Grant this Lambda function permissions to invoke another Lambda function.
        
        Args:
            target_function_arn: ARN of the target Lambda function to grant invoke access to
        """
        self.execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["lambda:InvokeFunction"],
                resources=[target_function_arn]
            )
        )

    def add_bedrock_model_access(self, model_arn_pattern: str) -> None:
        """
        Grant this Lambda function permissions to access specific Bedrock models.
        
        Args:
            model_arn_pattern: ARN pattern for Bedrock models (e.g., "arn:aws:bedrock:*::foundation-model/anthropic.*")
        """
        self.execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=[model_arn_pattern]
            )
        )

    def add_environment_variable(self, key: str, value: str) -> None:
        """
        Add an environment variable to the Lambda function.
        
        Args:
            key: Environment variable key
            value: Environment variable value
        """
        current_env = self.lambda_function.environment or {}
        current_env[key] = value
        # Note: This requires CDK to update the function configuration 