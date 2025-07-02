"""
CDK Shared Constructs Package

This package provides reusable AWS CDK constructs for the YuantaChan investment analysis platform.

Available constructs:
- InvestmentProcessor: Lambda function for investment analysis and metrics calculation
- FinancialCollector: Lambda function for financial data collection from external APIs
- BedrockAdapter: Lambda function for Bedrock Agent integration
"""

from .investment_processor import InvestmentProcessor
from .financial_collector import FinancialCollector
from .bedrock_adapter import BedrockAdapter

__all__ = [
    "InvestmentProcessor",
    "FinancialCollector", 
    "BedrockAdapter",
]

__version__ = "0.1.0" 