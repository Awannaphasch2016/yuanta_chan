# Project Requirements Document (PRD): InHouse AI Chatbot Infrastructure for Brokerage Company

## Project Summary

This project aims to build a fully in-house, AWS-native AI chatbot infrastructure for a brokerage company. The chatbot will serve as a central interface that empowers employees and (eventually) clients to access powerful productivity-enhancing tools. In the initial phase, the primary end-users will be internal Investment Consultants (ICs) at the brokerage. These ICs will use the chatbot to quickly get investment insights, retrieve financial data (e.g. stock metrics, earnings), and perform internal ticket creation for support issues. The primary goal is to demonstrate a scalable, extensible, and secure solution entirely using AWS services, with a focus on simplicity for the first release and tangible improvements to ICs' daily workflows.

## Objectives

- Build a conversational interface that connects to various internal and external systems through natural language.
- Support multi-turn reasoning, data retrieval, and intelligent task execution using Amazon Agents for Bedrock (LLM-based agents).
- Skip unnecessary complexity (e.g., RAG, complex IAM integration, CI/CD pipelines, and monitoring) for the initial demo.
- Enable quick wins with measurable productivity boosts to justify long-term investment.
- Design for incremental extensibility, where future use cases (additional tools or data sources) can be added without reimplementation of the core system.
- Target initial adoption by internal Investment Consultants to validate the chatbot in real workflows and gather feedback before rolling out to broader employee or client groups (as a client of brokerage company).

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

### 1. Portfolio News & Client Engagement

**User Story** "As a client or IC, I want to know which news affects a portfolio, so the assistant can fetch and explain relevant headlines tied to holdings with actionable summaries."

**User Query (Example - Client):** "What are the top news items affecting my portfolio?"

**Expected Agent Action:** The agent identifies the client's portfolio holdings and retrieves recent market news and price updates relevant to those securities.

**Lambda Tool Behavior:** A News-and-Data tool calls external APIs (such as the Yahoo Finance news API) to gather recent headlines and current price data for each stock in the portfolio. It fetches news articles for each ticker and broad market news (e.g. Fed announcements, major economic events). The tool returns structured data: relevant news articles (with title, summary, source, and associated tickers) and latest price quotes for each holding.

**Agent Response:** The agent summarizes key news items and explains their relevance to the portfolio holdings, including citations for the information. For example, it might respond: "According to Reuters, U.S. markets rallied after the Fed kept interest rates unchanged¹, benefiting broad market sectors. This likely boosted your technology and financial stocks. In contrast, oil prices jumped about 7% amid Middle East tensions², which would have increased the value of energy holdings. Also, Tesla (TSLA) rebounded ~4% after a 14% drop tied to a public dispute³, indicating volatility for that position. Overall, your portfolio saw mixed impacts: tech/finance gains from the Fed news, and higher energy prices from geopolitical events. Would you like more details on any of these?" The assistant should present such insights as bullet points or short paragraphs, clearly linking each news item to specific holdings and citing credible sources.

**User Query (Example - IC):** "Summarize the top news for client Alice's portfolio."

**Expected Agent Action:** The agent retrieves Alice's portfolio holdings (simulated or provided in session memory) and fetches relevant news as described above.

**Agent Response:** The assistant produces a concise briefing for the IC. It might respond with bullet points like:
- "Fed holds rates steady; U.S. stocks rally +~1% (likely good for tech/financial holdings)."
- "Oil futures +7% on Middle East conflict (energy holdings likely up)."
- "Tesla (TSLA): down 14% then +4% recovery¹; note impact on TSLA."

The response should highlight news impacts for each relevant holding.

**Additional User Intents (Examples):**
- "Are there any major news headlines affecting my holdings today?"
- "Show recent news about [Ticker]."
- "What should I tell my client about recent market events?"
- "List significant news for my portfolio companies."

**Assistant Example Responses:** The assistant should clearly connect news events to portfolio holdings. For instance:
- "According to Reuters, the Fed kept rates steady, causing markets to rally¹. This likely benefited your broad-market holdings (e.g., index ETFs, financial stocks)."
- "Oil futures jumped ~7% on Middle East conflict², so your energy sector stocks probably saw gains."
- "Tesla (TSLA) stock slid 14% due to a public spat but then rose ~4%³. Your TSLA position was volatile because of this news."

**News-to-Holdings Mapping Behavior:**
- The agent matches ticker symbols and company names in news headlines to the client's portfolio list. If a news article mentions a holding, that holding is flagged.
- Broad market news (e.g. Fed policy, inflation data, geopolitical events) is identified by key terms and applied to affected sectors or the whole portfolio.
- The agent notes which specific holdings are impacted by each news item. For example, Fed news may be linked to banks/brokers, while oil price news maps to energy stocks.

**Suggested Follow-Up Prompts:**
- "Would you like to adjust any positions in response to this news?"
- "Do you want more details on any specific news item?"
- "Shall I pull up price charts for these stocks?"
- "Would you like to schedule a portfolio review with this update?"

**Fallback and Empty States:**
- If no relevant news is found for the portfolio: "No major news affecting your portfolio was found."
- If the portfolio is empty or undefined: "Your portfolio appears to have no holdings. Please add a ticker or account to review."
- If the query is unsupported: "I'm sorry, I cannot assist with that request."

**System Behavior (Summarization & Citations):**
- The News-and-Data Lambda tool retrieves raw news articles and price data, which the Bedrock agent passes to the LLM for reasoning.
- The agent uses the LLM to condense the information into key bullet points or paragraphs. It focuses on linking each news event to the appropriate holdings.
- The assistant includes citations to the original news sources (as shown above) to attribute facts. For example, it will append after any factual claim about market movements.
- This logic ensures responses are concise, factual, and traceable to external information.

## Architectural Diagram (Textual)

```
User (Investment Consultant)
--> Amazon Bedrock Agent (LLM Orchestrator)
--> [Calls Tools via AWS Lambda]:
    1. Lambda: API news fetch e.g., Newsdata.io, Yahoo Finance News
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

## Success Metrics

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
- 1 working conversational workflows (one for each use case), demonstrated via a chat interface. *(The agent can handle the example queries and similar variants end-to-end.)*
- Minimal infrastructure setup (manual or basic scripted deployment) with no RAG, no advanced IAM, no CI/CD, and no monitoring in this phase, focusing on core functionality.
- A demo script and presentation outlining the use cases, plus a brief report on success metrics (time savings observed, accuracy of answers in testing, etc.).
- Documentation for developers (or Cursor AI) with technical details on how each component is implemented, to facilitate further development.

## Lambda Tool Specifications (Use Case Implementation Details)

To fulfill the above use cases, one AWS Lambda functions will be created as Bedrock Agent tools. Each Lambda has a defined interface (input/output schema) and behavior:

### Lambda 1: Portfolio News & Price Summary Tool

**Purpose:**  
Fetch recent news headlines and live price data for a list of portfolio tickers to inform users (clients or ICs) about events that may affect their holdings.

**Invocation Name (for Agent):**  
`PortfolioNewsTool` (invoked when agent needs to check news or updates tied to a portfolio)

---

**Input Schema:**  
JSON object with the following structure:

| Field        | Type     | Description                                  | Example               |
|--------------|----------|----------------------------------------------|-----------------------|
| tickers      | string[] | List of stock symbols in the portfolio       | ["AAPL", "TSLA", "XOM"] |
| timeframe    | string   | Optional. Time range for recent news         | "24h", "7d", "30d"    |

**Example Input:**
```json
{
  "tickers": ["AAPL", "TSLA", "XOM"],
  "timeframe": "48h"
}
```

---

**Output Schema:**  
JSON object containing arrays of news items and price data for each ticker:

```json
{
  "news": [
    {
      "title": "Fed Holds Rates Steady, Markets Rally",
      "summary": "The Federal Reserve left interest rates unchanged, boosting equities.",
      "source": "Reuters",
      "published_at": "2025-06-13T14:00:00Z",
      "tickers": ["AAPL", "JPM", "TSLA"]
    },
    {
      "title": "Oil Prices Spike Amid Middle East Conflict",
      "summary": "Crude futures surged 7% on geopolitical fears.",
      "source": "Bloomberg",
      "published_at": "2025-06-13T12:30:00Z",
      "tickers": ["XOM", "CVX"]
    }
  ],
  "prices": [
    {
      "ticker": "AAPL",
      "price": 196.33,
      "change_percent": 1.27,
      "timestamp": "2025-06-13T15:00:00Z"
    },
    {
      "ticker": "TSLA",
      "price": 192.01,
      "change_percent": 4.23,
      "timestamp": "2025-06-13T15:00:00Z"
    }
  ]
}
```

---

**Behavior:**
- Retrieves headlines from financial news APIs (e.g., Yahoo Finance, Benzinga, or NewsAPI) that mention any of the provided tickers.
- Filters results by timeframe if specified (e.g., within the last 24–48 hours).
- De-duplicates and ranks articles based on recency, sentiment, and ticker relevance.
- Optionally retrieves latest price and % change for each holding from a price quote API.
- Returns both news and quote data in a structured JSON format.

---

**Error Handling:**
If no news or price data is found, returns empty arrays with a message field:

```json
{
  "news": [],
  "prices": [],
  "message": "No recent news found for the provided tickers."
}
```

---

**Example Workflow:**
User says: *"What’s affecting my portfolio today?"*  
→ Agent retrieves user's portfolio: `["AAPL", "TSLA", "XOM"]`  
→ Agent calls `PortfolioNewsTool` with those tickers  
→ Lambda returns news and price change data  
→ Agent summarizes impacts for each holding in clear, cited bullets


## External API and Data Source Details

Implementing the above Lambdas requires integration with external data sources (for financial data) and handling of internal data (for tickets). Below are the details for each:

### News Data API Integration (for Lambda 4: Portfolio News Tool)

For delivering news insights related to a client's portfolio holdings, we will integrate with one or both of the following:

**Option 1: Newsdata.io API (https://newsdata.io/blog/financial-news-api/)**

Newsdata.io offers financial news data, including filtering by topic, source, region, and keywords. Example query:

```
GET https://newsdata.io/api/1/news?apikey=<API_KEY>&q=Apple+Inc&language=en&category=business
```

**Fields Returned:**
- Title
- Link
- Description/Content
- Source
- Publication Date

Newsdata.io supports portfolio-relevant searches by company name or ticker keyword.

**Option 2: Yahoo Finance News Tool via LangChain**

LangChain has an integration for Yahoo Finance news which can be used within agents and tools. It provides concise and company-targeted news using:
```python
from langchain.tools.yahoo_finance_news import YahooFinanceNewsTool
```

This tool can be used inside an agent chain and fetches latest news stories linked to a given stock ticker.

**Chosen Approach for v1:** Use Newsdata.io for broad news coverage and headline access (suitable for ICs), and optionally use Yahoo Finance News Tool (LangChain wrapper) for LLM-friendly integration.

**Authentication:** Newsdata.io requires an API key. This will be stored in AWS Secrets Manager or securely in Lambda environment variables.

These APIs will power the Lambda 4 response structure by providing recent and relevant headlines tied to each ticker in the user's portfolio.

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

1. How To Use the Yahoo Finance API (in 2021) [Tutorial] | RapidAPI
2. Yahoo Finance API URL : r/sheets (Reddit)
3. Retain conversational context across multiple sessions using memory - Amazon Bedrock (AWS Documentation)
4. Wall Street rallies after Fed keeps rates unchanged | Reuters  
   https://www.reuters.com/markets/us/futures-edge-higher-investors-await-fed-decision-2025-03-19/
5. Investors choose safe havens, oil over equities as Middle East erupts | Reuters  
   https://www.reuters.com/business/energy/global-markets-investors-pix-graphic-2025-06-13/
6. Tesla shares gain after $152 billion selloff, but Trump-Musk truce uncertain | Reuters  
   https://www.reuters.com/business/autos-transportation/tesla-shares-rise-politico-reports-musk-white-house-hold-call-2025-06-06/