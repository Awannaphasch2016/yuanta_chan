# Portfolio News Lambda Function

This AWS Lambda function provides portfolio-related news headlines and price data for multiple stock tickers. It's designed to integrate with Amazon Bedrock Agents as part of an AI chatbot infrastructure for investment consultants.

## Overview

The Portfolio News Tool fetches:
- Recent news headlines from multiple sources (Yahoo Finance, NewsAPI, Newsdata.io)
- Current stock prices and change percentages
- Comprehensive summary of news impact and price movements

## Input Schema

### Option 1: Direct Ticker Input
```json
{
  "tickers": ["AAPL", "TSLA", "XOM"],  // Array of stock symbols
  "timeframe": "24h"                    // Optional: "24h", "48h", "7d", "30d"
}
```

### Option 2: Client Portfolio Lookup
```json
{
  "client_name": "alice",              // Client identifier for portfolio lookup
  "timeframe": "24h"                    // Optional: "24h", "48h", "7d", "30d"
}
```

### Option 3: Mixed Input (client_name takes precedence)
```json
{
  "client_name": "bob",                // Will use Bob's portfolio
  "tickers": ["AAPL", "MSFT"],        // Ignored if client_name is valid
  "timeframe": "48h"
}
```

## Output Schema

```json
{
  "success": true,
  "tickers": ["AAPL", "TSLA", "XOM"],
  "timeframe": "24h",
  "news": [
    {
      "title": "Fed Holds Rates Steady, Markets Rally",
      "summary": "The Federal Reserve left interest rates unchanged...",
      "source": "Reuters",
      "published_at": "2025-01-13T14:00:00Z",
      "tickers": ["AAPL", "TSLA"],
      "url": "https://reuters.com/example",
      "relevance_score": 0.9
    }
  ],
  "prices": [
    {
      "ticker": "AAPL",
      "price": 196.33,
      "change_percent": 1.27,
      "timestamp": "2025-01-13T15:00:00Z"
    }
  ],
  "summary": {
    "total_news_articles": 5,
    "news_sources": {"Reuters": 2, "Bloomberg": 3},
    "total_tickers": 3,
    "price_summary": {
      "average_change_percent": 2.3,
      "tickers_up": 2,
      "tickers_down": 1,
      "tickers_unchanged": 0
    },
    "top_news_topics": ["federal", "rates", "earnings", "oil", "markets"]
  },
  "client": {                           // Only present when client_name is used
    "name": "Alice Johnson",
    "account_type": "Growth Portfolio", 
    "last_updated": "2025-01-13"
  },
  "timestamp": "2025-01-13T15:00:00.123456Z"
}
```

## Mock Client Portfolio Database

For demonstration and testing purposes, the function includes a mock client portfolio database with the following clients:

| Client Name | Full Name | Portfolio Type | Holdings |
|-------------|-----------|----------------|----------|
| `alice` | Alice Johnson | Growth Portfolio | AAPL, MSFT, GOOGL, TSLA |
| `bob` | Bob Smith | Conservative Portfolio | XOM, CVX, JPM, BAC, WMT |
| `charlie` | Charlie Davis | Tech Portfolio | NVDA, AMD, INTC, QCOM, AVGO |
| `diana` | Diana Wilson | Diversified ETF Portfolio | SPY, QQQ, VTI, VXUS, BND |
| `default` | Demo Client | Demo Portfolio | AAPL, TSLA, GOOGL |

### Client Lookup Behavior
- Client names are case-insensitive
- Unknown clients automatically fall back to the `default` portfolio
- Client information is included in the response when available
- Direct ticker input bypasses client lookup entirely

## Key Features

### Multi-Source News Aggregation
- **Yahoo Finance**: Primary source for ticker-specific news
- **NewsAPI**: Professional news sources (requires API key)
- **Newsdata.io**: Financial news aggregation (requires API key)

### Price Data Integration
- Real-time price quotes from Yahoo Finance
- Percentage change calculations
- Error handling for unavailable data

### Smart Content Processing
- Deduplication of similar articles
- Relevance scoring based on ticker mentions
- Topic extraction from headlines
- News-to-ticker mapping

### Caching & Performance
- 15-minute cache for news data
- 30-minute cache for price data
- Retry mechanism with exponential backoff
- Parallel data fetching where possible

## Dependencies

- `yfinance`: Stock price and basic news data
- `requests`: HTTP client for external APIs
- `newsapi-python`: NewsAPI client library
- `python-dotenv`: Environment variable management

## Environment Variables

Optional API keys for enhanced news coverage:
- `NEWSAPI_KEY`: For NewsAPI.org integration
- `NEWSDATA_API_KEY`: For Newsdata.io integration

Without these keys, the function falls back to Yahoo Finance news only.

## Usage Examples

### Bedrock Agent Integration
The function is designed to work with Amazon Bedrock Agents:

#### Direct Ticker Input
```json
{
  "messageVersion": "1.0",
  "actionGroup": "PortfolioNewsActionGroup",
  "function": "getPortfolioNews",
  "parameters": [
    {"name": "tickers", "value": ["AAPL", "TSLA", "XOM"]},
    {"name": "timeframe", "value": "24h"}
  ]
}
```

#### Client Portfolio Lookup
```json
{
  "messageVersion": "1.0",
  "actionGroup": "PortfolioNewsActionGroup", 
  "function": "getPortfolioNews",
  "parameters": [
    {"name": "client_name", "value": "alice"},
    {"name": "timeframe", "value": "48h"}
  ]
}
```

### Direct Lambda Invocation
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "timeframe": "48h"
}
```

### String Input Format
```json
{
  "tickers": "AAPL,MSFT,GOOGL",  // Comma-separated string
  "timeframe": "7d"
}
```

## Error Handling

The function gracefully handles various error scenarios:
- Invalid or missing tickers
- API rate limits and timeouts
- Network connectivity issues
- Malformed input data

Error responses follow the standard format:
```json
{
  "success": false,
  "error": "Missing required parameter: tickers",
  "timestamp": "2025-01-13T15:00:00.123456Z"
}
```

## Local Testing

### Run Built-in Tests
Run the module directly to test with mock data:
```bash
python lambda_function.py
```

This will execute several test cases and display the responses.

### Test Client Portfolio Functionality
Run the comprehensive client portfolio test:
```bash
python test_client_portfolios.py
```

This will test all mock clients and demonstrate the portfolio lookup functionality.

### Test Unknown Client Fallback
Test what happens with an unknown client:
```bash
python test_unknown_client.py
```

### Test with Real APIs
Test with actual news APIs (requires API keys):
```bash
python run_portfolio_news_real.py
```

## Deployment Notes

1. **Package Dependencies**: Ensure all dependencies are included in the deployment package
2. **Memory**: Recommend at least 512MB memory allocation
3. **Timeout**: Set timeout to 30-60 seconds for external API calls
4. **Environment**: Configure API keys in AWS Lambda environment or Secrets Manager
5. **IAM Permissions**: No special AWS permissions required beyond basic Lambda execution

## Integration with Bedrock Agents

This function is specifically designed to work as a tool within Amazon Bedrock Agents:

1. **Action Group**: Configure as "PortfolioNewsActionGroup"
2. **Function Name**: "getPortfolioNews"
3. **Input Schema**: Define tickers as array and timeframe as string
4. **Response Format**: JSON response wrapped in Bedrock Agent format

The agent can then process natural language queries like:
- "What news is affecting my portfolio today?"
- "Show me recent headlines for AAPL and TSLA"
- "What's the latest on my energy holdings?"
- "Get portfolio news for client Alice"
- "Show me Bob's portfolio news for the last 48 hours"
- "What's affecting Charlie's tech holdings?"

## Performance Considerations

- **API Rate Limits**: Built-in retry and backoff mechanisms
- **Caching**: Reduces redundant API calls
- **Concurrent Processing**: News and price data fetched in parallel
- **Response Size**: Limited to top 20 most relevant articles to manage payload size

## Monitoring & Logging

All operations are logged with structured JSON format including:
- Request parameters and timing
- API call success/failure rates  
- Cache hit/miss statistics
- Error details with context

Logs are available in CloudWatch for monitoring and debugging. 