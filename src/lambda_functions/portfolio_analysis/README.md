# Portfolio Analysis Lambda Function

## Overview

The Portfolio Analysis Lambda function provides comprehensive portfolio analysis capabilities for the PortfolioBot AI Chatbot. It handles all PRD-specified query types including client portfolio overviews, performance reports, risk analysis, and compliance monitoring.

## Features

### Supported Analysis Types

1. **Portfolio Overview** (`overview`)
   - Total portfolio value and performance
   - Top holdings analysis
   - Sector allocation breakdown
   - Risk metrics summary

2. **Performance Reports** (`performance`)
   - Monthly/quarterly/annual performance reports
   - Benchmark comparison
   - Asset-level performance analysis
   - Risk-adjusted returns

3. **Holdings Analysis** (`holdings`)
   - Current holdings breakdown
   - Position sizing analysis
   - Asset allocation review

4. **Transaction Analysis** (`transactions`)
   - Recent transaction history
   - Transaction pattern analysis
   - Trade impact assessment

5. **Risk Analysis** (`risk`)
   - Portfolio risk metrics (Beta, Sharpe ratio, volatility)
   - Value at Risk (VaR) calculations
   - Risk contribution by asset
   - Risk alerts and warnings

6. **Comparative Analysis** (`comparison`)
   - Client-to-client performance comparison
   - Benchmark comparison
   - Peer analysis

7. **Sector Breakdown** (`sector_breakdown`)
   - Sector allocation analysis
   - Sector performance comparison
   - Rebalancing recommendations

8. **Alerts & Notifications** (`alerts`)
   - Portfolio value change alerts
   - Rebalancing notifications
   - Risk threshold breaches
   - Compliance alerts

9. **Personal Portfolio** (`personal_portfolio`)
   - Employee personal portfolio analysis
   - Performance tracking
   - Personal investment insights

10. **Compliance & Audit** (`compliance`)
    - Unusual transaction detection
    - Regulatory compliance checks
    - Audit trail analysis

## Usage

### Basic Function Call

```python
import json
from lambda_function import lambda_handler

# Portfolio overview example
event = {
    "analysis_type": "overview",
    "client_name": "John Smith"
}

response = lambda_handler(event, None)
result = json.loads(response['body'])
```

### Event Structure

```json
{
    "analysis_type": "overview|performance|holdings|transactions|risk|comparison|sector_breakdown|alerts|personal_portfolio|compliance",
    "client_name": "John Smith",  // Optional for client-specific queries
    "employee_name": "Jane Doe",  // Optional for employee queries
    "additional_params": {
        "period": "monthly|quarterly|annual",  // For performance reports
        "client1": "John Smith",               // For comparison
        "client2": "Sarah Johnson",            // For comparison
        "threshold": 0.05                      // For alerts (5% threshold)
    }
}
```

### Response Structure

```json
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": {
        "client_name": "John Smith",
        "analysis_type": "portfolio_overview",
        "summary": {
            "total_portfolio_value": 250000,
            "total_gain_loss": 12500,
            "total_return_percentage": 8.5,
            "number_of_holdings": 15
        },
        "top_holdings": [...],
        "sector_allocation": {...},
        "risk_metrics": {...},
        "insights": [...],
        "performance_metrics": {
            "analysis_time_seconds": 0.045,
            "timestamp": "2025-01-13T12:00:00Z",
            "analysis_type": "overview"
        },
        "success": true
    }
}
```

## Example Queries and Responses

### 1. Portfolio Overview

**Query**: "Show me an overview of John Smith's portfolio"

**Event**:
```json
{
    "analysis_type": "overview",
    "client_name": "John Smith"
}
```

**Response**: Complete portfolio summary with holdings, allocation, and risk metrics.

### 2. Performance Report

**Query**: "Generate the monthly report for Sarah Johnson"

**Event**:
```json
{
    "analysis_type": "performance",
    "client_name": "Sarah Johnson",
    "additional_params": {
        "period": "monthly"
    }
}
```

### 3. Risk Analysis

**Query**: "Show risk metrics for John Smith's portfolio"

**Event**:
```json
{
    "analysis_type": "risk",
    "client_name": "John Smith"
}
```

### 4. Client Comparison

**Query**: "Compare performance between John Smith and Sarah Johnson"

**Event**:
```json
{
    "analysis_type": "comparison",
    "additional_params": {
        "client1": "John Smith",
        "client2": "Sarah Johnson"
    }
}
```

### 5. Portfolio Alerts

**Query**: "Which clients need portfolio rebalancing?"

**Event**:
```json
{
    "analysis_type": "alerts",
    "additional_params": {
        "threshold": 0.05
    }
}
```

## Mock Data

The function includes comprehensive mock data for demonstration purposes:

- **John Smith**: Technology-heavy portfolio ($250K value)
- **Sarah Johnson**: Diversified portfolio ($180K value)

Each mock portfolio includes:
- Holdings with market values and gains/losses
- Risk metrics (beta, Sharpe ratio, volatility)
- Sector allocations
- Performance history

## Dependencies

- `boto3`: AWS SDK for Python
- `requests`: For external API calls (Yahoo Finance)
- Standard Python libraries: `json`, `datetime`, `typing`

## Deployment

### As AWS Lambda Function

1. Package the function with dependencies:
```bash
cd src/lambda_functions/portfolio_analysis
zip -r portfolio_analysis.zip .
```

2. Create Lambda function in AWS Console or via CLI:
```bash
aws lambda create-function \
    --function-name portfolio-analysis \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://portfolio_analysis.zip
```

### Environment Variables

No environment variables required for basic operation. For production:

- `LOG_LEVEL`: Set logging level (INFO, DEBUG, WARNING, ERROR)
- `YAHOO_FINANCE_API_KEY`: If using premium Yahoo Finance API
- `DATABASE_URL`: For persistent portfolio data storage

## Integration with Bedrock Agent

This Lambda function is designed to work as a tool for Amazon Bedrock Agents. Configure the agent with the following tool schema:

```json
{
    "toolSpec": {
        "name": "portfolio_analysis_tool",
        "description": "Comprehensive portfolio analysis for investment consultants",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["overview", "performance", "holdings", "transactions", "risk", "comparison", "sector_breakdown", "alerts", "personal_portfolio", "compliance"],
                        "description": "Type of portfolio analysis to perform"
                    },
                    "client_name": {
                        "type": "string",
                        "description": "Name of the client for analysis"
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "Name of the employee for personal portfolio analysis"
                    },
                    "additional_params": {
                        "type": "object",
                        "description": "Additional parameters for specific analysis types"
                    }
                },
                "required": ["analysis_type"]
            }
        }
    }
}
```

## Performance

- **Target Response Time**: < 3 seconds
- **Typical Response Time**: < 1 second for overview and risk analysis
- **Memory Usage**: ~128MB recommended
- **Timeout**: 30 seconds recommended

## Error Handling

The function includes comprehensive error handling:

- Invalid analysis types
- Missing client data
- API failures
- Calculation errors

All errors return structured responses with:
- Error message
- Timestamp
- Success flag (false)
- HTTP status code

## Testing

Run local tests:

```bash
cd src/lambda_functions/portfolio_analysis
python3 lambda_function.py
```

This will execute a test portfolio overview for "John Smith" and display the results.

## Future Enhancements

1. **Real Data Integration**: Replace mock data with actual portfolio databases
2. **Advanced Analytics**: Machine learning-based insights and predictions
3. **Real-time Updates**: Live market data integration
4. **Custom Benchmarks**: Client-specific benchmark comparisons
5. **Regulatory Compliance**: Enhanced compliance monitoring and reporting
6. **Multi-currency Support**: International portfolio support

## Support

For questions or issues with the Portfolio Analysis Lambda function, please refer to the project documentation or contact the development team. 