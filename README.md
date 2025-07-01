# InHouse AI Chatbot Infrastructure for Brokerage Company

## Overview

This project delivers a fully in-house, AWS-native AI chatbot infrastructure for a brokerage company. The chatbot acts as a central interface for internal Investment Consultants (ICs), enabling them to:

- Retrieve investment insights and financial data (e.g., stock metrics, earnings)
- Create internal support tickets
- Interact with a scalable, extensible, and secure solution built entirely on AWS

The system leverages Amazon Bedrock Agents for LLM-based orchestration and AWS Lambda for business logic and integrations.

---

## Features

- **Conversational AI**: Multi-turn, context-aware chat powered by Amazon Bedrock Agents
- **Investment Insights**: Fetches key financial metrics for stocks using Yahoo Finance APIs
- **Financial Data Lookup**: Retrieves latest quarterly earnings and other financial data
- **Internal Ticket Creation**: Simulates internal support ticket creation for workflow automation
- **AWS-Native**: All components are serverless and managed via AWS (Bedrock, Lambda, API Gateway)
- **Extensible**: Easily add new tools and data sources as business needs grow

---

## Architecture

```
User (Investment Consultant)
   |
   v
Amazon Bedrock Agent (LLM Orchestrator)
   |
   v
[Invokes AWS Lambda Tools]
   - Investment Metrics Tool (Yahoo Finance)
   - Financial Data Lookup Tool (Yahoo Finance)
   - Ticket Creation Tool (Mock)
   |
   v
[Agent composes answer using LLM + tool results]
   |
   v
User receives final conversational response
```

---

## Core AWS Services

| Purpose                        | AWS Service                |
|---------------------------------|----------------------------|
| LLM orchestration (agent)      | Amazon Bedrock (Agents)    |
| Business logic execution       | AWS Lambda                 |
| API endpoint exposure (optional)| Amazon API Gateway         |
| Data storage (if needed)       | Amazon DynamoDB (optional) |

---

## Use Cases

1. **Investment Insight Assistant**  
   _"Is AAPL a good investment?"_  
   → Fetches and summarizes key financial metrics for a given stock.

2. **Financial Data Lookup**  
   _"Show me the latest quarterly earnings of TSLA."_  
   → Retrieves and presents the latest earnings data for a stock.

3. **Internal Ticket Routing**  
   _"Create a ticket for a failed trade settlement."_  
   → Simulates creation of an internal support ticket and returns a confirmation.

---

## Project Structure

```
Chatbot/
├── cdk/                  # AWS CDK infrastructure (optional for v1)
├── src/
│   ├── bedrock_agent/    # Bedrock agent config, adapters, and examples
│   ├── lambda_functions/ # Lambda code for each tool (financial data, metrics, ticketing)
│   ├── common/           # Shared utilities (e.g., Yahoo Finance client)
│   └── tests/            # Unit and integration tests
├── memory-bank/          # Task tracking, creative docs, and project context
├── DEPLOYMENT_GUIDE.md   # Step-by-step deployment instructions
├── prd.md                # Full Project Requirements Document
└── README.md             # (This file)
```

---

## Getting Started

### Prerequisites

- AWS account with access to Bedrock and Lambda
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) configured
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) (optional, for local Lambda testing)
- Python 3.9+ (for Lambda functions)
- RapidAPI key for Yahoo Finance (or use `yfinance` library for prototyping)

### Setup & Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/Takedaxz/chatbot-yuanta-intern
   cd Chatbot
   ```

2. **Configure AWS credentials**
   ```bash
   aws configure
   ```

3. **Set up Lambda environment variables**
   - Store your RapidAPI key securely (e.g., AWS Secrets Manager or Lambda environment variable).

4. **Deploy Lambda functions**
   - Use the AWS Console, AWS CLI, or SAM to deploy each Lambda in `src/lambda_functions/`.
   - Ensure each Lambda has the necessary dependencies (see `requirements.txt`).

5. **Configure Bedrock Agent**
   - In the AWS Console, create a Bedrock Agent and register the Lambda tools.
   - Use the provided input/output schemas for each tool (see [PRD](prd.md) for details).

6. **(Optional) Deploy API Gateway or Web UI**
   - For direct Lambda invocation or to expose a simple chat interface.

7. **Test the system**
   - Use the Bedrock Agent test console or your UI to run sample queries.

---

## Lambda Tool Specifications

Each Lambda function implements a specific tool for the Bedrock Agent:

- **InvestmentMetricsTool**: Returns key financial metrics for a stock ticker.
- **FinancialDataTool**: Returns latest quarterly earnings for a stock ticker.
- **TicketCreationTool**: Simulates creation of an internal support ticket.

See [PRD](prd.md) for full input/output schemas and example payloads.

---

## Security & Privacy

- No customer PII is handled in v1.
- API keys are stored securely and never exposed in code or responses.
- No persistent storage of tickets or conversation logs in the prototype.
- Access is limited to internal pilot users.

---

## Extending the System

- Add new Lambda tools for additional workflows (e.g., research reports, trade execution).
- Integrate with real internal systems (e.g., ticketing, CRM) in future phases.
- Add a web UI or chat integration (Slack, Teams) for broader access.
- Implement CI/CD and monitoring for production readiness.

---

## Documentation

- [Project Requirements Document (PRD)](prd.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [CDK Infrastructure (optional)](cdk/README.md)
- [Bedrock Agent & Lambda Tool Examples](src/bedrock_agent/README.md)

---

## License

This project is proprietary and intended for internal use by the brokerage company.

---

## Contact

For questions or contributions, please contact the project maintainer or your internal development team.

---

**Demo Success Criteria:**  
A successful demo will show an IC asking each type of question and the chatbot responding correctly and quickly, with measurable time savings and high accuracy.

---

_See the [PRD](prd.md) for full details on architecture, use cases, and future directions._
