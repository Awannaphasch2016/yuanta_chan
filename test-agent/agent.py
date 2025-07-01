import boto3
import argparse
import sys

def invoke_agent(client, agent_id, alias_id, session_id, input_text):
    """Invoke the Bedrock agent and return the response"""
    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=session_id,
            inputText=input_text,
        )
        
        result = ""
        for event in response['completion']:
            if 'chunk' in event:
                payload = event['chunk']['bytes']
                chunk_text = payload.decode('utf-8')
                result += chunk_text
                print(chunk_text, end='', flush=True)
        
        print()  # New line after response
        return result
        
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return None

def interactive_chat(client, agent_id, alias_id, session_id):
    """Run an interactive chat session"""
    print(f"🤖 Starting interactive chat with Bedrock agent (Session: {session_id})")
    print("💡 Type 'quit', 'exit', or press Ctrl+C to end the conversation")
    print("=" * 60)
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("\n👤 You: ").strip()
            except EOFError:
                # Handle Ctrl+D
                break
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Send to agent and display response
            print("🤖 Agent: ", end='')
            invoke_agent(client, agent_id, alias_id, session_id, user_input)
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n👋 Chat ended. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

def single_message(client, agent_id, alias_id, session_id, input_text):
    """Send a single message (original functionality)"""
    print("🤖 Agent response:")
    invoke_agent(client, agent_id, alias_id, session_id, input_text)

def main():
    parser = argparse.ArgumentParser(description='Interact with Bedrock agent')
    parser.add_argument('--input', '-i', type=str,
                       help='Input text to send to the agent (if not provided, starts interactive chat)')
    parser.add_argument('--session', '-s', type=str, default='internquan',
                       help='Session ID for the agent (default: internquan)')
    parser.add_argument('--interactive', '-c', action='store_true',
                       help='Force interactive chat mode')
    
    args = parser.parse_args()

    try:
        client = boto3.client('bedrock-agent-runtime', region_name='ap-southeast-1')
    except Exception as e:
        print(f"❌ Failed to create Bedrock client: {e}")
        sys.exit(1)

    agent_id = '52MGYIUNTN'
    alias_id = 'XJUR3G7LY5'

    # Decide whether to run interactive chat or single message
    if args.input and not args.interactive:
        # Single message mode (original behavior)
        single_message(client, agent_id, alias_id, args.session, args.input)
    else:
        # Interactive chat mode
        interactive_chat(client, agent_id, alias_id, args.session)

if __name__ == '__main__':
    main()