#!/usr/bin/env python3
"""
AWS CDK Deployment Readiness Validation Script
Validates all requirements for CDK implementation with real AWS credentials
"""

import os
import sys
import json
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

class AWSCDKValidator:
    """Comprehensive validator for AWS CDK deployment readiness"""
    
    def __init__(self):
        self.results = {
            "credentials": {"status": "FAIL", "details": []},
            "permissions": {"status": "FAIL", "details": []},
            "services": {"status": "FAIL", "details": []},
            "dependencies": {"status": "FAIL", "details": []},
            "architecture": {"status": "FAIL", "details": []},
            "overall": {"status": "FAIL", "ready_for_cdk": False}
        }
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🔍 AWS CDK Deployment Readiness Validation")
        print("=" * 50)
        
        # Step 1: Validate AWS Credentials
        self.validate_credentials()
        
        # Step 2: Validate AWS Permissions
        self.validate_permissions()
        
        # Step 3: Validate AWS Service Access
        self.validate_services()
        
        # Step 4: Validate Dependencies
        self.validate_dependencies()
        
        # Step 5: Validate Architecture
        self.validate_architecture()
        
        # Step 6: Generate Overall Assessment
        self.generate_assessment()
        
        return self.results
    
    def validate_credentials(self):
        """Validate AWS credentials configuration"""
        print("\n1️⃣ AWS Credentials Validation")
        print("-" * 30)
        
        details = []
        status = "PASS"
        
        try:
            # Check environment variables
            env_vars = {
                "AWS_ACCESS_KEY_ID": os.getenv('AWS_ACCESS_KEY_ID'),
                "AWS_SECRET_ACCESS_KEY": os.getenv('AWS_SECRET_ACCESS_KEY'),
                "AWS_REGION": os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION'),
                "AWS_PROFILE": os.getenv('AWS_PROFILE') or os.getenv('AWS_DEFAULT_PROFILE'),
                "AWS_ACCOUNT_ID": os.getenv('AWS_ACCOUNT_ID')
            }
            
            print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if env_vars['AWS_ACCESS_KEY_ID'] else '❌ Not set'}")
            print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if env_vars['AWS_SECRET_ACCESS_KEY'] else '❌ Not set'}")
            print(f"AWS_REGION: {env_vars['AWS_REGION'] or '❌ Not set'}")
            print(f"AWS_PROFILE: {env_vars['AWS_PROFILE'] or 'Default'}")
            print(f"AWS_ACCOUNT_ID: {env_vars['AWS_ACCOUNT_ID'] or '❌ Not set'}")
            
            # Test boto3 session
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials:
                print("✅ Boto3 session created successfully")
                details.append("Boto3 credentials available")
                
                # Get region
                region = session.region_name or env_vars['AWS_REGION'] or 'us-east-1'
                print(f"✅ Region: {region}")
                details.append(f"Region configured: {region}")
                
            else:
                print("❌ No AWS credentials found")
                status = "FAIL"
                details.append("No AWS credentials configured")
                
        except Exception as e:
            print(f"❌ Credential validation error: {str(e)}")
            status = "FAIL"
            details.append(f"Error: {str(e)}")
        
        self.results["credentials"] = {"status": status, "details": details}
    
    def validate_permissions(self):
        """Validate AWS permissions for required services"""
        print("\n2️⃣ AWS Permissions Validation")
        print("-" * 30)
        
        details = []
        status = "PASS"
        
        required_permissions = [
            ("sts", "get_caller_identity", "Basic AWS access"),
            ("iam", "list_roles", "IAM role management"),
            ("lambda", "list_functions", "Lambda function management"),
            ("bedrock", "list_foundation_models", "Bedrock access"),
            ("cloudformation", "describe_stacks", "CloudFormation access")
        ]
        
        for service, action, description in required_permissions:
            try:
                client = boto3.client(service)
                
                if service == "sts":
                    response = client.get_caller_identity()
                    account_id = response.get('Account')
                    print(f"✅ {description}: Account {account_id}")
                    details.append(f"Account ID: {account_id}")
                    
                elif service == "iam":
                    client.list_roles(MaxItems=1)
                    print(f"✅ {description}")
                    details.append("IAM permissions verified")
                    
                elif service == "lambda":
                    client.list_functions(MaxItems=1)
                    print(f"✅ {description}")
                    details.append("Lambda permissions verified")
                    
                elif service == "bedrock":
                    client.list_foundation_models()
                    print(f"✅ {description}")
                    details.append("Bedrock permissions verified")
                    
                elif service == "cloudformation":
                    # CloudFormation describe_stacks doesn't accept MaxItems parameter
                    client.describe_stacks()
                    print(f"✅ {description}")
                    details.append("CloudFormation permissions verified")
                    
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                    print(f"❌ {description}: Access denied")
                    status = "FAIL"
                    details.append(f"{description}: Access denied")
                else:
                    print(f"⚠️  {description}: {error_code}")
                    details.append(f"{description}: {error_code}")
                    
            except Exception as e:
                print(f"❌ {description}: {str(e)}")
                status = "FAIL"
                details.append(f"{description}: Error - {str(e)}")
        
        self.results["permissions"] = {"status": status, "details": details}
    
    def validate_services(self):
        """Validate AWS service availability"""
        print("\n3️⃣ AWS Services Validation")
        print("-" * 30)
        
        details = []
        status = "PASS"
        
        # Test Bedrock access through foundation models list instead of direct invocation
        try:
            bedrock = boto3.client('bedrock')
            bedrock_runtime = boto3.client('bedrock-runtime')
            
            # First, get available foundation models
            models_response = bedrock.list_foundation_models()
            available_models = [model['modelId'] for model in models_response.get('modelSummaries', [])]
            
            # Check for Claude models
            claude_models = [model for model in available_models if 'claude' in model.lower()]
            
            if claude_models:
                print(f"✅ Bedrock Claude models available: {len(claude_models)} models")
                details.append(f"Claude models available: {claude_models[:3]}")  # Show first 3
                
                # Test runtime access without actual invocation (just client creation)
                print("✅ Bedrock Runtime client accessible")
                details.append("Bedrock Runtime client created successfully")
            else:
                print("⚠️  No Claude models found in available models")
                details.append("No Claude models available")
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'AccessDeniedException':
                print(f"❌ Bedrock access denied: {error_code}")
                status = "FAIL" 
                details.append("Bedrock access denied")
            else:
                print(f"⚠️  Bedrock service issue: {error_code}")
                details.append(f"Bedrock issue: {error_code}")
                
        except Exception as e:
            print(f"❌ Bedrock service error: {str(e)}")
            status = "FAIL"
            details.append(f"Bedrock error: {str(e)}")
        
        self.results["services"] = {"status": status, "details": details}
    
    def validate_dependencies(self):
        """Validate project dependencies and configuration"""
        print("\n4️⃣ Dependencies Validation")
        print("-" * 30)
        
        details = []
        status = "PASS"
        
        # Check Python packages
        required_packages = [
            ("boto3", "boto3"),
            ("python-dotenv", "dotenv"), 
            ("yfinance", "yfinance")
        ]
        
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                print(f"✅ {package_name} installed")
                details.append(f"{package_name} available")
            except ImportError:
                print(f"❌ {package_name} missing")
                status = "FAIL"
                details.append(f"{package_name} missing")
        
        # Check awslabs MCP servers (these are available according to pyproject.toml)
        mcp_packages = [
            ("awslabs-cdk-mcp-server", "awslabs_cdk_mcp_server"),
            ("awslabs-core-mcp-server", "awslabs_core_mcp_server"),
            ("awslabs-aws-serverless-mcp-server", "awslabs_aws_serverless_mcp_server")
        ]
        
        for package_name, import_name in mcp_packages:
            try:
                __import__(import_name)
                print(f"✅ {package_name} installed")
                details.append(f"{package_name} available")
            except ImportError:
                print(f"⚠️  {package_name} missing (may impact CDK functionality)")
                details.append(f"{package_name} missing")
        
        self.results["dependencies"] = {"status": status, "details": details}
    
    def validate_architecture(self):
        """Validate project architecture readiness"""
        print("\n5️⃣ Architecture Validation")
        print("-" * 30)
        
        details = []
        status = "PASS"
        
        # Check Lambda functions
        lambda_dirs = [
            "src/lambda_functions/investment_metrics",
            "src/lambda_functions/financial_data",
            "src/lambda_functions/ticket_creation"
        ]
        
        for lambda_dir in lambda_dirs:
            if os.path.exists(lambda_dir) and os.path.exists(f"{lambda_dir}/lambda_function.py"):
                print(f"✅ Lambda function: {lambda_dir}")
                details.append(f"Lambda ready: {os.path.basename(lambda_dir)}")
            else:
                print(f"❌ Lambda function missing: {lambda_dir}")
                status = "FAIL"
                details.append(f"Lambda missing: {os.path.basename(lambda_dir)}")
        
        # Check Bedrock adapter
        if os.path.exists("src/bedrock_agent/bedrock_adapter.py"):
            print("✅ Bedrock adapter ready")
            details.append("Bedrock adapter implemented")
        else:
            print("❌ Bedrock adapter missing")
            status = "FAIL"
            details.append("Bedrock adapter missing")
        
        # Check common utilities
        if os.path.exists("src/common/logger.py"):
            print("✅ Common utilities ready")
            details.append("Common utilities available")
        else:
            print("❌ Common utilities missing")
            status = "FAIL"
            details.append("Common utilities missing")
        
        self.results["architecture"] = {"status": status, "details": details}
    
    def generate_assessment(self):
        """Generate overall assessment"""
        print("\n6️⃣ Overall Assessment")
        print("-" * 30)
        
        # Count passing checks
        passing_checks = sum(1 for check in self.results.values() 
                           if isinstance(check, dict) and check.get("status") == "PASS")
        total_checks = len([k for k in self.results.keys() if k != "overall"])
        
        # Determine readiness
        critical_checks = ["credentials", "permissions", "architecture"]
        critical_passing = all(self.results[check]["status"] == "PASS" for check in critical_checks)
        
        ready_for_cdk = critical_passing and passing_checks >= 4
        
        if ready_for_cdk:
            print("🎉 READY FOR CDK DEPLOYMENT")
            status = "PASS"
        else:
            print("❌ NOT READY FOR CDK DEPLOYMENT")
            status = "FAIL"
        
        print(f"Checks passed: {passing_checks}/{total_checks}")
        
        # Provide recommendations
        recommendations = []
        if self.results["credentials"]["status"] != "PASS":
            recommendations.append("Configure AWS credentials using environment variables or AWS profiles")
        if self.results["permissions"]["status"] != "PASS":
            recommendations.append("Ensure AWS IAM permissions for required services")
        if self.results["services"]["status"] != "PASS":
            recommendations.append("Verify Bedrock service access and model permissions")
        if self.results["architecture"]["status"] != "PASS":
            recommendations.append("Complete Lambda function implementations")
        
        self.results["overall"] = {
            "status": status,
            "ready_for_cdk": ready_for_cdk,
            "checks_passed": f"{passing_checks}/{total_checks}",
            "recommendations": recommendations
        }
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        
        for section, result in self.results.items():
            if section == "overall":
                continue
            status_emoji = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_emoji} {section.upper()}: {result['status']}")
        
        print(f"\n🎯 OVERALL: {self.results['overall']['status']}")
        print(f"📊 CDK Ready: {self.results['overall']['ready_for_cdk']}")
        
        if self.results["overall"]["recommendations"]:
            print("\n📝 RECOMMENDATIONS:")
            for i, rec in enumerate(self.results["overall"]["recommendations"], 1):
                print(f"{i}. {rec}")

def main():
    """Main validation function"""
    validator = AWSCDKValidator()
    results = validator.validate_all()
    validator.print_summary()
    
    # Save results to file
    with open("aws_cdk_validation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: aws_cdk_validation_report.json")
    
    return 0 if results["overall"]["ready_for_cdk"] else 1

if __name__ == "__main__":
    sys.exit(main()) 