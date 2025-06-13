# Project Brief: InHouse AI Chatbot Infrastructure

## Project Overview
Building a fully in-house, AWS-native AI chatbot infrastructure for a brokerage company using Amazon Bedrock Agents and AWS Lambda functions.

## Target Users
- Primary: Internal Investment Consultants (ICs)
- Future: Company employees and clients

## Core Objectives
- Conversational interface for natural language access to internal/external systems
- Multi-turn reasoning and intelligent task execution
- Quick wins with measurable productivity improvements
- Incremental extensibility for future use cases

## Architecture Principles
- All AWS-native services
- Amazon Bedrock + Agents for orchestration
- AWS Lambda for business logic (tools)
- No RAG, complex IAM, or CI/CD in v1
- Focus on simplicity and immediate value

## Core Use Cases
1. Investment Insight Assistant (stock analysis)
2. Financial Data Lookup (earnings, metrics)
3. Internal Ticket Routing (support tickets)

## Success Metrics
- 30% time reduction vs manual process
- 3 major workflows in v1
- 90% response accuracy
- <2s tool call latency
- 10 active IC users in pilot

## Technology Stack
- Amazon Bedrock (Agents)
- AWS Lambda
- DynamoDB (optional)
- API Gateway (optional)
- Yahoo Finance API integration

## Current Status
- Memory Bank initialized
- Project requirements documented
- Ready for planning phase
