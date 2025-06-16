"""
Deployment script for Bedrock Agent Integration
Creates and configures the Bedrock Agent with Lambda tools
"""

import json
import boto3
import os
from typing import Dict, Any

class BedrockAgentDeployer:
    """Deploy and configure Bedrock Agent for investment analysis"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
    
    def deploy_agent(self, account_id: str) -> Dict[str, Any]:
        """Deploy the complete Bedrock Agent setup"""
        try:
            print("🚀 Starting Bedrock Agent deployment...")
            
            # Step 1: Create IAM role for Bedrock Agent
            role_arn = self._create_bedrock_agent_role(account_id)
            print(f"✅ Created Bedrock Agent IAM role: {role_arn}")
            
            # Step 2: Deploy Lambda function for agent adapter
            lambda_arn = self._deploy_lambda_function(account_id)
            print(f"✅ Deployed Lambda function: {lambda_arn}")
            
            # Step 3: Create Bedrock Agent
            agent_id = self._create_bedrock_agent(role_arn)
            print(f"✅ Created Bedrock Agent: {agent_id}")
            
            # Step 4: Create action group with Lambda integration
            action_group_id = self._create_action_group(agent_id, lambda_arn)
            print(f"✅ Created action group: {action_group_id}")
            
            # Step 5: Prepare agent for use
            self._prepare_agent(agent_id)
            print("✅ Agent prepared and ready for use")
            
            return {
                "agent_id": agent_id,
                "agent_arn": f"arn:aws:bedrock:{self.region}:{account_id}:agent/{agent_id}",
                "lambda_arn": lambda_arn,
                "role_arn": role_arn,
                "status": "deployed"
            }
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            raise
    
    def _create_bedrock_agent_role(self, account_id: str) -> str:
        """Create IAM role for Bedrock Agent"""
        role_name = "BedrockAgentInvestmentAnalysisRole"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "lambda:InvokeFunction"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                        f"arn:aws:lambda:{self.region}:{account_id}:function:BedrockAgentAdapter"
                    ]
                }
            ]
        }
        
        try:
            # Create role
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="IAM role for Bedrock Agent Investment Analysis"
            )
            
            # Attach inline policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName="BedrockAgentInvestmentPolicy",
                PolicyDocument=json.dumps(policy_document)
            )
            
            return response['Role']['Arn']
            
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            # Role already exists, return its ARN
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
    
    def _deploy_lambda_function(self, account_id: str) -> str:
        """Deploy Lambda function for Bedrock Agent adapter"""
        function_name = "BedrockAgentAdapter"
        
        # This would typically involve packaging and uploading the Lambda code
        # For now, we'll assume the function exists or provide deployment instructions
        
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
            return response['Configuration']['FunctionArn']
        except self.lambda_client.exceptions.ResourceNotFoundException:
            print(f"⚠️ Lambda function {function_name} not found. Please deploy it manually.")
            return f"arn:aws:lambda:{self.region}:{account_id}:function:{function_name}"
    
    def _create_bedrock_agent(self, role_arn: str) -> str:
        """Create the Bedrock Agent"""
        agent_config = {
            "agentName": "InvestmentAnalysisAgent",
            "description": "Professional investment analysis assistant for financial data and insights",
            "foundationModel": "anthropic.claude-3-sonnet-20240229-v1:0",
            "instruction": """You are a professional investment analysis assistant for a brokerage company. 
            You help investment consultants and clients analyze financial data, understand company performance, 
            and make informed investment decisions. Always provide accurate, well-structured responses with 
            appropriate financial disclaimers. Use the available tools to fetch real-time financial data and 
            generate comprehensive analysis. When users ask questions like 'How does Apple make money?', 
            use the analyze_investment tool to get detailed financial analysis and present it in a clear, 
            professional manner.""",
            "idleSessionTTLInSeconds": 1800,
            "agentResourceRoleArn": role_arn
        }
        
        response = self.bedrock_agent.create_agent(**agent_config)
        return response['agent']['agentId']
    
    def _create_action_group(self, agent_id: str, lambda_arn: str) -> str:
        """Create action group with Lambda integration"""
        
        # Load the API schema
        schema_path = os.path.join(os.path.dirname(__file__), "investment_tools_schema.json")
        with open(schema_path, 'r') as f:
            api_schema = json.load(f)
        
        action_group_config = {
            "agentId": agent_id,
            "agentVersion": "DRAFT",
            "actionGroupName": "InvestmentTools",
            "description": "Tools for investment analysis and financial data retrieval",
            "actionGroupExecutor": {
                "lambda": lambda_arn
            },
            "apiSchema": {
                "payload": json.dumps(api_schema)
            }
        }
        
        response = self.bedrock_agent.create_agent_action_group(**action_group_config)
        return response['agentActionGroup']['actionGroupId']
    
    def _prepare_agent(self, agent_id: str):
        """Prepare the agent for use"""
        self.bedrock_agent.prepare_agent(agentId=agent_id)
    
    def test_agent(self, agent_id: str, test_query: str = "How does Apple make money?") -> Dict[str, Any]:
        """Test the deployed agent with a sample query"""
        try:
            bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=self.region)
            
            response = bedrock_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId="TSTALIASID",
                sessionId="test-session-001",
                inputText=test_query
            )
            
            return {
                "status": "success",
                "response": response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Bedrock Agent for Investment Analysis")
    parser.add_argument("--account-id", required=True, help="AWS Account ID")
    parser.add_argument("--region", default="us-east-1", help="AWS Region")
    parser.add_argument("--test", action="store_true", help="Test the agent after deployment")
    
    args = parser.parse_args()
    
    deployer = BedrockAgentDeployer(region=args.region)
    
    try:
        result = deployer.deploy_agent(args.account_id)
        print(f"\n🎉 Deployment completed successfully!")
        print(f"Agent ID: {result['agent_id']}")
        print(f"Agent ARN: {result['agent_arn']}")
        
        if args.test:
            print("\n🧪 Testing agent...")
            test_result = deployer.test_agent(result['agent_id'])
            if test_result['status'] == 'success':
                print("✅ Agent test successful!")
            else:
                print(f"❌ Agent test failed: {test_result['error']}")
    
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 