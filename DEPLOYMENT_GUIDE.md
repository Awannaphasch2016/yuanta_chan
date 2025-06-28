# 🚀 AWS CDK Deployment Guide - Poetry Edition

## Project Package Management
This project uses **Poetry** for Python package management, not pip. All dependencies are managed through `pyproject.toml`.

## 🎯 DEPLOYMENT STEPS

### 1️⃣ Install CDK CLI:
```powershell
npm install -g aws-cdk
```

### 2️⃣ Set AWS Credentials:
```powershell
$env:AWS_ACCESS_KEY_ID="<YOUR_AWS_ACCESS_KEY_ID>"
$env:AWS_SECRET_ACCESS_KEY="<YOUR_AWS_SECRET_ACCESS_KEY>"
$env:AWS_REGION="<YOUR_AWS_REGION>"
$env:AWS_ACCOUNT_ID="<YOUR_AWS_ACCOUNT_ID>"
```

### 3️⃣ Navigate to project root and install dependencies:
```powershell
# From project root (yuanta_chan/)
poetry install
```

### 4️⃣ Choose your deployment option:

#### Option A: Investment Metrics Only (Testing)
```powershell
cd cdk/investment-metrics
python deploy.py
```

#### Option B: Full Chatbot Infrastructure
```powershell
cd cdk/full-chatbot
cdk bootstrap aws://<YOUR_AWS_ACCOUNT_ID>/<YOUR_AWS_REGION>
cdk deploy ChatbotInfrastructureStack --require-approval never
```

### 7️⃣ Verify deployment:
```powershell
aws lambda list-functions --region <YOUR_AWS_REGION>
```

## 📋 Expected Resources:
- **4 Lambda Functions**: 
  - ChatbotInvestmentMetrics
  - ChatbotFinancialData  
  - ChatbotTicketCreation
  - ChatbotBedrockAdapter
- **2 IAM Roles**: Lambda execution role, Bedrock agent role
- **4 CloudWatch Log Groups**: For monitoring and debugging
- **All necessary permissions**: Bedrock, Lambda, IAM access

## 🚀 Post-Deployment:
- Test Lambda functions with sample data
- Configure Bedrock Agent with deployed adapter
- Set up monitoring and alerts

## 📦 Package Management Notes:
- **Primary tool**: Poetry (configured in `pyproject.toml`)
- **CDK dependencies**: Already included in Poetry configuration
- **Development dependencies**: pytest for testing
- **MCP servers**: awslabs MCP servers for enhanced AWS integration

## 🔧 Troubleshooting:
- Ensure Poetry is installed: `poetry --version`
- Check AWS credentials: `aws sts get-caller-identity`
- Validate CDK: `cdk --version`
- Run validation script: `python validate_aws_cdk_readiness.py`
        