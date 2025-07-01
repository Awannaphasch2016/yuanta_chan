#!/usr/bin/env python3
"""
Test script to demonstrate client portfolio functionality
"""

import sys
import json
import os

# Set environment variables BEFORE importing lambda function
os.environ["NEWSAPI_KEY"] = "88c06ae3a76d41b988fd1b6d4468e123"
os.environ["NEWSDATA_API_KEY"] = "pub_e8de0f08568146bfbec24646f3c2b4de"

# Add the lambda function directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'portfolio_news'))

from lambda_function import lambda_handler

def test_client_portfolio(client_name, timeframe='24h'):
    """Test portfolio news for a specific client"""
    print(f"\n{'='*60}")
    print(f"Testing Portfolio News for Client: {client_name}")
    print(f"{'='*60}")
    
    event = {
        'client_name': client_name,
        'timeframe': timeframe
    }
    
    result = lambda_handler(event, {})
    
    # Extract and display results
    try:
        body = result['response']['functionResponse']['responseBody']['TEXT']['body']
        data = json.loads(body)
        
        if data.get('success'):
            print(f"✅ Success!")
            if 'client' in data:
                client_info = data['client']
                print(f"📋 Client: {client_info['name']}")
                print(f"💼 Account Type: {client_info['account_type']}")
                print(f"📅 Last Updated: {client_info['last_updated']}")
            
            print(f"📈 Tickers: {', '.join(data['tickers'])}")
            print(f"📰 News Articles: {len(data['news'])}")
            print(f"💰 Price Quotes: {len(data['prices'])}")
            
            # Show sample news
            if data['news']:
                print(f"\n📰 Sample News Headlines:")
                for i, article in enumerate(data['news'][:3], 1):
                    print(f"  {i}. {article['title']} - {article['source']}")
            
            # Show price summary
            if data['prices']:
                print(f"\n💰 Price Summary:")
                for price in data['prices']:
                    change_symbol = "📈" if price['change_percent'] > 0 else "📉" if price['change_percent'] < 0 else "➡️"
                    print(f"  {change_symbol} {price['ticker']}: ${price['price']:.2f} ({price['change_percent']:+.2f}%)")
        else:
            print(f"❌ Error: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")
        print(f"Raw response: {result}")

def main():
    """Test all client portfolios"""
    print("🚀 Client Portfolio News Tool - Demonstration")
    print("=" * 60)
    
    print(f"🔑 Using API Keys - NewsAPI: {os.environ.get('NEWSAPI_KEY')[:10]}...")
    print(f"🔑 Using API Keys - NewsData: {os.environ.get('NEWSDATA_API_KEY')[:10]}...")
    
    # Test different clients
    test_clients = [
        ('alice', '24h'),
        ('bob', '48h'),
        ('charlie', '7d'),
        ('diana', '24h'),
        ('unknown_client', '24h')  # This should fall back to default
    ]
    
    for client_name, timeframe in test_clients:
        test_client_portfolio(client_name, timeframe)
    
    # Test with direct tickers (no client)
    print(f"\n{'='*60}")
    print(f"Testing Direct Tickers (No Client)")
    print(f"{'='*60}")
    
    event = {
        'tickers': ['TSLA', 'NVDA'],
        'timeframe': '7d'
    }
    
    result = lambda_handler(event, {})
    
    try:
        body = result['response']['functionResponse']['responseBody']['TEXT']['body']
        data = json.loads(body)
        
        if data.get('success'):
            print(f"✅ Success!")
            print(f"📈 Tickers: {', '.join(data['tickers'])}")
            print(f"📰 News Articles: {len(data['news'])}")
            print(f"💰 Price Quotes: {len(data['prices'])}")
            print(f"👤 Client Info: {'Not provided (direct ticker lookup)' if 'client' not in data else data['client']['name']}")
        else:
            print(f"❌ Error: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")
    
    print(f"\n{'='*60}")
    print("✨ Demonstration Complete!")
    print("💡 Available clients: alice, bob, charlie, diana")
    print("📋 Each client has a different portfolio composition")
    print("🔄 You can also use direct 'tickers' parameter instead of 'client_name'")
    print("=" * 60)

if __name__ == "__main__":
    main() 