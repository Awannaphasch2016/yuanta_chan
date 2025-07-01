# Test Suite

This directory contains comprehensive tests for the chatbot infrastructure components.

## Portfolio News Tests

### `test_portfolio_news.py`
Unit tests for the Portfolio News Lambda function:
- Service initialization and configuration
- Client portfolio lookup functionality  
- Error handling and response formats
- Lambda handler with different input formats
- Mock client portfolio testing

**Run with:**
```bash
python src/tests/test_portfolio_news.py
```

### `test_client_portfolios.py`
Comprehensive demonstration of client portfolio functionality:
- Tests all mock client portfolios (alice, bob, charlie, diana)
- Unknown client fallback testing
- Direct ticker vs client lookup comparison
- Real API integration (when API keys are available)

**Run with:**
```bash
python src/tests/test_client_portfolios.py
```

### `test_portfolio_news_integration.py`
Integration tests for the complete portfolio news workflow.

### `test_news_client.py`
Tests for the news client module and external API integrations.

## Other Component Tests

### `test_financial_data.py`
Tests for financial data retrieval functionality.

### `test_ticket_creation.py`
Tests for the ticket creation Lambda function.

### `test_yahoo_finance.py`
Tests specifically for Yahoo Finance API integration.

## Mock Client Portfolios

The tests use the following mock client data:

| Client | Portfolio Type | Holdings |
|--------|----------------|----------|
| alice | Growth Portfolio | AAPL, MSFT, GOOGL, TSLA |
| bob | Conservative Portfolio | XOM, CVX, JPM, BAC, WMT |
| charlie | Tech Portfolio | NVDA, AMD, INTC, QCOM, AVGO |
| diana | Diversified ETF Portfolio | SPY, QQQ, VTI, VXUS, BND |
| default | Demo Portfolio | AAPL, TSLA, GOOGL |

## Running Tests

### Individual Tests
```bash
# Portfolio news unit tests
python src/tests/test_portfolio_news.py

# Client portfolio demonstration
python src/tests/test_client_portfolios.py

# News client tests
python src/tests/test_news_client.py
```

### All Tests (if pytest is available)
```bash
python -m pytest src/tests/ -v
```

## Environment Variables

For tests that use real APIs, set these environment variables:
```bash
export NEWSAPI_KEY="your_newsapi_key"
export NEWSDATA_API_KEY="your_newsdata_key"
```

Or use the helper scripts in the project root:
```bash
# PowerShell
.\set_env_vars.ps1

# Windows CMD
set_env_vars.bat
``` 