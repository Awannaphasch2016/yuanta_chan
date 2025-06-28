#!/usr/bin/env python3
"""
Deployment script for Investment Metrics Lambda function
Updated for new CDK structure: cdk/investment-metrics/
"""

import os
import subprocess
import sys
from pathlib import Path

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, check=True)
        print("✅ AWS credentials are configured")
        return True
    except subprocess.CalledProcessError:
        print("❌ AWS credentials not configured. Please run 'aws configure'")
        return False
    except FileNotFoundError:
        print("❌ AWS CLI not found. Please install AWS CLI")
        return False

def check_cdk_installed():
    """Check if CDK is installed"""
    try:
        subprocess.run(['cdk', '--version'], capture_output=True, check=True)
        print("✅ AWS CDK is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            result = subprocess.run(['powershell', '-Command', 'cdk --version'], 
                                  capture_output=True, check=True, text=True)
            print("✅ AWS CDK is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ AWS CDK not found. Please install with 'npm install -g aws-cdk'")
            return False

def check_dependencies():
    """Check if all required dependencies exist"""
    # Path relative to project root (../../src from cdk/investment-metrics/)
    investment_metrics_dir = Path("../../src/lambda_functions/investment_metrics")
    
    if not investment_metrics_dir.exists():
        print(f"❌ Lambda function directory not found: {investment_metrics_dir}")
        return False
    
    required_files = [
        "lambda_function.py",
        "requirements.txt",
        "logger.py",
        "yahoo_finance_client.py"
    ]
    
    for file in required_files:
        if not (investment_metrics_dir / file).exists():
            print(f"❌ Required file not found: {investment_metrics_dir / file}")
            return False
    
    print("✅ All Lambda function files exist")
    return True

def run_validation():
    """Run AWS CDK readiness validation"""
    validation_script = Path("../shared/validate_deployment.py")
    
    if validation_script.exists():
        print("🔍 Running AWS CDK readiness validation...")
        try:
            result = subprocess.run(['python', str(validation_script)], 
                                  capture_output=True, text=True, check=True)
            print("✅ AWS environment validation passed")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Validation warnings detected, but proceeding...")
            return True
    else:
        print("⚠️  Validation script not found, skipping validation")
        return True

def deploy_lambda():
    """Deploy the Investment Metrics Lambda function"""
    print("🚀 Starting deployment of Investment Metrics Lambda...")
    
    try:
        # Bootstrap CDK (if needed)
        print("📦 Bootstrapping CDK...")
        subprocess.run(['powershell', '-Command', 'poetry run cdk bootstrap'], check=True, cwd='../..')
        
        # Deploy the stack
        print("🔄 Deploying Investment Metrics Stack...")
        subprocess.run(['powershell', '-Command', 'poetry run cdk deploy InvestmentMetricsStack --app "python cdk/investment-metrics/app.py" --require-approval never'], 
                      check=True, cwd='../..')
        
        print("✅ Investment Metrics Lambda deployed successfully!")
        
        # Get deployment outputs
        print("📋 Getting deployment outputs...")
        result = subprocess.run(['powershell', '-Command', 'poetry run cdk ls --app "python cdk/investment-metrics/app.py"'], 
                              capture_output=True, text=True, check=True, cwd='../..')
        print(f"Deployed stacks: {result.stdout.strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False

def test_lambda():
    """Test the deployed Lambda function"""
    print("🧪 Testing the deployed Lambda function...")
    
    test_event = {
        "ticker": "AAPL",
        "depth": "standard"
    }
    
    try:
        import json
        
        # Create test event file
        with open("test_event.json", "w") as f:
            json.dump(test_event, f)
        
        # Invoke the Lambda function
        result = subprocess.run([
            'aws', 'lambda', 'invoke',
            '--function-name', 'ChatbotInvestmentMetrics',
            '--payload', json.dumps(test_event),
            'test_response.json'
        ], capture_output=True, text=True, check=True)
        
        # Read the response
        with open("test_response.json", "r") as f:
            response = json.load(f)
        
        print("✅ Lambda function test successful!")
        print(f"Response preview: {json.dumps(response, indent=2)[:200]}...")
        
        # Clean up test files
        os.remove("test_event.json")
        os.remove("test_response.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🎯 Investment Metrics Lambda Deployment")
    print("📁 New CDK Structure: cdk/investment-metrics/")
    print("=" * 60)
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📍 Working directory: {os.getcwd()}")
    
    # Pre-deployment checks
    if not check_aws_credentials():
        sys.exit(1)
    
    if not check_cdk_installed():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not run_validation():
        sys.exit(1)
    
    # Set environment variables if needed
    if not os.getenv('AWS_ACCOUNT_ID'):
        try:
            result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
                                  capture_output=True, text=True, check=True)
            os.environ['AWS_ACCOUNT_ID'] = result.stdout.strip()
        except subprocess.CalledProcessError:
            print("❌ Could not determine AWS Account ID")
            sys.exit(1)
    
    if not os.getenv('AWS_REGION'):
        os.environ['AWS_REGION'] = 'ap-southeast-1'  # Use your configured region
    
    print(f"📍 Deploying to Account: {os.environ['AWS_ACCOUNT_ID']}")
    print(f"📍 Region: {os.environ['AWS_REGION']}")
    
    # Deploy the Lambda function
    if deploy_lambda():
        print("\n🎉 Deployment completed successfully!")
        
        # Optional: Test the function
        user_input = input("\n🤔 Would you like to test the Lambda function? (y/N): ")
        if user_input.lower() in ['y', 'yes']:
            test_lambda()
        
        print("\n✨ Investment Metrics Lambda is ready to use!")
        print(f"Function Name: ChatbotInvestmentMetrics")
        print(f"Stack Name: InvestmentMetricsStack")
        print(f"You can test it via AWS Console or AWS CLI")
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 