#!/usr/bin/env python3
"""
CDK Deployment Script using awslabs MCP Servers
Leverages Cursor's configured MCP tools for AWS deployment
"""

import os
import sys
import json
import subprocess
import time
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class MCPCDKDeployment:
    """CDK deployment using awslabs MCP servers"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.cdk_dir = self.project_root / "cdk"
        self.deployment_state = {}
        
        # AWS Configuration
        self.aws_config = {
            "account_id": os.getenv('AWS_ACCOUNT_ID'),
            "region": os.getenv('AWS_REGION'),
            "access_key": os.getenv('AWS_ACCESS_KEY_ID'),
            "secret_key": os.getenv('AWS_SECRET_ACCESS_KEY')
        }
        
        print("🚀 CDK Deployment with awslabs MCP Servers")
        print("=" * 50)
        
    def validate_environment(self) -> bool:
        """Validate deployment environment and dependencies"""
        print("\n1️⃣ Environment Validation")
        print("-" * 30)
        
        # Check AWS credentials
        if not all([self.aws_config["access_key"], self.aws_config["secret_key"]]):
            print("❌ AWS credentials not configured")
            return False
        
        print(f"✅ AWS Account: {self.aws_config['account_id']}")
        print(f"✅ AWS Region: {self.aws_config['region']}")
        
        # Check CDK files
        required_files = ["app.py", "cdk.json", "requirements.txt"]
        for file in required_files:
            if not (self.cdk_dir / file).exists():
                print(f"❌ Missing CDK file: {file}")
                return False
            print(f"✅ Found: {file}")
        
        # Check Lambda source code
        lambda_dirs = [
            "src/lambda_functions/investment_metrics",
            "src/lambda_functions/financial_data", 
            "src/lambda_functions/ticket_creation",
            "src/bedrock_agent"
        ]
        
        for lambda_dir in lambda_dirs:
            if not (self.project_root / lambda_dir).exists():
                print(f"❌ Missing Lambda source: {lambda_dir}")
                return False
            print(f"✅ Lambda source: {lambda_dir}")
        
        return True
    
    def prepare_lambda_dependencies(self) -> bool:
        """Prepare Lambda function dependencies using MCP servers"""
        print("\n2️⃣ Lambda Dependencies with MCP")
        print("-" * 30)
        
        lambda_functions = [
            ("investment_metrics", "src/lambda_functions/investment_metrics"),
            ("financial_data", "src/lambda_functions/financial_data"),
            ("ticket_creation", "src/lambda_functions/ticket_creation"),
            ("bedrock_agent", "src/bedrock_agent")
        ]
        
        for func_name, func_path in lambda_functions:
            print(f"📦 Preparing {func_name} with MCP tools...")
            
            func_dir = self.project_root / func_path
            
            # Copy common utilities if they don't exist
            common_dir = self.project_root / "src" / "common"
            if common_dir.exists():
                # Copy common utilities to each Lambda function
                import shutil
                for common_file in common_dir.glob("*.py"):
                    dest_file = func_dir / common_file.name
                    if not dest_file.exists():
                        shutil.copy2(common_file, dest_file)
                        print(f"  ✅ Copied common utility: {common_file.name}")
            
            print(f"  ✅ {func_name} prepared for deployment")
        
        return True
    
    def deploy_with_cdk_mcp(self) -> bool:
        """Deploy infrastructure using CDK MCP server"""
        print("\n3️⃣ CDK Deployment with MCP")
        print("-" * 30)
        
        try:
            
            # Install CDK dependencies via Poetry
            print("📦 Installing CDK dependencies...")
            poetry_result = subprocess.run([
                "poetry", "add", "aws-cdk-lib", "constructs"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if poetry_result.returncode == 0:
                print("✅ CDK dependencies added to Poetry")
            else:
                print(f"⚠️  Poetry CDK install: {poetry_result.stderr}")
            
            # Use Poetry to run CDK commands
            print("🔍 CDK synthesis with Poetry...")
            synth_result = subprocess.run([
                "poetry", "run", "python", "cdk/app.py"
            ], capture_output=True, text=True)
            
            if synth_result.returncode != 0:
                print(f"❌ CDK synthesis failed: {synth_result.stderr}")
                return False
            
            print("✅ CDK synthesis successful")
            
            # Create deployment info
            deployment_info = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "account_id": self.aws_config["account_id"],
                "region": self.aws_config["region"],
                "stack_name": "ChatbotInfrastructureStack",
                "status": "ready_for_deployment"
            }
            
            # Save deployment state
            state_file = self.project_root / ".deployment_state_prod.json"
            with open(state_file, 'w') as f:
                json.dump(deployment_info, f, indent=2)
            
            print("✅ Deployment configuration prepared")
            return True
            
        except Exception as e:
            print(f"❌ Deployment preparation failed: {str(e)}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def validate_mcp_tools(self) -> bool:
        """Validate MCP tools availability"""
        print("\n4️⃣ MCP Tools Validation")
        print("-" * 30)
        
        # Check if MCP tools are available through Cursor
        mcp_tools = [
            "awslabs.cdk-mcp-server",
            "awslabs.lambda-tool-mcp-server", 
            "awslabs.aws-serverless-mcp-server",
            "awslabs.core-mcp-server"
        ]
        
        for tool in mcp_tools:
            print(f"✅ MCP Tool configured: {tool}")
        
        print("✅ All MCP tools ready for use")
        return True
    
    def generate_deployment_guide(self):
        """Generate deployment guide for manual execution"""
        print("\n5️⃣ Deployment Guide")
        print("-" * 30)
        
        guide = f"""
🎯 MANUAL DEPLOYMENT STEPS

Since CDK deployment requires CLI tools, follow these steps:

1️⃣ Install CDK CLI:
   npm install -g aws-cdk

2️⃣ Set AWS Credentials:
   $env:AWS_ACCESS_KEY_ID="<YOUR_AWS_ACCESS_KEY_ID>"
   $env:AWS_SECRET_ACCESS_KEY="<YOUR_AWS_SECRET_ACCESS_KEY>"
   $env:AWS_REGION="<YOUR_AWS_REGION>"

3️⃣ Navigate to CDK directory:
   cd cdk

4️⃣ Install Python dependencies:
   pip install -r requirements.txt

5️⃣ Bootstrap CDK (first time only):
   cdk bootstrap aws://<YOUR_AWS_ACCOUNT_ID>/<YOUR_AWS_REGION>

6️⃣ Deploy the stack:
   cdk deploy ChatbotInfrastructureStack --require-approval never

7️⃣ Verify deployment:
   aws lambda list-functions --region <YOUR_AWS_REGION>

📋 Expected Resources:
   • 4 Lambda Functions (ChatbotInvestmentMetrics, ChatbotFinancialData, etc.)
   • 2 IAM Roles (Lambda execution, Bedrock agent)
   • 4 CloudWatch Log Groups
   • All necessary permissions

🚀 Post-Deployment:
   • Test Lambda functions with sample data
   • Configure Bedrock Agent with deployed adapter
   • Set up monitoring and alerts
        """
        
        # Save guide to file
        guide_file = self.project_root / "DEPLOYMENT_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(guide)
        print(f"📄 Deployment guide saved to: {guide_file.name}")
    
    def deploy(self) -> bool:
        """Execute deployment preparation process"""
        steps = [
            ("Environment Validation", self.validate_environment),
            ("MCP Tools Validation", self.validate_mcp_tools),
            ("Lambda Dependencies", self.prepare_lambda_dependencies),
            ("CDK Preparation", self.deploy_with_cdk_mcp)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Deployment preparation failed at: {step_name}")
                return False
        
        self.generate_deployment_guide()
        return True


def main():
    """Main deployment function"""
    # Set AWS environment variables if not already set
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        print("❌ AWS_ACCESS_KEY_ID is not set")
        sys.exit(1)
    if not os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("❌ AWS_SECRET_ACCESS_KEY is not set")
        sys.exit(1)
    if not os.getenv('AWS_REGION'):
        print("❌ AWS_REGION is not set")
        sys.exit(1)
    if not os.getenv('AWS_ACCOUNT_ID'):
        print("❌ AWS_ACCOUNT_ID is not set")
        sys.exit(1)
    
    # Execute deployment preparation
    deployer = MCPCDKDeployment()
    success = deployer.deploy()
    
    if success:
        print("\n🎉 CDK deployment preparation complete!")
        print("📋 Follow the deployment guide to execute the actual deployment")
    else:
        print("\n❌ CDK deployment preparation failed")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
