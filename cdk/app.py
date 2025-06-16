#!/usr/bin/env python3
"""
CDK Application for InHouse AI Chatbot Infrastructure
Leverages awslabs MCP servers for deployment
"""

import os
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

class ChatbotInfrastructureStack(Stack):
    """Main stack for AI Chatbot infrastructure"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Configuration from environment
        self.account_id = os.getenv('AWS_ACCOUNT_ID', '864130225056')
        
        # Create IAM roles first
        self.lambda_execution_role = self._create_lambda_execution_role()
        self.bedrock_agent_role = self._create_bedrock_agent_role()
        
        # Create Lambda functions
        self.investment_metrics_lambda = self._create_investment_metrics_lambda()
        self.financial_data_lambda = self._create_financial_data_lambda()
        self.ticket_creation_lambda = self._create_ticket_creation_lambda()
        self.bedrock_adapter_lambda = self._create_bedrock_adapter_lambda()
        
        # Create CloudWatch Log Groups
        self._create_log_groups()
        
        # Create outputs
        self._create_outputs()

    def _create_lambda_execution_role(self) -> iam.Role:
        """Create IAM role for Lambda execution with comprehensive permissions"""
        return iam.Role(
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

    def _create_bedrock_agent_role(self) -> iam.Role:
        """Create IAM role for Bedrock Agent"""
        return iam.Role(
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

    def _create_investment_metrics_lambda(self) -> _lambda.Function:
        """Create Investment Metrics Lambda function"""
        return _lambda.Function(
            self, "InvestmentMetricsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("src/lambda_functions/investment_metrics"),
            role=self.lambda_execution_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO"
            },
            function_name="ChatbotInvestmentMetrics",
            description="Investment analysis and metrics for AI chatbot"
        )

    def _create_financial_data_lambda(self) -> _lambda.Function:
        """Create Financial Data Lambda function"""
        return _lambda.Function(
            self, "FinancialDataFunction", 
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("src/lambda_functions/financial_data"),
            role=self.lambda_execution_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO"
            },
            function_name="ChatbotFinancialData",
            description="Financial data retrieval service for AI chatbot"
        )

    def _create_ticket_creation_lambda(self) -> _lambda.Function:
        """Create Ticket Creation Lambda function"""
        return _lambda.Function(
            self, "TicketCreationFunction",
            runtime=_lambda.Runtime.PYTHON_3_12, 
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("src/lambda_functions/ticket_creation"),
            role=self.lambda_execution_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO"
            },
            function_name="ChatbotTicketCreation",
            description="Internal ticketing system integration for AI chatbot"
        )

    def _create_bedrock_adapter_lambda(self) -> _lambda.Function:
        """Create Bedrock Agent Adapter Lambda function"""
        return _lambda.Function(
            self, "BedrockAdapterFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="bedrock_adapter.lambda_handler", 
            code=_lambda.Code.from_asset("src/bedrock_agent"),
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

    def _create_log_groups(self):
        """Create CloudWatch Log Groups for all Lambda functions"""
        functions = [
            ("InvestmentMetricsLogGroup", self.investment_metrics_lambda),
            ("FinancialDataLogGroup", self.financial_data_lambda), 
            ("TicketCreationLogGroup", self.ticket_creation_lambda),
            ("BedrockAdapterLogGroup", self.bedrock_adapter_lambda)
        ]
        
        for log_group_id, lambda_function in functions:
            logs.LogGroup(
                self, log_group_id,
                log_group_name=f"/aws/lambda/{lambda_function.function_name}",
                retention=logs.RetentionDays.ONE_WEEK,
                removal_policy=cdk.RemovalPolicy.DESTROY
            )

    def _create_outputs(self):
        """Create CloudFormation outputs for key resources"""
        CfnOutput(
            self, "InvestmentMetricsLambdaArn",
            value=self.investment_metrics_lambda.function_arn,
            description="Investment Metrics Lambda Function ARN"
        )
        
        CfnOutput(
            self, "FinancialDataLambdaArn", 
            value=self.financial_data_lambda.function_arn,
            description="Financial Data Lambda Function ARN"
        )
        
        CfnOutput(
            self, "TicketCreationLambdaArn",
            value=self.ticket_creation_lambda.function_arn,
            description="Ticket Creation Lambda Function ARN"
        )
        
        CfnOutput(
            self, "BedrockAdapterLambdaArn",
            value=self.bedrock_adapter_lambda.function_arn,
            description="Bedrock Adapter Lambda Function ARN"
        )
        
        CfnOutput(
            self, "BedrockAgentRoleArn",
            value=self.bedrock_agent_role.role_arn,
            description="Bedrock Agent IAM Role ARN"
        )


class ChatbotApp(cdk.App):
    """CDK Application for AI Chatbot Infrastructure"""
    
    def __init__(self):
        super().__init__()
        
        # Create the main infrastructure stack
        ChatbotInfrastructureStack(
            self, "ChatbotInfrastructureStack",
            env=cdk.Environment(
                account=os.getenv('AWS_ACCOUNT_ID', '864130225056'),
                region=os.getenv('AWS_REGION', 'ap-southeast-1')
            ),
            description="InHouse AI Chatbot Infrastructure with Bedrock Agent and Lambda Tools"
        )


# Create and synthesize the CDK app
app = ChatbotApp()
app.synth() 