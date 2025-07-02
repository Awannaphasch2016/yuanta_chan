import os
import aws_cdk as cdk
from portfolio_analysis_stack import PortfolioAnalysisStack

app = cdk.App()
PortfolioAnalysisStack(
    app, "PortfolioAnalysisStack",
    env=cdk.Environment(
        account=os.getenv('AWS_ACCOUNT_ID'),
        region=os.getenv('AWS_REGION')
    ),
    description="Standalone deployment for Portfolio Analysis Lambda"
)
app.synth() 