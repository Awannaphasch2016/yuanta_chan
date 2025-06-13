# Project Requirements Document (PRD): InHouse AI Chatbot Infrastructure for Brokerage Company

## Project Summary

This project aims to build a fully in-house, AWS-native AI chatbot infrastructure for a brokerage company. The chatbot will serve as a central interface that empowers employees and (eventually) clients to access powerful productivity-enhancing tools. In the initial phase, the primary end-users will be internal Investment Consultants (ICs) at the brokerage. These ICs will use the chatbot to quickly get investment insights, retrieve financial data (e.g. stock metrics, earnings), and perform internal ticket creation for support issues. The primary goal is to demonstrate a scalable, extensible, and secure solution entirely using AWS services, with a focus on simplicity for the first release and tangible improvements to ICs' daily workflows.

## Objectives

- Build a conversational interface that connects to various internal and external systems through natural language.
- Support multi-turn reasoning, data retrieval, and intelligent task execution using Amazon Agents for Bedrock (LLM-based agents).
- Skip unnecessary complexity (e.g., RAG, complex IAM integration, CI/CD pipelines, and monitoring) for the initial demo.
- Enable quick wins with measurable productivity boosts to justify long-term investment.
- Design for incremental extensibility, where future use cases (additional tools or data sources) can be added without reimplementation of the core system.
- Target initial adoption by internal Investment Consultants to validate the chatbot in real workflows and gather feedback before rolling out to broader employee or client groups.

## Architecture Principles

- All services must be AWS-native. Leverage AWS-managed services for ease of integration and scalability.
- Amazon Bedrock + Agents will handle orchestration, conversation flow, and reasoning (including basic memory of the conversation context).
- Business logic and integrations will be implemented via AWS Lambda functions (Bedrock agent tools) for each distinct capability.
- External APIs (e.g., Yahoo Finance for market data) will be accessed securely within Lambda tools (using API keys or SDKs as needed, never directly exposed to the end-user).
- No use of vector databases or Retrieval-Augmented Generation (RAG) for v1 – rely on direct API/tool calls for information.
- No complex IAM setup or user-specific roles required for the initial stage (simplified access for pilot users).
- No CI/CD or automated infrastructure provisioning needed in the first iteration (infrastructure can be set up manually for the prototype).

## Core AWS Services to Use

| Purpose | AWS Service |
|---------|-------------|
| LLM orchestration (agent & reasoning) | Amazon Bedrock (Agents) |
| Business logic execution (tools) | AWS Lambda |
| API endpoint exposure (if needed) | Amazon API Gateway (optional, for invoking Lambdas securely) |
| Data storage (if needed for state) | Amazon DynamoDB or simple in-memory/mock within Lambda (for demo, persistence is optional) |

## Functional Use Cases

### 1. Investment Insight Assistant

**User Query (Example):** "Is AAPL a good investment?"

**Expected Agent Action:** The agent recognizes the user is asking for an investment analysis of Apple (ticker: AAPL). It invokes an Investment Insight Lambda tool, passing the ticker ("AAPL") as input.

**Lambda Tool Behavior:** The Lambda fetches key financial metrics for AAPL (e.g. P/E ratio, EV/EBITDA, ROE, etc.) from Yahoo Finance and returns these metrics in a structured format.

**Agent Response:** Using the data, the Bedrock agent formulates a summary with rationale. It might say, for example, that AAPL has a certain P/E ratio compared to peers, a healthy ROE, etc., and provide a brief recommendation or insight based on these metrics and general market context. The response should be structured (e.g., bullet points or a short paragraph per metric) with an overall rationale that is easy for the IC to understand.

### 2. 📊 Financial Data Lookup

**User Query (Example):** "Show me the latest quarterly earnings of TSLA."

**Expected Agent Action:** The agent identifies that the user is asking for specific financial data (Tesla's latest quarterly earnings). It invokes a Financial Lookup Lambda tool with the ticker ("TSLA") and the query intent (latest earnings).

**Lambda Tool Behavior:** The Lambda calls Yahoo Finance (or a similar financial data source) to retrieve the most recent quarterly earnings data for TSLA. This might include figures like revenue, net income, earnings per share (EPS), and the quarter period (e.g., Q4 2024).

**Agent Response:** The agent receives the structured data and presents it to the user in a clear format. For example, it may respond with a bullet list or table: the quarter name, revenue, net income, and EPS. The agent does not just dump numbers – it may add a sentence like "Tesla's latest reported quarter (Q4 2024) had an EPS of X and revenue of Y, which was an increase from the previous quarter."

### 3. 🛠 Internal Ticket Routing

**User Query (Example):** "Create a ticket for a failed trade settlement."

**Expected Agent Action:** The agent interprets this as a request to create an internal support ticket regarding a failed trade settlement issue. It invokes a Ticket Creation Lambda tool with the ticket details parsed from the request (e.g., title or description of the issue).

**Lambda Tool Behavior:** The Lambda simulates creating a ticket in the internal system (for the demo, this is a mock and not actually connected to a live ticketing database). It might simply generate a new ticket ID and record the provided details (in memory or logs).

**Agent Response:** The agent confirms the ticket creation to the user. For example, it might say "Ticket #12345 has been created for the trade settlement issue." The response should include the ticket ID and any relevant next steps or confirmation message. (Since this is a demo, the ticket is not actually saved persistently, but the user should feel the action was completed.)

## Architectural Diagram (Textual)

```
User (Investment Consultant) 
 --> Amazon Bedrock Agent (LLM Orchestrator)
 --> [Calls Tools via AWS Lambda]:
     1. Lambda: Yahoo Finance data fetch (for insights and lookups)
     2. Lambda: Ticketing logic (for internal ticket creation)
 <-- [Agent composes answer using LLM reasoning and tool results]
 <-- Returns final conversational response to User
```

*(In the above flow, Amazon API Gateway can be an intermediary if direct Lambda invocation needs to be exposed, but in this design the Bedrock Agent likely calls Lambda functions directly as tools. The Agent uses the Lambdas to fetch external data (Yahoo Finance) or perform actions (create ticket) and then uses the LLM to generate a natural language answer.)*

## Security & Privacy Considerations

- **No customer PII in pilot:** The system will not handle sensitive client data in v1. All data used (stock prices, financial metrics, generic ticket info) is either public or non-sensitive internal info.
- **API Keys Protection:** API keys (e.g., for Yahoo Finance or any external API) used within Lambda must be stored securely (such as in AWS Secrets Manager or as encrypted environment variables). They should not be exposed in code or responses.
- **No IAM user-role integration for demo:** User access will be limited to the pilot ICs through out-of-band means. We will not integrate with the corporate IAM/SSO for this prototype. Instead, access can be controlled by sharing a secured URL or credentials manually with the approved internal users. This avoids IAM overhead during the demo phase.
- **Data privacy:** Any sensitive internal information (if needed for future use cases) would be mocked or omitted in this demo. The system should not expose confidential data. All interactions and logs should comply with internal security policies.
- **Ephemeral data handling:** For demo purposes, any data stored (e.g., created tickets, query logs) can be kept ephemeral (in-memory or short-lived) unless necessary for the conversation flow. This ensures no long-term storage of possibly sensitive info. (Persistent logging/monitoring can be added in later phases with proper security reviews.)

## 📈 Success Metrics

| Metric | Target (v1 Demo) |
|--------|------------------|
| Time saved per workflow | ≥ 30% reduction vs. manual process |
| Use case coverage | 3 major workflows (investment Q&A, data lookup, ticket creation) in v1 |
| Agent response correctness | ≥ 90% accuracy on test prompts (responses are factually and contextually correct) |
| Integration latency | < 2 seconds for tool calls (end-to-end response ideally within 3 seconds) |
| Internal adoption | ≥ 10 active IC users in pilot phase (showing engagement) |

*(The above metrics will help demonstrate the value of the solution. For example, if an IC usually takes 5 minutes to lookup and compile data for a client, the chatbot doing it in under 1 minute achieves the ≥30% time reduction. Similarly, correctness will be evaluated with sample queries, and adoption measured by pilot usage.)*

## Phases

### Phase 1: Foundation (Week 1–2)

- Set up the Amazon Bedrock Agent with basic conversation capabilities.
- Implement Lambda connectors to external data:
  - Yahoo Finance Lambda for stock data retrieval.
  - Ticketing Lambda to simulate internal ticket creation.
- Basic testing of Lambda tool invocation through the agent (ensure the agent can call the Lambdas and get responses).
- *(No front-end yet, using test console or simple interface to validate backend logic.)*

### Phase 2: Prototype Use Cases (Week 3–4)

- Develop end-to-end conversational workflows for the three core use cases:
  - Investment Insight query (stock analysis workflow).
  - Financial data lookup (earnings or other metrics workflow).
  - Internal ticket creation workflow.
- Integrate a simple user interface for the chatbot (could be a web UI or an internal chat tool like Slack/MS Teams integration) for the ICs to interact with the agent.
- Fine-tune prompts and agent instructions for each use case to ensure quality responses (e.g., prompt the agent to call the correct tool and format the answer clearly).
- Collect initial feedback from a small group of ICs during this prototype phase.

### Phase 3: Review & Iterate (Week 5)

- Gather internal feedback from pilot users (ICs) on usefulness, accuracy, and any pain points.
- Refine the workflows, adjust the Lambda outputs or prompt wording as needed based on feedback.
- Polish the overall conversational experience (e.g., more friendly tone, handle edge-case queries).
- Prepare a final demo presentation showcasing a few example interactions for leadership/stakeholders.
- Outline next steps for production-hardening (not implemented in v1, but planning for IAM, monitoring, etc., if proceeding).

## Deliverables

- A working Bedrock Agent configured with the specified tools (Lambdas for finance data and ticketing).
- 3 working conversational workflows (one for each use case), demonstrated via a chat interface. (The agent can handle the example queries and similar variants end-to-end.)
- Minimal infrastructure setup (manual or basic scripted deployment) with no RAG, no advanced IAM, no CI/CD, and no monitoring in this phase, focusing on core functionality.
- A demo script and presentation outlining the use cases, plus a brief report on success metrics (time savings observed, accuracy of answers in testing, etc.).
- Documentation for developers (or Cursor AI) with technical details on how each component is implemented, to facilitate further development.

## Lambda Tool Specifications (Use Case Implementation Details)

To fulfill the above use cases, three AWS Lambda functions will be created as Bedrock Agent tools. Each Lambda has a defined interface (input/output schema) and behavior:

### Lambda 1: Investment Insight Metrics Tool

**Purpose:** Fetch key financial metrics for a given stock ticker to aid in investment insight queries (Use Case 1).

**Invocation Name (for Agent):** e.g., `InvestmentMetricsTool` (the Bedrock agent can call this tool when it needs stock metrics).

**Input Schema:** JSON object with the following structure:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| ticker | string | Required. Stock symbol to analyze. | "AAPL" |

**Output Schema:** JSON object containing financial metrics and related data for the company. For example:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| ticker | string | Echo of the input ticker symbol. | "AAPL" |
| companyName | string (Optional) | Company name for the ticker. | "Apple Inc." |
| PE_ratio | number | Price-to-Earnings ratio (latest available). | 28.5 |
| EV_EBITDA | number | Enterprise Value / EBITDA ratio. | 21.3 |
| ROE | number | Return on Equity (as a decimal or %). | 0.15 (15%) |
| marketCap | number (Optional) | Market capitalization in USD. | 2500000000000 |
| timestamp | string | Timestamp of data retrieval (UTC). | "2025-06-13T07:30:00Z" |

**Example Input:**
```json
{ "ticker": "AAPL" }
```

**Example Output:**
```json
{
  "ticker": "AAPL",
  "companyName": "Apple Inc.",
  "PE_ratio": 28.5,
  "EV_EBITDA": 21.3,
  "ROE": 0.15,
  "marketCap": 2500000000000,
  "timestamp": "2025-06-13T07:30:00Z"
}
```

**Behavior:** Given a ticker, the Lambda will call an external financial data API (e.g., Yahoo Finance) to retrieve a set of fundamental metrics. It will then construct a JSON response with the key metrics needed for the insight analysis. The Lambda itself does not generate advice or textual analysis; it just provides data. The Bedrock agent will use these metrics combined with its prompt instructions to formulate an answer to the user.

The metrics chosen (P/E, EV/EBITDA, ROE, etc.) are indicative of company valuation, profitability, and efficiency, which the agent can then explain or use in reasoning.

If the ticker symbol is invalid or data is not found, the Lambda should handle this gracefully.

**Error Handling:** In case of an error (e.g., unknown ticker or API failure), the Lambda can return a JSON with an error field instead of the metrics. For example:
```json
{ "error": "DataNotFound", "message": "No data found for ticker symbol 'INVALID'." }
```

The agent should detect this and respond to the user with an apology or clarification request (this behavior can be configured in the agent's tool-handling logic).

**Example Workflow:** User asks about AAPL → Agent calls InvestmentMetricsTool with "AAPL" → Lambda returns above JSON → Agent's LLM summarizes: "Apple Inc. (AAPL) has a P/E of 28.5, which is relatively high, an EV/EBITDA of 21.3, indicating a robust valuation, and an ROE of 15%, showing strong profitability. These metrics suggest AAPL is performing well, though the high P/E means the stock is somewhat expensive relative to earnings." (The exact wording is generated by the LLM using the data.)

### Lambda 2: Financial Data Lookup Tool

**Purpose:** Retrieve specific financial data (such as earnings results) for a given stock ticker (Use Case 2).

**Invocation Name:** e.g., `FinancialDataTool`.

**Input Schema:** JSON object with the following fields. (This tool can be designed to handle various types of financial queries; for v1 we focus on quarterly earnings.)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| ticker | string | Required. Stock symbol to lookup. | "TSLA" |
| queryType | string | Required. Type of data requested (e.g., "latestEarnings"). For v1, we primarily use "latestEarnings". | "latestEarnings" |

*(In future, queryType could support other values like "priceHistory", "analystRating", etc., but those are out of scope for now.)*

**Output Schema:** JSON object containing the requested financial data. For the "latestEarnings" queryType, the output might look like:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| ticker | string | Echo of the input ticker. | "TSLA" |
| quarter | string | Period of the latest earnings (fiscal quarter and year). | "Q1 2025" |
| reportDate | string | Date of the earnings report (ISO 8601 date). | "2025-04-25" |
| revenue | number | Revenue of that quarter (in USD, or specified currency). | 18500000000 |
| netIncome | number | Net income for that quarter (in USD). | 2500000000 |
| EPS | number | Earnings per share for the quarter. | 2.15 |
| currency | string | Currency of the reported figures. | "USD" |
| yearAgoRevenue | number (Optional) | Revenue from the year-ago quarter (YOY comparison). | 17000000000 |
| yearAgoEPS | number (Optional) | EPS from the year-ago quarter. | 1.95 |

**Example Input:**
```json
{ "ticker": "TSLA", "queryType": "latestEarnings" }
```

**Example Output (partial):**
```json
{
  "ticker": "TSLA",
  "quarter": "Q1 2025",
  "reportDate": "2025-04-25",
  "revenue": 18500000000,
  "netIncome": 2500000000,
  "EPS": 2.15,
  "currency": "USD",
  "yearAgoRevenue": 17000000000,
  "yearAgoEPS": 1.95
}
```

**Behavior:** For queryType = "latestEarnings", the Lambda will retrieve the most recent quarterly earnings data for the given company. This likely involves calling an external API to get financial statements or earnings releases. The Lambda then formats the key figures into the JSON output.

The agent will use this data to answer the user. For example, it might convert the above output to a sentence: "Tesla's latest earnings (Q1 2025, reported April 25, 2025) show revenue of $18.5B and net income of $2.5B (EPS $2.15), up from $17.0B revenue and EPS $1.95 a year ago." The agent can present this as a short report.

**Error Handling:** If the data cannot be found (e.g., the ticker is valid but the particular data is unavailable or the API fails), the Lambda should return an error structure similar to Lambda 1, e.g.
```json
{ "error": "DataUnavailable", "message": "Could not retrieve earnings for TSLA at this time." }
```

The agent would then respond appropriately (e.g., "Sorry, I'm having trouble finding that information.").

This tool can be extended beyond earnings. For example, if a user asked for a stock's current price or other financial info, the same Lambda could handle it by checking queryType and calling the relevant API endpoint. For now, we focus on quarterly earnings as the primary example.

### Lambda 3: Internal Ticket Creation Tool

**Purpose:** Create or route an internal support ticket based on a user's request (Use Case 3).

**Invocation Name:** e.g., `TicketCreationTool`.

**Input Schema:** JSON object with details about the ticket to be created.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| title | string | Required. Short summary of the issue or request. | "Failed Trade Settlement" |
| description | string | Detailed description of the issue (if provided by user or agent). | "Trade ID 4567 failed to settle on 2025-06-12. Please investigate." |
| priority | string (Optional) | Priority level of the ticket ("Low", "Medium", "High"). Default could be "Medium". | "High" |
| requestedBy | string (Optional) | The user creating the ticket (could be inferred or a static value in demo). | "jane.doe" |

*(In a real integration, there might be fields like department, category, etc., but for the prototype we keep it minimal.)*

**Output Schema:** JSON object representing the created ticket (mocked). For example:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| ticketId | string | Unique identifier for the new ticket. | "TCK-1001" |
| title | string | Echo of the ticket title. | "Failed Trade Settlement" |
| status | string | Status of the new ticket (e.g., "OPEN"). | "OPEN" |
| createdAt | string | Timestamp when the ticket was created. | "2025-06-13T07:31:00Z" |
| priority | string | Priority of the ticket. | "High" |
| message | string | Confirmation message (if any). | "Ticket TCK-1001 created successfully." |

**Example Input:**
```json
{
  "title": "Failed Trade Settlement",
  "description": "Trade ID 4567 failed to settle on 2025-06-12. Please investigate.",
  "priority": "High",
  "requestedBy": "jane.doe"
}
```

**Example Output:**
```json
{
  "ticketId": "TCK-1001",
  "title": "Failed Trade Settlement",
  "status": "OPEN",
  "createdAt": "2025-06-13T07:31:00Z",
  "priority": "High",
  "message": "Ticket TCK-1001 created successfully."
}
```

**Behavior:** This Lambda simulates the creation of a ticket. It does not actually save to a database in the prototype – it will generate a fake ticketId (e.g., using a simple counter or random ID) and return the details. The main goal is to integrate the workflow, so the IC gets a confirmation.

The agent will call this tool when it detects the user wants to create a ticket. The title might be derived from the user's request. For example, if the user just says "Create a ticket for a failed trade settlement," the agent might use that phrase as the title and possibly prompt the user for more details (in v1, we might not do multi-turn for details, so the description could be left similar to the title or a generic message).

On success, the Lambda returns the ticket info. The Bedrock agent then formulates a confirmation message to the user, e.g., "I've created ticket TCK-1001 titled 'Failed Trade Settlement'. It's currently OPEN and has been marked High priority." The message field from the Lambda can be used or the agent can craft its own message using the returned data.

**Error Handling:** If required fields are missing or some internal error occurs, the Lambda can return an error object. For instance, if title was empty, it might return:
```json
{ "error": "ValidationError", "message": "Ticket title is required." }
```

The agent would then ask the user to provide the missing info. In the prototype, however, we assume the user's query provides enough detail to create a ticket.

**Data Storage:** For the prototype, no persistent storage is used. The ticket is not actually saved in a ticketing system. It is ephemeral – each request to create a ticket will produce a new ticket ID that isn't stored beyond the function execution. This is acceptable for the demo. (In a future iteration, this Lambda could write to a DynamoDB table or call a real ticketing system API to persist the ticket.)

## External API and Data Source Details

Implementing the above Lambdas requires integration with external data sources (for financial data) and handling of internal data (for tickets). Below are the details for each:

### Yahoo Finance API Integration (for Investment Insight & Financial Lookup)

For financial metrics and data (used in Lambda 1 and Lambda 2), the system will integrate with Yahoo Finance data. Since Yahoo Finance does not offer an official public API, we have a couple of options:

**Option 1: Yahoo Finance via RapidAPI.** Yahoo Finance data can be accessed through third-party APIs on RapidAPI. One popular choice is the Yahoo Finance API on RapidAPI, which provides numerous endpoints for stock data. We can use endpoints such as:
- Get Quote – to get real-time quote information for one or multiple symbols (this can provide current price, day's range, etc., and some fundamental data like PE ratio).
- Get Summary / Financials – to retrieve detailed financial summary data for a company (e.g., key statistics, financial ratios).
- Get Chart / History – for historical price data (if needed in future).

**Authentication:** RapidAPI requires an API Key. We would subscribe to the Yahoo Finance API on RapidAPI and obtain an X-RapidAPI-Key. In our Lambda, we must include this key in the request headers when calling the API. The key should be stored securely (e.g., in AWS Secrets Manager or as an encrypted env var) and the Lambda will read it at runtime.

**Endpoint example:** To fetch quote and basic financial info for a ticker, we might use an endpoint like:
```
GET https://yh-finance.p.rapidapi.com/market/v2/get-quotes?symbols=AAPL&region=US
```

with headers:
```
X-RapidAPI-Key: <your_api_key>
X-RapidAPI-Host: yh-finance.p.rapidapi.com
```

A successful response returns a JSON structure containing `quoteResponse -> result` array. For example, a snippet for AAPL might include:
```json
{
  "quoteResponse": {
    "result": [
      {
        "symbol": "AAPL",
        "shortName": "Apple Inc.",
        "regularMarketPrice": 150.12,
        "twoHundredDayAverage": 148.50,
        "marketCap": 2500000000000,
        "forwardPE": 28.5,
        "priceToBook": 34.1,
        "earningsTimestamp": 1682625600,
        "financialCurrency": "USD"
      }
    ],
    "error": null
  }
}
```

From this, our Lambda can extract fields like `forwardPE` (P/E ratio), `marketCap`, etc. For more advanced metrics (EV/EBITDA, ROE), we might need a different endpoint or to compute them from data.

Yahoo Finance has a "key statistics" endpoint (accessible via quoteSummary with modules like `defaultKeyStatistics`, `financialData`, etc.). For example:
```
GET https://query2.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=financialData,defaultKeyStatistics
```

This returns a detailed JSON with fields including `returnOnEquity` (ROE), `enterpriseToEbitda` (EV/EBITDA), etc., for AAPL. We can use such endpoints if we prefer not to use RapidAPI, but some may require a valid Yahoo user cookie or may be undocumented.

**Option 2: Python library (yfinance).** Alternatively, we could use the yfinance Python library inside the Lambda to fetch data. This library scrapes Yahoo Finance and can retrieve many of these metrics without needing an official API key. For example:
```python
import yfinance as yf
ticker = yf.Ticker("AAPL")
data = ticker.info
pe = data.get("forwardPE")
roe = data.get("returnOnEquity")
```

This approach is convenient (no API key required), but it relies on an unofficial method and may be slower or subject to HTML changes. For a quick prototype, yfinance might be acceptable if it fits in Lambda's package size limits. However, using RapidAPI's service could be more reliable in the long run.

**Chosen Approach for v1:** We will likely use RapidAPI's Yahoo Finance endpoints for structured data access, given the time constraints and reliability. Specifically, for Lambda 1 (Investment Insight), we can call get-quotes for basic financials and quoteSummary for advanced stats (using an HTTP client within the Lambda, e.g., Python requests). For Lambda 2 (Financial Lookup), Yahoo Finance provides an earnings history as part of quoteSummary (module `incomeStatementHistoryQuarterly` or an earnings calendar endpoint). We might fetch the latest quarter's income statement from there to get revenue and net income. Another approach is to use yfinance's `ticker.quarterly_financials` or `ticker.earnings` if using the library.

**Sample Response (Yahoo Finance Earnings):** For illustration, an earnings data response might look like:
```json
{
  "finance": {
    "result": {
      "incomeStatementHistoryQuarterly": {
        "incomeStatementHistory": [
          {
            "endDate": "2025-03-31",
            "totalRevenue": 18500000000,
            "netIncome": 2500000000,
            "researchDevelopment": 700000000,
            "incomeBeforeTax": 2800000000,
            "eps": 2.15
          }
        ]
      }
    }
  }
}
```

Our Lambda would parse this JSON to extract `totalRevenue`, `netIncome`, `eps` from the most recent quarter (`endDate` 2025-03-31, which corresponds to Q1 2025) and format the output as specified in the schema.

**Performance:** We should note that calling external APIs will add latency. We aim to keep each Lambda call under ~1 second. The Yahoo Finance API calls typically return in a few hundred milliseconds, which should be fine. We will also ensure to not make unnecessary calls (the agent should only call the Lambda when needed and perhaps batch requests if multiple data points are needed from the same API).

### Internal Ticketing System (Mock) Integration

For the ticketing use case, since this is a demo, we do not integrate with a real ticketing system (like JIRA or ServiceNow) in v1. Instead, the Lambda will emulate the ticket creation:
- It does not call any external API; it simply generates a response.
- We may implement a simple in-memory counter or random generator for ticketId. For example, the first call could return TCK-1000, next TCK-1001, etc. (The sequence or format can be arbitrary since it's just for show.)
- No data is persisted. If the same ticket tool Lambda is invoked again, it won't "remember" past tickets. This is acceptable for now because the demo likely won't query the ticket system (e.g., "what is the status of ticket X?") – that is out of scope.
- If we wanted to simulate persistence, we could have the Lambda store tickets in a temporary DynamoDB table or a global variable. However, this adds complexity and is not needed for the initial demo. We clarify to stakeholders that this is a stubbed integration.
- The Lambda will return a confirmation message and the ID. The format can mimic what a real system might return. For example, status "OPEN", createdAt timestamp, etc., to make it realistic.
- In future iterations, if this chatbot is to be productionized, we would plan integration with the actual internal ticketing system API. That would involve authentication (likely using an internal API key or IAM role), and the Lambda would perform a network call to create a ticket in that system, then return the real ticket ID. For now, these details are not needed.

## Agent Memory and Multi-Turn Reasoning

Amazon Bedrock Agents have the ability to retain conversational context, enabling multi-turn dialogues where the agent remembers what was said earlier in the conversation. We need to decide how to handle memory for our chatbot:

**Intra-session memory (Enabled by default):** By default, the Bedrock agent will keep track of the conversation within a single chat session. This means an Investment Consultant can ask a follow-up question without repeating all details, and the agent will use the previous prompt and its answer for context. For example:
- User: "Is AAPL a good investment?" → (Agent gives insight with metrics)
- User (follow-up): "How about compared to MSFT?" → Here, the agent, if memory is enabled, knows the context is investment comparison and can call the tools for MSFT and perhaps compare metrics to AAPL's from earlier.

This kind of multi-turn reasoning is crucial for a natural experience. We will enable memory for each session so that the agent's LLM has the conversation history.

**Cross-session memory (Not needed in v1):** Bedrock Agents also support retaining context across sessions by using a memory store and session identifiers. This would allow the agent to "remember" information a specific user asked in a previous chat (e.g., yesterday). For the first version, we do not enable long-term memory across sessions, because:
- It introduces complexity in storing and retrieving conversation logs.
- Our initial use cases don't require the agent to recall information beyond the current conversation. Each session is short and focused on a task.
- We also are not implementing user authentication, so we cannot reliably identify the same user across sessions to give them personalized memory.

**Memory Implementation:** Enabling memory in Bedrock is straightforward. We would configure the agent with `memoryEnabled: true` (if using a JSON/SDK config) and can specify a memory retention duration (default might be one session or we can set a few hours/days if needed). For multi-turn within a session, the Bedrock agent will automatically pass the conversation history to the model. We should monitor that the prompt size doesn't become too large; if it does, Bedrock might summarize the memory (it has a built-in summarization mechanism for long chats).

In practice, when using the Bedrock API, we will use a consistent sessionId for all messages from a given user's conversation thread to maintain context. If we wanted to force-clear context, we could start a new session or end the session via the API.

**Recommendation for v1:** Enable conversational memory for each session. This ensures the agent can handle follow-up questions like "tell me more about that" or context like "use the same data as before for a different stock." It will make the chatbot experience more fluid for ICs. We will not implement persistent memory beyond the session in this prototype. Once the user or agent ends the conversation (or after a timeout), the context resets.

**Potential Use Cases of Memory:**
- **Clarifications:** If the agent's answer is long or complex, the user might ask, "Can you clarify the P/E part?" The agent should understand this refers to the P/E ratio mentioned earlier.
- **Sequential Queries:** An IC might first ask for an insight on AAPL, then say "Now do one for GOOGL." The agent should carry over the context that "do one" refers to an investment insight analysis, and just switch the ticker to GOOGL.
- **Ticket context:** If a user says "create a ticket for issue X," and then "Actually, add that it's urgent," a memory-enabled agent could potentially update the ticket creation (though in v1 our ticket tool doesn't store state to update, but the agent could combine the info in one request if it hadn't created it yet).

**Memory Limitations:** We will caution that the memory within a session is limited by the model's context length. The agent can summarize if the history grows, but in our use cases, conversations are likely short. We will not store any memory beyond the session (no database of conversations in v1), which also helps with privacy (no long-term storage of conversation content).

## ⚙ Deployment & Access Considerations

In the first iteration, we aim to get a working prototype quickly without heavy infrastructure overhead. Below are assumptions and plans regarding deployment and user access:

**Environment:** All components (Bedrock agent, Lambdas, etc.) will run in the company's AWS environment (could be a dev/test account dedicated to this prototype). We will manually deploy the Lambdas and configure the Bedrock Agent via the AWS console or simple scripts. Infrastructure-as-Code is not required for v1, since the focus is on functionality. (For example, we do not need Terraform or CloudFormation templates right now. We can set up resources by hand or with minimal AWS CLI commands.)

**CI/CD:** No continuous integration or deployment pipeline will be set up for this demo. Any code changes can be deployed manually. This is acceptable given the limited scope and the internal audience. In future phases, if the project continues, we would implement proper CI/CD and dev/test/prod environments.

**Access Control:** We will make the prototype accessible to a small group of internal users (the pilot group of Investment Consultants). Because we are not using IAM integration, access will be controlled in a lightweight way. Options include:
- Deploying a simple web UI (e.g., a static website or a lightweight React app) that connects to the Bedrock agent. The URL for this UI can be shared only with the pilot users. We might protect it with a basic password or host it on an internal network/VPN that only ICs can reach.
- Alternatively, integrate the bot into an internal chat platform (like Slack) in a workspace/channel where only the pilot users are invited.
- Manual distribution of credentials or tokens if needed (for example, if using API Gateway with an API key, give the key to the pilot users).

Since this is not public, we trust the limited distribution. However, we will still ensure the API keys (for Yahoo etc.) cannot be abused beyond this app.

**Scalability:** With only ~10 pilot users and no heavy compute tasks, a basic deployment is fine. Each Lambda can scale to handle the small number of requests. Bedrock service can handle the concurrent conversations easily given the low user count.

**Monitoring & Logging:** While we are not setting up a full monitoring stack (CloudWatch alarms, etc.), we will still have basic logging in place:
- Lambda CloudWatch Logs will record each invocation (useful for debugging tool outputs).
- Bedrock Agent might provide some logs or we can wrap the agent calls to log prompts and responses for analysis of accuracy.
- No automated alerting is set up; the development team will manually check logs during the pilot.

**Cost Considerations:** This prototype should be low-cost:
- Bedrock usage (LLM calls) and Lambda invocations are the primary cost. With few users and short conversations, it should stay in a manageable range.
- The Yahoo Finance API via RapidAPI might have limited free tier calls (e.g., 500/month on the free plan). We will monitor usage to avoid hitting limits. If needed, we can upgrade the plan or use multiple accounts for testing. Alternatively, the yfinance library approach has no direct cost, just compute time.
- No EC2 servers or long-running infrastructure in this design (everything is serverless or managed).

**Deployment Timeline:** By end of Week 2 (Phase 1), we plan to have the basic setup in AWS. Pilot users would get access in Phase 2 once we have the UI/interface ready. During Phase 3, any redeployments (to update logic) will be done in off-hours or quickly as it's a small user base.

## Additional Notes

**Extensibility:** The PRD is written with future growth in mind. After this initial prototype for ICs, the same infrastructure could be extended to other roles or even clients, with added security (e.g., IAM Cognito integration) and more tools (for example, a tool to retrieve research reports, or a tool to execute trades). The v1 design ensures adding new Lambdas for new use cases is straightforward.

**Testing:** Before giving access to ICs, we will test the agent with a set of predefined questions to ensure it calls the right tools and the outputs make sense. We'll refine prompts so that, for instance, when the user asks for an investment insight, the agent definitely triggers the InvestmentMetricsTool.

**Agent Prompting:** Part of the implementation involves crafting the agent's system prompt or tool instruction so it knows when to use each tool. We will configure the Bedrock Agent with a prompt along the lines of: "You are an internal assistant. You have tools: 'InvestmentMetricsTool' for stock metrics, 'FinancialDataTool' for financial statements, 'TicketCreationTool' for creating support tickets. Use them when appropriate. Provide clear, concise answers." This ensures the agent utilizes the Lambdas correctly.

**Fallback:** If the agent is asked something outside our 3 use cases (which is possible, since once ICs have a chatbot they might try other questions), we will have it respond with a polite deferral. For example, if asked about something it cannot do (like detailed trade execution), it should say "I'm sorry, I cannot assist with that request." This can be handled in the agent's prompt or by not providing tools for those tasks.

**Demo Success Criteria:** A successful demo will show an IC asking each type of question and the chatbot responding correctly and quickly. We will gather informal feedback – e.g., did it actually save them time finding info? – to include in the success report.

## References

1. [How To Use the Yahoo Finance API (in 2021) [Tutorial] | RapidAPI](https://rapidapi.com/blog/blog/how-to-use-the-yahoo-finance-api/)
2. [Yahoo Finance API URL : r/sheets](https://www.reddit.com/r/sheets/comments/ji52uk/yahoo_finance_api_url/)
3. [Retain conversational context across multiple sessions using memory - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-memory.html)