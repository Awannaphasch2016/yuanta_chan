import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct

class PortfolioAnalysisStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Lambda execution role
        lambda_execution_role = iam.Role(
            self, "PortfolioAnalysisLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ]
        )

        # Portfolio Analysis Lambda
        portfolio_analysis_lambda = _lambda.Function(
            self, "PortfolioAnalysisFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                "../src/lambda_functions/portfolio_analysis",
                bundling=cdk.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                    ]
                )
            ),
            role=lambda_execution_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO"
            },
            function_name="PortfolioAnalysisFunction",
            description="Portfolio analysis Lambda for AI chatbot"
        ) 