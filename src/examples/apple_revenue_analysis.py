"""
Example script demonstrating how to analyze Apple's revenue streams
using yfinance directly.
"""

import yfinance as yf
from datetime import datetime

def analyze_apple_revenue():
    """
    Analyze Apple's revenue streams and business model
    """
    try:
        # Get Apple stock data
        aapl = yf.Ticker("AAPL")
        
        # Get company info
        info = aapl.info
        
        # Get financial data
        financials = aapl.financials
        balance_sheet = aapl.balance_sheet
        cash_flow = aapl.cash_flow
        
        # Extract key metrics
        company_name = info.get('longName', 'Apple Inc.')
        sector = info.get('sector', 'Technology')
        industry = info.get('industry', 'Consumer Electronics')
        
        # Get revenue data
        total_revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
        gross_profit = financials.loc['Gross Profit'].iloc[0] if 'Gross Profit' in financials.index else None
        net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else None
        
        # Calculate margins
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue and gross_profit else None
        net_margin = (net_income / total_revenue * 100) if total_revenue and net_income else None
        
        # Get revenue by segment
        revenue_by_segment = {
            'iPhone': info.get('iPhoneRevenue', 0),
            'Services': info.get('servicesRevenue', 0),
            'Mac': info.get('macRevenue', 0),
            'iPad': info.get('iPadRevenue', 0),
            'Wearables': info.get('wearablesRevenue', 0)
        }
        
        # Print analysis
        print(f"\n📊 {company_name} Revenue Analysis")
        print("=" * 50)
        print(f"Sector: {sector}")
        print(f"Industry: {industry}")
        
        if total_revenue:
            print(f"\n💰 Total Revenue: ${total_revenue:,.2f}")
            print(f"💵 Gross Profit: ${gross_profit:,.2f}")
            print(f"📈 Net Income: ${net_income:,.2f}")
            
            if gross_margin:
                print(f"📊 Gross Margin: {gross_margin:.1f}%")
            if net_margin:
                print(f"📊 Net Margin: {net_margin:.1f}%")
        
        print("\n📱 Revenue by Segment:")
        for segment, revenue in revenue_by_segment.items():
            if revenue:
                print(f"- {segment}: ${revenue:,.2f}")
        
        # Get growth metrics
        revenue_growth = info.get('revenueGrowth', 0) * 100
        earnings_growth = info.get('earningsGrowth', 0) * 100
        
        print("\n📈 Growth Metrics:")
        print(f"- Revenue Growth: {revenue_growth:.1f}%")
        print(f"- Earnings Growth: {earnings_growth:.1f}%")
        
        # Get market metrics
        market_cap = info.get('marketCap', 0)
        pe_ratio = info.get('forwardPE', 0)
        
        print("\n📊 Market Metrics:")
        print(f"- Market Cap: ${market_cap:,.2f}")
        print(f"- Forward P/E Ratio: {pe_ratio:.2f}")
        
        # Print business model summary
        print("\n💡 Business Model Summary:")
        print("Apple generates revenue through multiple streams:")
        print("1. Hardware Sales: iPhone, Mac, iPad, and Wearables")
        print("2. Services: App Store, iCloud, Apple Music, Apple TV+, etc.")
        print("3. Other Products: Accessories and other hardware")
        
        print("\n🚀 Key Strengths:")
        print("- Strong brand loyalty and ecosystem")
        print("- High-margin services business")
        print("- Premium product positioning")
        print("- Global market presence")
        
    except Exception as e:
        print(f"❌ Error analyzing Apple's revenue: {str(e)}")

if __name__ == "__main__":
    analyze_apple_revenue() 