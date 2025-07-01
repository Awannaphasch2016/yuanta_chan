### 1. Workflow Diagram: AWS Bedrock Agent (with example query)

**Example Query:** "How does APPL make money?"

```mermaid
graph TD
    A["User: 'How does APPL make money?'"] --> B(Chat Interface)
    B --> C(Amazon Bedrock Agent)
    C -- '1. Detects Intent: AAPL revenue model' --> D(Agent Prompts LLM)
    D -- '2. Agent Decides to Invoke Tool: CompanyProfileTool (Sends Input: {ticker: AAPL, queryType: revenueModel})' --> E(AWS Lambda Function: CompanyProfileTool)
    E -- '3. Lambda Invokes External Financial Data API (e.g., Yahoo Finance)' --> F[Data Source: External Financial Data API]
    F -- '4. API Returns Revenue Data (e.g., iPhone, Services revenue)' --> E
    E -- '5. Lambda Sends Raw Data Back' --> C
    C -- '6. Agent (LLM) Summarizes & Generates Response' --> G["Chatbot Response: 'Apple Inc. (AAPL) primarily generates revenue from iPhone sales, Mac, iPad, and services like the App Store, Apple Music, and iCloud.'"]
    G --> B
    B --> A
```

![](amz.png)


**Additional Explanation:**
* The **Agent (LLM)** will be intelligent enough to interpret "make money" as a request for the revenue model or business segments, and select the appropriate `CompanyProfileTool`.
* The `CompanyProfileTool` should be designed to fetch "revenue model" or "earnings segments" type of data.
