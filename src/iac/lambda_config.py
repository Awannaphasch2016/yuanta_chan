"""
AWS Lambda Configuration for InHouse AI Chatbot Infrastructure
Basic configuration for testing purposes.
"""

class LambdaConfig:
    """Configuration class for AWS Lambda functions."""
    
    # Common configuration across all Lambda functions
    COMMON_CONFIG = {
        "runtime": "python3.12",
        "timeout": 30,
        "memory_size": 512,
        "environment_variables": {
            "LOG_LEVEL": "INFO",
            "PYTHONPATH": "/var/task/src"
        }
    }
    
    # Lambda-specific configurations
    LAMBDA_FUNCTIONS = {
        "investment-metrics": {
            "function_name": "InHouseAI-InvestmentMetrics",
            "description": "Investment analysis and metrics calculation",
            "handler": "lambda_function.lambda_handler",
            "runtime": "python3.12",
            "timeout": 60,
            "memory_size": 1024,
            "environment_variables": {
                "LOG_LEVEL": "INFO",
                "DATA_SOURCE": "yahoo_finance",
                "CACHE_TTL": "300"
            }
        },
        "financial-data": {
            "function_name": "InHouseAI-FinancialData",
            "description": "Financial data retrieval and processing",
            "handler": "lambda_function.lambda_handler",
            "runtime": "python3.12",
            "timeout": 60,
            "memory_size": 1024,
            "environment_variables": {
                "LOG_LEVEL": "INFO",
                "DATA_SOURCE": "yahoo_finance",
                "API_VERSION": "v2"
            }
        }
    }
    
    @classmethod
    def get_function_config(cls, function_name: str):
        """Get configuration for a specific Lambda function."""
        if function_name not in cls.LAMBDA_FUNCTIONS:
            raise ValueError(f"Unknown function: {function_name}")
        return cls.LAMBDA_FUNCTIONS[function_name]


if __name__ == "__main__":
    # Example usage
    config = LambdaConfig()
    print("Lambda configuration loaded successfully")