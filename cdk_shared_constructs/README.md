# CDK Shared Constructs

Reusable CDK constructs for the Yuanta Chan investment analysis platform.

## Overview

This package provides shared CDK constructs that encapsulate common infrastructure patterns for AWS Lambda functions, API Gateway integrations, and other AWS resources used across the Yuanta Chan platform.

## Available Constructs

### InvestmentProcessor

A reusable construct for creating Lambda functions that perform investment analysis.

**Features:**
- Lambda function with Python 3.12 runtime
- IAM execution role with appropriate permissions
- CloudWatch log group with configurable retention
- Proper asset bundling for dependencies
- Auto-generated resource names for uniqueness

**Usage:**
```python
from cdk_shared_constructs import InvestmentProcessor

processor = InvestmentProcessor(
    self, "InvestmentProcessor",
    environment="prod",
    timeout=Duration.seconds(60),
    memory_size=1024
)
```

## Installation

This package is designed to be installed as a local Poetry dependency:

```bash
cd your-cdk-project
poetry add --editable ../path/to/cdk-shared-constructs
```

## Development

The constructs are designed to reference Lambda business logic from the main project's `src/lambda_functions/` directory, maintaining proper separation of concerns between infrastructure (constructs) and business logic (Lambda code).

## Architecture

- **Constructs**: Infrastructure patterns (how to deploy)
- **Lambda Code**: Business logic (what to deploy)
- **Separation**: Clean separation of concerns for maintainability 