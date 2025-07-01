import sys
import json
import os

# Set environment variables BEFORE importing lambda function
os.environ["NEWSAPI_KEY"] = "88c06ae3a76d41b988fd1b6d4468e123"
os.environ["NEWSDATA_API_KEY"] = "pub_e8de0f08568146bfbec24646f3c2b4de"

sys.path.append('src/lambda_functions/portfolio_news')
sys.path.append('src/lambda_functions/financial_data')

from src.lambda_functions.portfolio_news.lambda_function import lambda_handler
# Test with client lookup
event = {
    'client_name': 'alice',
    'timeframe': '7d'
}

# Alternative: Test with direct tickers
# event = {
#     'tickers': ['NVDA', 'AMZN', 'GOOGL'],
#     'timeframe': '7d'
# }

result = lambda_handler(event, {})

# Print the whole result to see the structure (optional for debugging)
# print(json.dumps(result, indent=2))

# Try to extract news from the nested structure (Bedrock Agent format)
try:
    # If your lambda returns the Bedrock Agent format:
    body = result['response']['functionResponse']['responseBody']['TEXT']['body']
    data = json.loads(body)
    news = data.get('news', [])
except Exception:
    # If your lambda returns a plain dict with 'news' at the top level:
    news = result.get('news', [])

print('News articles found:', len(news))
print('--- Sample News ---')
for article in news[:3]:
    print(f"{article.get('title', 'No title')} - {article.get('source', 'Unknown')}")

environment={
    "LOG_LEVEL": "INFO",
    "NEWSAPI_KEY": "88c06ae3a76d41b988fd1b6d4468e123",
    "NEWSDATA_API_KEY": "pub_e8de0f08568146bfbec24646f3c2b4de"
} 