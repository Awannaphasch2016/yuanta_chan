# Technical Context

## Platform Detection
- **OS**: Windows 10.0.22631
- **Shell**: PowerShell
- **Language**: Python 3.12+
- **Package Manager**: Poetry
- **Cloud**: AWS (native services only)

## Technology Stack
- Amazon Bedrock (Agents for LLM orchestration)
- AWS Lambda (business logic and tool execution)
- API Gateway (optional)
- DynamoDB (optional)

## External Integrations
- Yahoo Finance API: Financial data retrieval
  - yfinance library (v0.2.63) configured
- Internal Systems: Mock ticketing for demo

## Architecture Pattern
User  Bedrock Agent  Lambda Tools  External APIs

## Key Decisions
- No RAG or vector databases in v1
- No complex IAM integration for pilot
- Ephemeral data storage for demo
- Direct API integration through Lambda tools
