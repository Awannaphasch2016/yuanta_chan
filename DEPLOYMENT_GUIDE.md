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
        