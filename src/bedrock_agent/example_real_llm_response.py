"""
Example: Simulate a real LLM response to 'how does APPLE make money?'
"""
import sys
import os

# Ensure src is in the path for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.bedrock_agent.bedrock_adapter import BedrockAgentAdapter

# Simulate a client query
query = "how does APPLE make money?"

# In a real LLM scenario, the agent would map this to a tool call:
event = {
    "actionGroup": "InvestmentTools",
    "function": "analyze_investment",
    "parameters": {
        "ticker": "AAPL",
        "depth": "detailed"
    }
}

adapter = BedrockAgentAdapter()
response = adapter.handle_agent_request(event)

# Extract the LLM-style response
llm_response = response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"]

print("\n=== LLM Response to: 'how does APPLE make money?' ===\n")
print(llm_response)
print("\n=== END OF RESPONSE ===\n") 