### 3. Workflow Diagram: n8n (No-code option) (with example query)

**Example Query:** "Tell me about Amazon (AMZN)."

```mermaid
graph TD
    A["User: 'Tell me about Amazon (AMZN)'"] --> B(Chat Interface)
    B --> C(n8n Workflow)
    C -- "1.Webhook Trigger (Receives message)" --> D["Text Processing Node / Regex: Extracts 'Amazon', 'AMZN'"]
    D -- "2.Sends 'Amazon' (or 'AMZN') to" --> E["HTTP Request Node: Invokes External Company Info API"]
    E -- "3.API Returns Amazon's Overview Data" --> E
    E -- "4.Sends Data to" --> F["Set Node / Function Node: Formats Response"]
    F -- "5.Sends Formatted Message to" --> G["Chatbot Integration Node: e.g., Slack, Custom Webhook"]
    G --> B
    B --> A
```
![](n88n.png)

**Additional Explanation:**
* A **Text Processing Node** in n8n (possibly using Regular Expressions or simple logic) would extract the company name/ticker from the user's message.
* The **HTTP Request Node** would be configured to call an API that provides company overview information.
* A **Set Node / Function Node** would then take the API's response and format it into a human-readable answer.
