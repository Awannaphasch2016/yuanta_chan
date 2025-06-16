# Bedrock Agent Integration for Investment Analysis

This directory contains the implementation of Amazon Bedrock Agent integration that enables natural language processing for the investment analysis system.

## Overview

The Bedrock Agent Integration allows clients to ask questions in natural language (e.g., "How does Apple make money?") and receive intelligent, structured responses powered by Claude 3 Sonnet and the existing Lambda-based investment analysis system.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│                 │    │                  │    │                     │
│   Client Query  │───▶│  Bedrock Agent   │───▶│   Lambda Functions  │
│                 │    │                  │    │                     │
│ "How does AAPL  │    │ - Claude 3 Sonnet│    │ - Investment Metrics│
│  make money?"   │    │ - Tool Selection │    │ - Financial Data    │
│                 │    │ - Response Gen   │    │ - Ticket Creation   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                │                          │
                                │                          │
                                ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────────┐
                       │                  │    │                     │
                       │ Structured       │    │   Yahoo Finance     │
                       │ Natural Language │    │   API Integration   │
                       │ Response         │    │                     │
                       └──────────────────┘    └─────────────────────┘
```

## Components

### 1. Bedrock Agent Adapter (`bedrock_adapter.py`)
- **Purpose**: Converts Bedrock Agent requests to Lambda function calls
- **Features**:
  - Handles investment analysis requests
  - Formats responses for natural language consumption
  - Implements error handling and validation
  - Provides professional financial disclaimers

### 2. Agent Configuration (`agent_config.json`)
- **Purpose**: Defines Bedrock Agent settings and behavior
- **Features**:
  - Claude 3 Sonnet model configuration
  - Professional investment assistant instructions
  - Tool integration specifications
  - Session management settings

### 3. Tool Schema (`investment_tools_schema.json`)
- **Purpose**: OpenAPI schema defining available tools
- **Features**:
  - Investment analysis tool definition
  - Financial data retrieval tool definition
  - Parameter validation and documentation

### 4. Deployment Script (`deploy_agent.py`)
- **Purpose**: Automated deployment of Bedrock Agent infrastructure
- **Features**:
  - IAM role creation for Bedrock Agent
  - Lambda function deployment
  - Agent and action group configuration
  - End-to-end testing capabilities

### 5. Test Suite (`test_integration.py`)
- **Purpose**: Comprehensive testing of integration components
- **Features**:
  - Local adapter testing
  - Conversation flow simulation
  - Response formatting validation
  - Error handling verification

## Usage Examples

### Example 1: Investment Analysis Query
**User Input**: "How does Apple make money?"

**Agent Process**:
1. Bedrock Agent interprets query as investment analysis request
2. Agent calls `analyze_investment` tool with ticker "AAPL"
3. Lambda returns comprehensive financial analysis
4. Agent generates structured natural language response

**Sample Response**:
```
📊 Investment Analysis: Apple Inc. (AAPL)

💰 Current Price: $150.12
🎯 Recommendation: Buy
📈 Investment Score: 78.5/100
🔍 Confidence: High

📋 Key Insights:
• Excellent profit margins of 24.0%
• Strong ROE of 28.2%
• Conservative debt levels (D/E: 31.2)

🚀 Growth Opportunities:
• Strong earnings growth trajectory (7.8%)
• Attractive dividend yield (0.5%)

⚠️ Disclaimer: This analysis is for informational purposes only and should not be considered as financial advice.
```

### Example 2: Multi-turn Conversation
**User Input 1**: "Analyze Microsoft's financial health"
**Agent Response**: [Provides Microsoft analysis]

**User Input 2**: "How does it compare to Apple?"
**Agent Process**: Agent maintains context and provides comparative analysis

## Deployment

### Prerequisites
- AWS Account with Bedrock access
- Python 3.12+ environment
- AWS CLI configured
- Required IAM permissions

### Quick Deployment
```bash
# 1. Install dependencies
poetry install

# 2. Test locally
poetry run python src/bedrock_agent/test_integration.py

# 3. Deploy to AWS
poetry run python src/bedrock_agent/deploy_agent.py --account-id YOUR_ACCOUNT_ID --region us-east-1

# 4. Test deployed agent
poetry run python src/bedrock_agent/deploy_agent.py --account-id YOUR_ACCOUNT_ID --test
```

### Manual Deployment Steps
1. **Create IAM Role**: Set up Bedrock Agent service role with Lambda invoke permissions
2. **Deploy Lambda**: Package and deploy the `bedrock_adapter.py` as a Lambda function
3. **Create Agent**: Use AWS Console or CLI to create Bedrock Agent with Claude 3 Sonnet
4. **Configure Tools**: Register Lambda function as agent action group
5. **Test Integration**: Validate end-to-end functionality

## Configuration

### Environment Variables
- `AWS_REGION`: AWS region for deployment (default: us-east-1)
- `LOG_LEVEL`: Logging level (default: INFO)

### Agent Settings
- **Model**: Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0)
- **Session Timeout**: 30 minutes
- **Response Format**: Structured text with emojis and professional formatting

## Testing

### Local Testing
```bash
# Run comprehensive test suite
poetry run python src/bedrock_agent/test_integration.py

# Test specific components
poetry run python -c "from src.bedrock_agent.bedrock_adapter import BedrockAgentAdapter; adapter = BedrockAgentAdapter(); print('Adapter initialized successfully')"
```

### AWS Testing
```bash
# Test deployed agent
aws bedrock-agent-runtime invoke-agent \
  --agent-id YOUR_AGENT_ID \
  --agent-alias-id TSTALIASID \
  --session-id test-session \
  --input-text "How does Apple make money?"
```

## Performance

### Response Times
- **Local Testing**: ~0.5s for investment analysis
- **End-to-End (with LLM)**: <5s target response time
- **Tool Calling**: <2s for Lambda execution

### Scalability
- **Concurrent Sessions**: Supports multiple simultaneous conversations
- **Rate Limiting**: Managed by AWS Bedrock service limits
- **Cost Optimization**: Pay-per-use model with efficient token usage

## Error Handling

### Common Error Scenarios
1. **Invalid Ticker**: Graceful error message with suggestions
2. **Data Unavailable**: Fallback responses with alternative options
3. **Service Failures**: Retry mechanisms and user-friendly error messages
4. **Rate Limiting**: Automatic backoff and retry strategies

### Monitoring
- **CloudWatch Logs**: Comprehensive logging for debugging
- **Performance Metrics**: Response time and success rate tracking
- **Error Tracking**: Detailed error categorization and alerting

## Security

### IAM Permissions
- **Bedrock Agent Role**: Minimal permissions for model invocation and Lambda calling
- **Lambda Execution**: Standard Lambda execution role with CloudWatch logging
- **Data Protection**: No sensitive data stored or logged

### Compliance
- **Financial Disclaimers**: Automatic inclusion in all investment-related responses
- **Data Privacy**: No personal information stored or transmitted
- **Audit Trail**: Complete request/response logging for compliance

## Troubleshooting

### Common Issues
1. **Agent Not Responding**: Check IAM permissions and agent status
2. **Tool Calling Failures**: Verify Lambda function deployment and permissions
3. **Response Quality Issues**: Review agent instructions and tool schema
4. **Performance Problems**: Check CloudWatch metrics and optimize accordingly

### Debug Commands
```bash
# Check agent status
aws bedrock-agent get-agent --agent-id YOUR_AGENT_ID

# View Lambda logs
aws logs tail /aws/lambda/BedrockAgentAdapter --follow

# Test tool schema
poetry run python -c "import json; print(json.load(open('src/bedrock_agent/investment_tools_schema.json')))"
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: Support for additional languages beyond English
- **Advanced Analytics**: More sophisticated financial analysis capabilities
- **Voice Integration**: Amazon Polly integration for voice responses
- **Custom Models**: Fine-tuned models for financial domain expertise

### Integration Opportunities
- **Slack/Teams**: Direct integration with collaboration platforms
- **Mobile Apps**: Native mobile application support
- **Web Interface**: Browser-based chat interface
- **API Gateway**: RESTful API for third-party integrations

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review CloudWatch logs for detailed error information
3. Test components individually using the provided test scripts
4. Consult AWS Bedrock documentation for service-specific issues

## License

This implementation is part of the InHouse AI Chatbot Infrastructure project and follows the same licensing terms. 